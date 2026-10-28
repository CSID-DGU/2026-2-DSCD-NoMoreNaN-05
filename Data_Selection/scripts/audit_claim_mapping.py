"""Read-only coverage audit for a supplied claim extraction sample, not a verdict engine."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def rows(connection, statement, parameters=()):
    return [dict(row) for row in connection.execute(statement, parameters)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--claims', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/claim_mapping_audit.json')
    args = parser.parse_args()
    original = args.claims.read_bytes()
    text = original.decode('utf-8-sig').strip()
    repairs = []
    if text.startswith('"claims"'):
        text = '{'+text+'}'
        repairs.append('Wrapped top-level claims member in an object for audit parsing only')
    # The supplied illustrative JSON contains trailing commas after timestamps.
    # Do not modify quoted strings or the original input.
    pattern = r'"(?:\\.|[^"\\])*"|,(?=\s*[}\]])'
    repaired = re.sub(pattern, lambda m: '' if m.group().startswith(',') else m.group(), text)
    if repaired != text:
        repairs.append('Removed trailing commas outside quoted strings in audit copy only')
    claims = json.loads(repaired)['claims']
    report = {'created_at': datetime.now(timezone.utc).isoformat(),
              'input_sha256': hashlib.sha256(original).hexdigest(),
              'input_repairs': repairs, 'claim_count': len(claims),
              'method': 'Literal and whitespace-normalized SQL coverage checks only; no embeddings, LLM or verdicts',
              'claims': claims, 'databases': {}, 'product_matches': {},
              'ingredient_name_matches': {}, 'growth_evidence_candidates': [],
              'patent_keyword_candidates': {}}
    path = ROOT/'Data_List_Claim_Verification/claim_verification.sqlite'
    with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        report['databases']['claim_verification'] = {
            t: db.execute('SELECT count(*) FROM '+t).fetchone()[0]
            for t in ['products','ingredients','diseases','evidence','claims','claim_evidence_links']}
        report['evidence_type_counts'] = rows(db, 'SELECT evidence_type,count(*) AS count FROM evidence GROUP BY evidence_type')
        for target in sorted({c['target'] for c in claims if c.get('target')}):
            normalized = re.sub(r'[\s\-_,.()\[\]]+', '', target).casefold()
            report['product_matches'][target] = rows(db, '''SELECT product_id,product_name,company_name,manufacturing_report_number
                FROM products WHERE product_name_normalized=?''', (normalized,))
        for term in ['홍삼','초유','CBP','YGF','한속단','칼슘']:
            report['ingredient_name_matches'][term] = rows(db, '''SELECT ingredient_id,ingredient_name,
                recognition_number,functionality_text FROM ingredients WHERE ingredient_name LIKE ?''', ('%'+term+'%',))
        report['growth_evidence_candidates'] = rows(db, '''SELECT e.evidence_id,e.evidence_text,i.ingredient_id,
            i.ingredient_name,i.recognition_number FROM evidence e JOIN ingredients i USING(ingredient_id)
            WHERE e.evidence_type='OFFICIAL_FUNCTIONALITY'
            AND (replace(e.evidence_text,' ','') LIKE ? OR replace(e.evidence_text,' ','') LIKE ?)''', ('%키성장%','%성장판%'))
        report['red_ginseng_evidence'] = rows(db, '''SELECT e.*,i.ingredient_name,i.recognition_number
            FROM evidence e JOIN ingredients i USING(ingredient_id) WHERE i.ingredient_name=?''', ('홍삼',))
        report['calcium_product_context_only'] = rows(db, '''SELECT product_id,product_name,company_name,main_functionality
            FROM products WHERE main_functionality LIKE ? ORDER BY product_id LIMIT 3''', ('%[칼슘]%',))
        report['false_positive_example'] = rows(db, '''SELECT product_id,product_name FROM products
            WHERE product_name LIKE ? ORDER BY product_id LIMIT 2''', ('%초유%',))
    path = ROOT/'Data_List_Claim_Verification/kipris_evidence_cache.sqlite'
    with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        report['databases']['kipris'] = {'patents': db.execute('SELECT count(*) FROM patents').fetchone()[0]}
        for term in ['compound K','컴파운드','Rh2','성장판','카이스트']:
            parameters = ('%'+term+'%',)*2
            total = db.execute('SELECT count(*) FROM patents WHERE title LIKE ? OR abstract LIKE ?', parameters).fetchone()[0]
            candidates = rows(db, '''SELECT p.application_number,p.title,p.abstract,p.applicant,p.registration_status,
                (SELECT xml_path FROM patent_evidence_candidates e WHERE e.application_number=p.application_number LIMIT 1) AS xml_path
                FROM patents p WHERE p.title LIKE ? OR p.abstract LIKE ? ORDER BY p.application_number LIMIT 3''', parameters)
            report['patent_keyword_candidates'][term] = {'count': total, 'examples': candidates,
                'interpretation': 'Keyword candidates only; product use, certification, clinical efficacy and patent registration not established'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Audited {len(claims)} claims; read-only database checks; report: {args.output}')


if __name__ == '__main__':
    main()
