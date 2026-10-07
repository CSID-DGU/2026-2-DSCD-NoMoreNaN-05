"""Shared PostgreSQL connection configured in the project .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


def connect_postgres():
    import psycopg

    load_dotenv(ROOT / '.env')
    password = os.getenv('PGPASSWORD', '')
    if not password:
        raise ValueError('Set PGPASSWORD in the project .env')
    return psycopg.connect(
        host=os.getenv('PGHOST') or 'localhost',
        port=os.getenv('PGPORT') or '5432',
        dbname=os.getenv('PGDATABASE') or 'TrueAD_Evidence_Claim',
        user=os.getenv('PGUSER') or 'postgres',
        password=password,
        connect_timeout=10,
        application_name='TRUEAD',
    )
