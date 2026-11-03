"""Read-only inspection of the CSV inputs required by the enrichment guide."""
import csv
from collections import Counter,defaultdict
from contextlib import closing
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
_workspace_base=ROOT/'TRUEAD_DB_보강자료'
BASE=Path(os.environ['TRUEAD_ENRICHMENT_DIR']).expanduser() if os.environ.get('TRUEAD_ENRICHMENT_DIR') else (_workspace_base if _workspace_base.is_dir() else Path.home()/'Desktop'/'TRUEAD_DB_보강자료')
OUT=ROOT/'data/processed/md_enrichment_20261103'
FILES={'health':'mfds_health_functional_food_products_20261031.csv','items':'I0030.csv','business':'I2500.csv',
       'history':'I2860.csv','collagen':'mfds_eating_collagen_products_20261031.csv','standard':'I2710.csv',
       'approved':'I-0050.csv','class':'I0760.csv','dictionary':'mfds_food_raw_materials_20261031.csv','recall':'I0490.csv'}


def locate():
    files=list((BASE/'data_collection').rglob('*.csv'))
    found={}
    for kind,name in FILES.items():
        hits=[p for p in files if p.name==name]
        if len(hits)!=1:raise ValueError(f'Expected one {name}, found {len(hits)}')
        found[kind]=hits[0]
    return found


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    found=locate()
    info={}; relevant_licenses=set(); standard=[]; approved=[]
    for kind,path in found.items():
        with path.open(encoding='utf-8-sig',newline='') as stream:
            reader=csv.reader(stream);header=next(reader)
            counts=Counter(header);dups={k:[i for i,v in enumerate(header) if v==k] for k,n in counts.items() if n>1}
            duplicate_cell_conflicts=Counter();keys=Counter();n=0;business_values=defaultdict(set)
            for cells in reader:
                if len(cells)!=len(header):raise ValueError(f'Wrong CSV row width in {kind}, row {n+2}')
                row=dict(zip(header,cells));n+=1
                for field,positions in dups.items():
                    if len({cells[i] for i in positions})>1:duplicate_cell_conflicts[field]+=1
                key=row.get('STTEMNT_NO') if kind=='health' else row.get('PRDLST_REPORT_NO') if kind=='items' else None
                if key is not None:keys[key]+=1
                if kind=='items':relevant_licenses.add(row.get('LCNS_NO',''))
                if kind=='business' and row['LCNS_NO'] in relevant_licenses:
                    business_values[row['LCNS_NO']].add((row['ADDR'],row['PRMS_DT']))
                if kind=='collagen':business_values[row['LCNS_NO']].add(row['INSTT_NM'])
                if kind=='standard':standard.append(row)
                if kind=='approved':approved.append(row)
            info[kind]=dict(path=str(path),rows=n,bytes=path.stat().st_size,modified_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
                columns=header,duplicate_columns=dups,duplicate_cell_conflicts=dict(duplicate_cell_conflicts),
                duplicate_primary_keys={k:v for k,v in keys.items() if v>1},
                multi_value_licenses={k:sorted(v) for k,v in business_values.items() if len(v)>1})
        print(kind,n,'duplicate_cells',dict(duplicate_cell_conflicts),'multi_license',len(info[kind]['multi_value_licenses']),flush=True)
    def number(value):
        m=re.search(r'(\d{4})\s*-\s*(\d+)',value or '')
        return f'{m[1]}-{int(m[2])}' if m else ''
    grouped=defaultdict(list)
    for row in standard:grouped[number(row['PRDCT_NM'])].append(row)
    approved_groups=defaultdict(list)
    for row in approved:approved_groups[number(row['HF_FNCLTY_MTRAL_RCOGN_NO'])].append(row)
    report=dict(files=info,standard_without_number=len(grouped['']),
        duplicated_standard_numbers={k:[{f:r[f] for f in ('PRDCT_NM','DAY_INTK_LOWLIMIT','DAY_INTK_HIGHLIMIT','INTK_UNIT')} for r in v]
            for k,v in grouped.items() if k and len(v)>1},
        duplicated_approved_numbers={k:v for k,v in approved_groups.items() if k and len(v)>1})
    with closing(sqlite3.connect((BASE/'claim_verification.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as db:
        report['db_products']=db.execute('select count(*) from products').fetchone()[0]
        report['db_ingredients']=db.execute('select count(*) from ingredients').fetchone()[0]
    (OUT/'source_preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Standard rows without number:',report['standard_without_number'],flush=True)
    print('Duplicate standard numbers:',list(report['duplicated_standard_numbers']),flush=True)
    print('Duplicate approved numbers:',list(report['duplicated_approved_numbers']),flush=True)


if __name__=='__main__':main()
