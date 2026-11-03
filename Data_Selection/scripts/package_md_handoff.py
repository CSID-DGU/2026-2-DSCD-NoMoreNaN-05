"""Package verified outputs; optionally copy them beside the user-supplied DB."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--copy-to-desktop-folder',action='store_true')
    args=parser.parse_args()
    out=ROOT/'exports/claim_type_db_20261103'
    reports=out/'reports';reports.mkdir(exist_ok=True)
    source=ROOT/'data/processed/md_enrichment_20261103'
    for path in source.glob('*.json'):
        shutil.copy2(path,reports/path.name)
    specs=out/'specifications';specs.mkdir(exist_ok=True)
    base=Path.home()/'Desktop'/'TRUEAD_DB_보강자료'
    shutil.copy2(base/'data_collection/db_enrichment_guide.md',specs/'db_enrichment_guide.md')
    shutil.copy2(Path.home()/'Documents'/'카카오톡 받은 파일'/'claim_type_db_format.md',specs/'claim_type_db_format.md')
    with zipfile.ZipFile(out/'video_jsons.zip','a',compression=zipfile.ZIP_DEFLATED) as archive:
        if 'README.md' not in archive.namelist():archive.write(out/'README.md','README.md')
    complete=out/'TRUEAD_DB_enrichment_outputs_20261103.zip'
    with zipfile.ZipFile(complete,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out.rglob('*')):
            if path.is_file() and path.suffix!='.zip':archive.write(path,path.relative_to(out).as_posix())
    with zipfile.ZipFile(complete) as archive:
        assert archive.testzip() is None
        assert len([n for n in archive.namelist() if n.startswith('videos/') and n.endswith('.json')])==535
    summary=json.loads((out/'summary.json').read_text(encoding='utf-8'))
    if args.copy_to_desktop_folder:
        target=base/'작업결과_20261103'
        if target.exists():raise ValueError('Delivery directory already exists; not overwriting')
        shutil.copytree(out,target)
        for name in ['claims_with_db.json','TRUEAD_DB_enrichment_outputs_20261103.zip','video_jsons.zip']:
            assert hashlib.sha256((out/name).read_bytes()).digest()==hashlib.sha256((target/name).read_bytes()).digest()
        print('Delivery folder:',target)
    print(json.dumps(dict(videos=summary['videos'],claims=summary['claims'],effect_fields_preserved=summary['claim_effect_fields_preserved'],archive=str(complete),archive_bytes=complete.stat().st_size),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
