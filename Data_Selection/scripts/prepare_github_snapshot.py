"""Create a credential-scrubbed, split workspace archive and publish code copy.

Local originals are never edited. Tokens/passwords are read only to detect and
redact them, and are never printed. Runtime environments/model downloads omitted.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
import urllib.parse
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SKIP_DIRS={'.git','.publish-repo','.venv','.tools','__pycache__','.pytest_cache','.agents','.codex','.aws'}
SKIP_NAMES={'.env','debug.log','run.lock','job.lock','stdin.empty'}
TEXT={'.py','.ps1','.json','.jsonl','.xml','.txt','.md','.csv','.yaml','.yml','.toml','.ini','.cfg','.sql','.log','.html','.gitignore','.gitattributes'}


def secret_variants():
    from dotenv import dotenv_values
    variants=set()
    for key,value in dotenv_values(ROOT/'.env').items():
        if value and re.search(r'KEY|PASSWORD|TOKEN|SECRET',key,re.I) and len(value)>=4:
            for candidate in {value,urllib.parse.quote(value,safe=''),urllib.parse.unquote(value),urllib.parse.quote_plus(value)}:
                variants.add(candidate.encode('utf-8'))
    return sorted(variants,key=len,reverse=True)


def scrub(data,secrets):
    for value in secrets:
        data=data.replace(value,b'[REDACTED]')
    # Persisted HTTP request URLs can contain credentials absent from today's env.
    data=re.sub(rb'(?i)([?&](?:amp;)?(?:servicekey|api_key|apikey|key|access_token|token|password)=)[^&\s"<>\\]+',rb'\1[REDACTED]',data)
    data=re.sub(rb'(?i)(authorization["\s:]+bearer\s+)[A-Za-z0-9._~+/=-]+',rb'\1[REDACTED]',data)
    data=re.sub(rb'AIza[0-9A-Za-z_-]{35}',b'[REDACTED]',data)
    data=re.sub(rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}',b'[REDACTED]',data)
    return data


def clean_zip(data,secrets):
    changed=False
    source=io.BytesIO(data)
    output=io.BytesIO()
    with zipfile.ZipFile(source) as z,zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
        for info in z.infolist():
            original=z.read(info)
            cleaned=clean_bytes(original,Path(info.filename).suffix.lower(),secrets)
            changed|=cleaned!=original
            target.writestr(info,cleaned)
    return output.getvalue() if changed else data


def clean_bytes(data,suffix,secrets):
    if suffix=='.zip':
        return clean_zip(data,secrets)
    # SQLite is handled separately, maintaining valid file structure.
    if data.startswith(b'SQLite format 3\x00'):
        if any(s in data for s in secrets) or re.search(rb'AIza[0-9A-Za-z_-]{35}',data):
            raise RuntimeError('Credential-bearing SQLite found; sanitize via SQLite before publishing')
        return data
    if suffix in TEXT or suffix=='':
        return scrub(data,secrets)
    if any(s in data for s in secrets):
        raise RuntimeError('Credential-bearing binary found; format-specific sanitization required')
    return data


def files():
    errors=[]
    for base,dirs,names in os.walk(ROOT,onerror=lambda e:errors.append(Path(e.filename).relative_to(ROOT).as_posix())):
        dirs[:]=[d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(names):
            p=Path(base)/name
            if name in SKIP_NAMES or (name.startswith('.env.') and name!='.env.example') or name.endswith(('.pyc','.pyo','.sqlite-wal','.sqlite-shm')):
                continue
            yield p
    if errors:
        raise RuntimeError('Unreadable source directories: '+', '.join(errors))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-unreadable-images',action='store_true')
    parser.add_argument('--images-only',action='store_true',help='Supplementary image archive when read access requires elevation')
    args=parser.parse_args()
    secrets=secret_variants()
    destination=ROOT/'.publish-repo/Data_Selection'
    tag=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    snapshot=destination/'workspace_snapshots'/(('images_' if args.images_only else '')+tag)
    snapshot.mkdir(parents=True,exist_ok=True)
    changed=[]
    manifests=[]
    unreadable=[]
    # A complete snapshot contains data and code, while browsable files are copied
    # separately. Copies of generated runtime envs/models are intentionally absent.
    with tempfile.TemporaryDirectory(prefix='truead_publish_') as temp:
        archive=Path(temp)/'workspace.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
            try:
                iterator=(p for p in (ROOT/'text_test_data/images').rglob('*') if p.is_file()) if args.images_only else files()
                last_group=None
                for p in iterator:
                    relative=p.relative_to(ROOT)
                    if relative.parts[0]!=last_group:
                        last_group=relative.parts[0]
                        print('Archiving:',last_group,flush=True)
                    raw=p.read_bytes()
                    cleaned=clean_bytes(raw,p.suffix.lower(),secrets)
                    if cleaned!=raw:
                        changed.append(relative.as_posix())
                    z.writestr(relative.as_posix(),cleaned)
                    manifests.append(dict(path=relative.as_posix(),bytes=len(cleaned),sha256=hashlib.sha256(cleaned).hexdigest()))
                    # Large/runtime/data files live in the restorable archive.
                    if relative.parts[0] not in {'data','state','exports','Data_List_Claim_Verification','text_test_data'}:
                        target=destination/relative
                        target.parent.mkdir(parents=True,exist_ok=True)
                        target.write_bytes(cleaned)
                    elif relative.parts[0] in {'Data_List_Claim_Verification','text_test_data'} and p.suffix in {'.md','.py','.xlsx'}:
                        target=destination/relative
                        target.parent.mkdir(parents=True,exist_ok=True)
                        target.write_bytes(cleaned)
            except RuntimeError as error:
                if args.allow_unreadable_images and str(error)=='Unreadable source directories: text_test_data/images':
                    unreadable.append('text_test_data/images')
                else:
                    raise
        parts=[]
        with archive.open('rb') as source:
            index=1
            while chunk:=source.read(40*1024*1024):
                filename=f'workspace.zip.part{index:03d}'
                (snapshot/filename).write_bytes(chunk)
                parts.append(dict(file=filename,bytes=len(chunk),sha256=hashlib.sha256(chunk).hexdigest()))
                index+=1
        with zipfile.ZipFile(archive) as check:
            if check.testzip():
                raise RuntimeError('Snapshot ZIP integrity failure')
        manifest=dict(format='concatenated ZIP parts',created_at_utc=tag,archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                      files=manifests,parts=parts,redacted_files=changed,excluded_unreadable=unreadable,
                      excluded=['.env and credential files','virtual environments','downloaded tools/models','Python caches','runtime lock files'])
        (snapshot/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(snapshot=snapshot.relative_to(ROOT).as_posix(),files=len(manifests),parts=len(parts),
                          compressed_bytes=sum(p['bytes'] for p in parts),redacted_files=changed,unreadable=unreadable),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
