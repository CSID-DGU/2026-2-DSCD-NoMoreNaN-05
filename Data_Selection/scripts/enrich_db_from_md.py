"""Enrich the explicitly supplied DB in place, after a read-only plan.

Approved exceptions: insert new reports; retain historical reports; fill only
the three previously empty safety/storage cells. Never overwrite nonempty data.
"""
import argparse
from collections import Counter,defaultdict
from contextlib import closing
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.inspect_md_enrichment_sources import BASE,OUT,locate
from src.md_db_enrichment import EnrichmentSources,HEALTH_FIELDS,ADDED_FIELDS,ARRAY_FIELDS,number,material_key
from src.claim_evidence_experiment import name_key


def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def compact(value):return re.sub(r'\s+','',str(value or ''))


def table_hash(db,table):
    digest=hashlib.sha256();count=0
    for row in db.execute('SELECT * FROM "'+table+'" ORDER BY rowid'):
        digest.update(json.dumps(tuple(row),ensure_ascii=False,separators=(',',':')).encode('utf-8'))
        digest.update(b'\n');count+=1
    return dict(rows=count,sha256=digest.hexdigest())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    paths=locate();sources=EnrichmentSources(paths)
    database=BASE/'claim_verification.sqlite'
    if database.resolve().parent!=BASE.resolve():raise ValueError('Unexpected target DB')
    hashes={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()}
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        original_columns=[r['name'] for r in db.execute('pragma table_info(products)')]
        if set(ADDED_FIELDS)&set(original_columns):raise ValueError('DB already contains enrichment columns; do not overwrite')
        old={r['manufacturing_report_number']:dict(r) for r in db.execute('SELECT * FROM products')}
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name!='products'")]
        unchanged_tables={t:table_hash(db,t) for t in tables}
        ingredients=[dict(r) for r in db.execute('SELECT * FROM ingredients')]
    added=sorted(set(sources.health)-set(old));historical=sorted(set(old)-set(sources.health))
    comparisons={k:dict(different_nonblank=0,db_blank_source_present=0,examples=[]) for k in HEALTH_FIELDS.values() if k!='manufacturing_report_number'}
    fills=[]
    for report in sorted(set(old)&set(sources.health)):
        before=old[report];health=sources.health[report]
        for field,column in HEALTH_FIELDS.items():
            if column=='manufacturing_report_number':continue
            a,b=before[column],health[field]
            if not compact(a) and compact(b):
                comparisons[column]['db_blank_source_present']+=1
                if column not in {'intake_precautions','storage_and_distribution_standard'}:
                    raise ValueError('Unapproved empty-cell fill required in '+column)
                fills.append(dict(product_id=before['product_id'],report=report,column=column,before=a,after=b))
            elif compact(a) and compact(b) and compact(a)!=compact(b):
                entry=comparisons[column];entry['different_nonblank']+=1
                if len(entry['examples'])<3:entry['examples'].append(dict(report=report,DB=a,CSV=b))
    if len(added)!=681 or len(historical)!=728 or len(fills)!=3:
        raise ValueError(f'Unexpected approved scope: added={len(added)} historical={len(historical)} fills={len(fills)}')
    save('existing_field_comparison.json',comparisons)
    save('approved_empty_cell_fills.json',fills)
    save('blocked_materials.json',sources.blocked)
    save('material_source_precedence.json',sources.precedence_notes)
    ingredient_comparisons=[];ingredient_status=Counter()
    for ingredient in ingredients:
        code=number(ingredient.get('recognition_number'))
        standard=sources.standard_number.get(code) if code else sources.standard_name.get(material_key(ingredient['ingredient_name'],True))
        status='blocked' if code in sources.blocked else 'linked' if standard else 'not_linked'
        ingredient_status[status]+=1
        if not standard:continue
        fields={}
        for db_col,std_col in [('functionality_text','PRIMARY_FNCLTY'),('intake_precautions','IFTKN_ATNT_MATR_CN'),('daily_intake_min','DAY_INTK_LOWLIMIT'),('daily_intake_max','DAY_INTK_HIGHLIMIT')]:
            a,b=ingredient.get(db_col),standard[std_col]
            rule='equal' if compact(a)==compact(b) else 'missing_side' if not compact(a) or not compact(b) else 'contained_text' if compact(a) in compact(b) or compact(b) in compact(a) else 'different_representation_or_content'
            fields[db_col]=dict(DB=a,source=b,comparison=rule)
        ingredient_comparisons.append(dict(ingredient_id=ingredient['ingredient_id'],recognition_number=code,name=ingredient['ingredient_name'],fields=fields))
    save('existing_ingredients_comparison.json',dict(status_counts=dict(ingredient_status),comparisons=ingredient_comparisons,
        note='Read-only comparison by exact recognition number/name. Numeric/unit formats may differ; no existing ingredients values changed.'))
    plan=dict(database=str(database),source_db_sha256=hashlib.sha256(database.read_bytes()).hexdigest(),
        original_count=len(old),added_reports=added,historical_retained_reports=historical,fill_count=len(fills),
        added_columns=ADDED_FIELDS,blocked_material_count=len(sources.blocked),ingredients_compared_not_modified=True,
        source_csv_sha256=hashes,status='planned')
    save('enrichment_plan.json',plan)
    print(json.dumps({k:v for k,v in plan.items() if k not in {'added_reports','historical_retained_reports','source_csv_sha256'}},ensure_ascii=False,indent=2),flush=True)
    if not args.apply:return
    coverage=Counter();samples=[];started=datetime.now(timezone.utc).isoformat()
    allowed_fills={(v['product_id'],v['column']):v['after'] for v in fills}
    with closing(sqlite3.connect(database)) as db:
        db.row_factory=sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            for field in ADDED_FIELDS:db.execute('ALTER TABLE products ADD COLUMN "'+field+'" TEXT')
            insert_cols=list(HEALTH_FIELDS.values())+['product_name_normalized']
            for report in added:
                raw=sources.health[report];values={column:raw[field] for field,column in HEALTH_FIELDS.items()}
                values['product_name_normalized']=name_key(raw['PRDUCT'])
                db.execute('INSERT INTO products ('+','.join(insert_cols)+') VALUES ('+','.join('?' for _ in insert_cols)+')',[values[k] for k in insert_cols])
            for fill in fills:db.execute('UPDATE products SET '+fill['column']+'=? WHERE product_id=?',(fill['after'],fill['product_id']))
            products=[(r['product_id'],r['manufacturing_report_number']) for r in db.execute('SELECT product_id,manufacturing_report_number FROM products ORDER BY product_id')]
            query='UPDATE products SET '+','.join('"'+k+'"=?' for k in ADDED_FIELDS)+' WHERE product_id=?'
            batch=[]
            linked_products=[(pid,report) for pid,report in products if report in sources.items]
            sample_ids={pid for pid,report in linked_products if pid in {6411,29940,products[-1][0]}}
            for pid,report in linked_products:
                if len(sample_ids)>=5:break
                sample_ids.add(pid)
            for index,(pid,report) in enumerate(products,1):
                values=sources.product_fields(report)
                for key,value in values.items():
                    if value is not None and value!='' and value!=[]:coverage[key]+=1
                serialized=[json.dumps(values[k],ensure_ascii=False,separators=(',',':')) if k in ARRAY_FIELDS and values[k] else None if k in ARRAY_FIELDS else values[k] for k in ADDED_FIELDS]
                batch.append(serialized+[pid])
                if pid in sample_ids:samples.append(dict(product_id=pid,report=report,source_item=sources.items.get(report),expected_fields=values))
                if len(batch)>=100:db.executemany(query,batch);batch=[]
                if index%10000==0:print('Enriched products',index,len(products),flush=True)
            if batch:db.executemany(query,batch)
            assert len(products)==len(old)+681
            assert db.execute('select count(*)-count(distinct manufacturing_report_number) from products').fetchone()[0]==0
            for before in old.values():
                after=db.execute('SELECT '+','.join(original_columns)+' FROM products WHERE product_id=?',(before['product_id'],)).fetchone()
                for column in original_columns:
                    assert after[column]==allowed_fills.get((before['product_id'],column),before[column]),(before['product_id'],column)
            for table,fingerprint in unchanged_tables.items():assert table_hash(db,table)==fingerprint,table
            json_count=0
            for row in db.execute('SELECT '+','.join(ARRAY_FIELDS)+' FROM products'):
                for field in ARRAY_FIELDS:
                    if row[field] is not None:
                        assert isinstance(json.loads(row[field]),list)
                        json_count+=1
            for sample in samples:
                actual=db.execute('select * from products where product_id=?',(sample['product_id'],)).fetchone()
                assert sample['source_item']['PRDLST_REPORT_NO']==sample['report']
                for k,v in sample['expected_fields'].items():
                    stored=json.loads(actual[k]) if k in ARRAY_FIELDS and actual[k] else [] if k in ARRAY_FIELDS else actual[k]
                    assert stored==v,(sample['product_id'],k)
            assert len(samples)>=5
            for kind,path in paths.items():assert hashlib.sha256(path.read_bytes()).hexdigest()==hashes[kind],kind
            assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
            db.commit()
        except BaseException:
            db.rollback();raise
    save('source_sample_checks.json',samples)
    save('unlinked_materials.json',[dict(kind=kind,material=material,reason=reason,count=count) for (kind,material,reason),count in sources.missing.most_common()])
    summary=dict(status='complete',started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),database=str(database),
        original_product_count=len(old),added_product_count=681,product_count=len(products),historical_retained_count=728,
        filled_empty_cells=len(fills),columns_added=len(ADDED_FIELDS),original_values_preserved_except_approved_fills=True,
        other_tables_unchanged=unchanged_tables,source_csv_unchanged=True,json_cells_validated=json_count,
        sampled_products=len(samples),blocked_recognition_or_name_keys=len(sources.blocked),
        coverage={k:dict(count=coverage[k],percent=round(100*coverage[k]/len(products),2)) for k in ADDED_FIELDS},
        source_db_sha256_before=plan['source_db_sha256'],source_db_sha256_after=hashlib.sha256(database.read_bytes()).hexdigest(),
        no_database_copy_created=True)
    save('enrichment_summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
