import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.restore_workspace_snapshot import restore
from scripts.prepare_github_snapshot import scrub


class SnapshotTests(unittest.TestCase):
    def make_snapshot(self, folder):
        contents=b'public result'
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,'w') as z:
            z.writestr('data/result.txt',contents)
        data=buffer.getvalue()
        parts=[]
        for index,part in enumerate((data[:50],data[50:]),1):
            name=f'workspace.zip.part{index:03d}'
            (folder/name).write_bytes(part)
            parts.append(dict(file=name,bytes=len(part),sha256=hashlib.sha256(part).hexdigest()))
        manifest=dict(parts=parts,archive_sha256=hashlib.sha256(data).hexdigest(),
                      files=[dict(path='data/result.txt',bytes=len(contents),sha256=hashlib.sha256(contents).hexdigest())])
        (folder/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')

    def test_split_snapshot_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            self.make_snapshot(folder)
            destination=folder/'restored'
            self.assertEqual(restore(folder,destination),1)
            self.assertEqual((destination/'data/result.txt').read_bytes(),b'public result')

    def test_corruption_blocks_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            self.make_snapshot(folder)
            (folder/'workspace.zip.part001').write_bytes(b'corrupted')
            with self.assertRaises(ValueError):
                restore(folder,folder/'restored')
            self.assertFalse((folder/'restored').exists())

    def test_restore_does_not_overwrite_existing_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp)/'existing.txt').write_text('keep',encoding='utf-8')
            with self.assertRaises(ValueError):
                restore(temp,temp)

    def test_url_key_and_known_secret_are_removed(self):
        result=scrub(b'https://example.com?serviceKey=[REDACTED]&x=1 password=example-secret',[b'example-secret'])
        self.assertNotIn(b'example-secret',result)
        self.assertIn(b'&x=1',result)
