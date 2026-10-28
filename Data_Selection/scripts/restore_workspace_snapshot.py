"""Verify and restore a split GitHub workspace snapshot into an empty folder."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile


def restore(snapshot, destination):
    snapshot, destination=Path(snapshot).resolve(),Path(destination).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Destination must be empty; original data will not be overwritten')
    manifest=json.loads((snapshot/'manifest.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='truead_restore_') as temporary:
        archive=Path(temporary)/'workspace.zip'
        digest=hashlib.sha256()
        with archive.open('wb') as target:
            for part in manifest['parts']:
                source=(snapshot/part['file']).resolve()
                if source.parent!=snapshot:
                    raise ValueError('Invalid part path')
                contents=source.read_bytes()
                if len(contents)!=part['bytes'] or hashlib.sha256(contents).hexdigest()!=part['sha256']:
                    raise ValueError('Part checksum mismatch: '+part['file'])
                digest.update(contents)
                target.write(contents)
        if digest.hexdigest()!=manifest['archive_sha256']:
            raise ValueError('Archive checksum mismatch')
        with zipfile.ZipFile(archive) as z:
            expected={f['path']:f for f in manifest['files']}
            if set(z.namelist())!=set(expected):
                raise ValueError('Archive manifest member mismatch')
            for info in z.infolist():
                path=(destination/info.filename).resolve()
                if not path.is_relative_to(destination):
                    raise ValueError('Unsafe archive path')
                contents=z.read(info)
                record=expected[info.filename]
                if len(contents)!=record['bytes'] or hashlib.sha256(contents).hexdigest()!=record['sha256']:
                    raise ValueError('File checksum mismatch: '+info.filename)
            destination.mkdir(parents=True,exist_ok=True)
            z.extractall(destination)
    return len(manifest['files'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot',type=Path)
    parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args()
    print('Restored files:',restore(args.snapshot,args.destination))
