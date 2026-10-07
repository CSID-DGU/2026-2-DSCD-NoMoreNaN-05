"""Portable SQLite snapshots, PostgreSQL dump and KIPRIS source XML."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[1]

def main():
    load_dotenv(ROOT/'.env')
    if not os.getenv('PGPASSWORD'):
        raise RuntimeError('PGPASSWORD missing')
    name='truead_database_bundle_'+datetime.now().strftime('%Y%m%d_%H%M%S')
    directory=ROOT/'exports'/name
    directory.mkdir(parents=True)
    for filename in ['claim_verification.sqlite','kipris_evidence_cache.sqlite']:
        source=ROOT/'Data_List_Claim_Verification'/filename
        destination=directory/'Data_List_Claim_Verification'/filename
        destination.parent.mkdir(exist_ok=True)
        source_db=sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)
        target_db=sqlite3.connect(destination)
        try:
            source_db.backup(target_db)
            if target_db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('SQLite snapshot invalid')
        finally:
            target_db.close();source_db.close()
    dump=Path(r'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe')
    command=[str(dump),'--host',os.getenv('PGHOST','localhost'),'--port',os.getenv('PGPORT','5432'),
             '--username',os.getenv('PGUSER','postgres'),'--dbname',os.getenv('PGDATABASE','TrueAD_Evidence_Claim'),
             '--format=custom','--no-owner','--no-acl','--no-password','--file',str(directory/'truead.dump')]
    result=subprocess.run(command,capture_output=True)
    if result.returncode:raise RuntimeError('pg_dump failed; credentials and raw error withheld')
    for metadata in (ROOT/'data/raw/kipris').glob('*/metadata.json'):
        contents=json.loads(metadata.read_text(encoding='utf-8'))
        for page in contents.get('pages',[]):
            source=metadata.parent/page['file']
            if hashlib.sha256(source.read_bytes()).hexdigest()!=page['sha256']:raise RuntimeError('Source XML hash mismatch')
            target=directory/source.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        target=directory/metadata.relative_to(ROOT);shutil.copy2(metadata,target)
    readme='''# TRUEAD database restore

Unzip this archive at the project root; retain the relative folder structure.
SQLite snapshots: Data_List_Claim_Verification/*.sqlite
PostgreSQL custom-format backup: truead.dump
KIPRIS original XML: data/raw/kipris/
No passwords or API keys are included.

On the destination computer install PostgreSQL 18 and pgvector 0.8.7 (or compatible versions).
Create an EMPTY database named TrueAD_Evidence_Claim in pgAdmin.
Right-click that database > Restore > select truead.dump (Custom format) > Restore.
If restoring as a different user, enable No owner and No privileges under restore options.
Do not restore over an existing populated database.
Configure the project's .env with destination PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD.
Then run: python scripts/check_postgres.py
Compare restored tables with table_counts.json.
Keep data/raw/kipris relative to the project root so original XML references resolve.
'''
    (directory/'RESTORE.md').write_text(readme,encoding='utf-8')
    sys.path.insert(0,str(ROOT))
    from src.utils.postgres import connect_postgres
    with connect_postgres() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('claim_verification','kipris') ORDER BY 1,2")
            tables=cursor.fetchall();counts={}
            from psycopg import sql
            for schema,table in tables:
                cursor.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(schema,table)))
                counts[schema+'.'+table]=cursor.fetchone()[0]
    (directory/'table_counts.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
    manifest={p.relative_to(directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.rglob('*') if p.is_file()}
    (directory/'checksums.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    archive=directory.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in directory.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(directory).as_posix())
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise RuntimeError('Archive verification failed')
    print('Bundle:',archive,'bytes:',archive.stat().st_size)

if __name__=='__main__':main()
