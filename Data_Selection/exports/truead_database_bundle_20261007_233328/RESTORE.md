# TRUEAD database restore

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
