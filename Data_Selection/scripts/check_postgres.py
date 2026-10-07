"""Check local PostgreSQL connectivity without modifying data."""
import getpass
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from src.utils.postgres import connect_postgres


def main():
    load_dotenv(ROOT / '.env')
    if not os.getenv('PGPASSWORD'):
        if not sys.stdin.isatty():
            print('[PostgreSQL] PGPASSWORD is missing in .env; connection not attempted.')
            return 1
        os.environ['PGPASSWORD'] = getpass.getpass('PostgreSQL password (hidden): ')
    try:
        with connect_postgres() as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT current_database(), current_user, version()')
                database, user, version = cursor.fetchone()
        print(f'[PostgreSQL] Connected: {database} / {user}')
        print(version)
        return 0
    except Exception as exc:
        # Connection exceptions can contain credentials; do not print them.
        print(f'[PostgreSQL] Connection failed ({type(exc).__name__}). Check server, database, user and password.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
