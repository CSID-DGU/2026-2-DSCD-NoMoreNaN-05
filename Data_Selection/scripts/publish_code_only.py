"""Copy source/documents to the publishing checkout without data or JSON.

Does not commit or push. Existing tracked data is left untouched. Credential
checks stop the copy rather than rewriting executable source silently.
"""
import hashlib
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.prepare_github_snapshot import secret_variants


def main():
    destination = ROOT / '.publish-repo' / 'Data_Selection'
    allowed = {'.py', '.md', '.ps1', '.sh', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.sql'}
    files = [p for p in ROOT.iterdir() if p.is_file() and (
        p.suffix in allowed or p.name.startswith('requirements') and p.suffix == '.txt'
        or p.name == '.env.example')]
    for directory in ('scripts', 'src', 'tests', 'docs', 'configs'):
        files += [p for p in (ROOT/directory).rglob('*') if p.is_file()
                  and p.suffix in allowed and '__pycache__' not in p.parts]
    # Retain human-readable results, not the generated datasets they describe.
    files += list((ROOT/'exports').rglob('*.md'))
    secrets = secret_variants()
    patterns = [rb'AIza[0-9A-Za-z_-]{35}', rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}',
                rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']
    prepared = []
    for path in sorted(set(files)):
        data = path.read_bytes()
        if any(secret in data for secret in secrets) or any(re.search(pattern, data) for pattern in patterns):
            raise RuntimeError('Potential credential detected; no files copied: '+str(path.relative_to(ROOT)))
        prepared.append((path.relative_to(ROOT), data))
    changes = []
    for relative, data in prepared:
        target = destination/relative
        if target.exists() and target.read_bytes() == data:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        changes.append(relative.as_posix())
    ignore = (ROOT/'.gitignore').read_text(encoding='utf-8')
    ignore += '\n# Code-only publishing policy: existing tracked JSON remains historical.\n*.json\n*.jsonl\n*.sqlite\n*.sqlite-*\n*.db\n*.dump\n*.zip\n*.zip.part*\n'
    (destination/'.gitignore').write_text(ignore, encoding='utf-8')
    print(f'Copied {len(changes)} changed source/document files; scanned {len(prepared)} files.')
    print('No JSON, database, archive, environment credentials, or runtime data copied.')


if __name__ == '__main__':
    main()
