"""Local, source-traceable patent candidate cache; not verified claim evidence."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'Data_List_Claim_Verification/kipris_evidence_cache.sqlite'
SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS searches(
 search_id TEXT PRIMARY KEY, query TEXT NOT NULL, endpoint TEXT NOT NULL,
 conditions_json TEXT NOT NULL, collected_at TEXT, status TEXT NOT NULL,
 total_results INTEGER, pages_collected INTEGER, records_observed INTEGER);
CREATE TABLE IF NOT EXISTS patents(
 application_number TEXT PRIMARY KEY, title TEXT NOT NULL, abstract TEXT,
 applicant TEXT, application_date TEXT, registration_number TEXT,
 registration_status TEXT, ipc TEXT, fields_json TEXT NOT NULL,
 evidence_role TEXT NOT NULL DEFAULT 'PATENT_CANDIDATE');
CREATE TABLE IF NOT EXISTS source_pages(
 search_id TEXT REFERENCES searches(search_id), page INTEGER,
 xml_path TEXT NOT NULL, sha256 TEXT NOT NULL, record_count INTEGER,
 PRIMARY KEY(search_id,page));
CREATE TABLE IF NOT EXISTS search_patents(
 search_id TEXT, application_number TEXT REFERENCES patents(application_number),
 page INTEGER, PRIMARY KEY(search_id,application_number),
 FOREIGN KEY(search_id,page) REFERENCES source_pages(search_id,page));
CREATE VIRTUAL TABLE IF NOT EXISTS patent_search USING fts5(application_number UNINDEXED,title,abstract,tokenize='trigram');
CREATE VIEW IF NOT EXISTS patent_evidence_candidates AS
 SELECT p.*,s.query,s.collected_at,s.status AS collection_status,r.xml_path,r.sha256
 FROM patents p JOIN search_patents l USING(application_number)
 JOIN searches s USING(search_id) JOIN source_pages r ON r.search_id=l.search_id AND r.page=l.page;
'''

def connect(db=DB):
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    return con

def import_directory(directory, db=DB):
    directory = Path(directory)
    meta = json.loads((directory/'metadata.json').read_text(encoding='utf-8'))
    conditions = {'word':meta['query'],'patent':True,'utility':True,'lastvalue':''}
    condition_json = json.dumps(conditions,ensure_ascii=False,sort_keys=True)
    sid = hashlib.sha256((meta['endpoint']+condition_json).encode()).hexdigest()
    pages = []
    identifiers = set()
    for page in meta['pages']:
        path = directory/page['file']
        body = path.read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        if digest != page['sha256']:
            raise ValueError('XML checksum mismatch: '+path.name)
        records = []
        for node in ET.fromstring(body).iter():
            if node.tag.rsplit('}',1)[-1].lower() != 'patentutilityinfo':
                continue
            fields = {x.tag.rsplit('}',1)[-1]:(x.text or '') for x in node}
            number = fields.get('ApplicationNumber','').strip()
            if not number or number in identifiers:
                raise ValueError('Missing or duplicate application number')
            identifiers.add(number)
            records.append(fields)
        if len(records) != page['records']:
            raise ValueError('Page record count mismatch')
        pages.append((page['page'],path.relative_to(ROOT).as_posix(),digest,records))
    if len(identifiers) != meta['records_observed']:
        raise ValueError('Observed total mismatch')
    if meta['status']=='complete' and len(identifiers)!=meta['total_results']:
        raise ValueError('Complete collection total mismatch')
    with closing(connect(db)) as con, con:
        con.execute('INSERT OR REPLACE INTO searches VALUES(?,?,?,?,?,?,?,?,?)',
                    (sid,meta['query'],meta['endpoint'],condition_json,meta['collected_at'],meta['status'],meta['total_results'],len(pages),len(identifiers)))
        con.execute('DELETE FROM search_patents WHERE search_id=?',(sid,))
        con.execute('DELETE FROM source_pages WHERE search_id=?',(sid,))
        for page,path,digest,records in pages:
            con.execute('INSERT INTO source_pages VALUES(?,?,?,?,?)',(sid,page,path,digest,len(records)))
            for f in records:
                number=f['ApplicationNumber'].strip()
                con.execute('INSERT OR REPLACE INTO patents VALUES(?,?,?,?,?,?,?,?,?,?)',
                  (number,f.get('InventionName',''),f.get('Abstract',''),f.get('Applicant',''),f.get('ApplicationDate',''),f.get('RegistrationNumber',''),f.get('RegistrationStatus',''),f.get('InternationalpatentclassificationNumber',''),json.dumps(f,ensure_ascii=False),'PATENT_CANDIDATE'))
                con.execute('DELETE FROM patent_search WHERE application_number=?',(number,))
                con.execute('INSERT INTO patent_search VALUES(?,?,?)',(number,f.get('InventionName',''),f.get('Abstract','')))
                con.execute('INSERT INTO search_patents VALUES(?,?,?)',(sid,number,page))
    return len(identifiers)

def search_candidates(query, limit=10, db=DB):
    if not query.strip():
        raise ValueError('Search text is required')
    with closing(connect(db)) as con:
        con.row_factory=sqlite3.Row
        # Literal substring matching supports short Korean terms and does not
        # treat claim text as FTS syntax. Trigram index accelerates longer terms.
        literal=query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        rows=con.execute('''SELECT application_number,title,abstract,evidence_role,
          (SELECT xml_path FROM patent_evidence_candidates e WHERE e.application_number=p.application_number LIMIT 1) AS xml_path
          FROM patents p WHERE title LIKE ? ESCAPE '\\' OR abstract LIKE ? ESCAPE '\\'
          ORDER BY application_number LIMIT ?''',('%'+literal+'%','%'+literal+'%',limit)).fetchall()
        return [dict(row) for row in rows]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-dir',type=Path)
    parser.add_argument('--search')
    parser.add_argument('--limit',type=int,default=10)
    args=parser.parse_args()
    if args.import_dir:
        print('Imported:',import_directory(args.import_dir),'records; DB:',DB)
    elif args.search:
        print(json.dumps(search_candidates(args.search,args.limit),ensure_ascii=False,indent=2))
    else:
        for directory in sorted((ROOT/'data/raw/kipris').iterdir()):
            if (directory/'metadata.json').exists():
                print(directory.name,import_directory(directory),'records')
        print('DB:',DB)

if __name__=='__main__':
    main()
