"""Build the local SQLite database used to verify health-functional-food claims."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "Data_List_Claim_Verification"


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def text(value):
    return (value or "").strip()


def normalise_name(value):
    return re.sub(r"[\s\-_,.()\[\]]+", "", text(value)).casefold()


def json_value(value):
    return json.dumps(value or {}, ensure_ascii=False, separators=(",", ":"))


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE dataset_registry (
    dataset_key TEXT PRIMARY KEY,
    source_file TEXT NOT NULL,
    description TEXT NOT NULL,
    record_count INTEGER NOT NULL,
    loaded_at TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    manufacturing_report_number TEXT,
    product_name TEXT,
    product_name_normalized TEXT,
    company_name TEXT,
    registration_date TEXT,
    main_functionality TEXT,
    intake_method TEXT,
    intake_precautions TEXT,
    specification TEXT,
    appearance TEXT,
    shelf_life TEXT,
    storage_and_distribution_standard TEXT
);

CREATE INDEX idx_products_report_number ON products(manufacturing_report_number);
CREATE INDEX idx_products_name_normalized ON products(product_name_normalized);

CREATE TABLE ingredients (
    ingredient_id INTEGER PRIMARY KEY,
    ingredient_type TEXT NOT NULL CHECK (ingredient_type IN ('FUNCTIONAL_INGREDIENT', 'INDIVIDUALLY_APPROVED')),
    recognition_number TEXT,
    ingredient_name TEXT NOT NULL,
    ingredient_name_normalized TEXT NOT NULL,
    functionality_text TEXT,
    daily_intake_text TEXT,
    daily_intake_min TEXT,
    daily_intake_max TEXT,
    intake_precautions TEXT,
    company_name TEXT,
    approval_date TEXT,
    company_address TEXT
);

CREATE INDEX idx_ingredients_recognition_number ON ingredients(recognition_number);
CREATE INDEX idx_ingredients_name_normalized ON ingredients(ingredient_name_normalized);

CREATE TABLE diseases (
    disease_id INTEGER PRIMARY KEY,
    disease_code TEXT NOT NULL,
    disease_name TEXT NOT NULL,
    disease_name_normalized TEXT NOT NULL,
    disease_name_en TEXT,
    sick_type TEXT,
    sick_type_label TEXT,
    medicine_type TEXT,
    medicine_type_label TEXT,
    UNIQUE (disease_code, sick_type, medicine_type)
);

CREATE INDEX idx_diseases_code ON diseases(disease_code);
CREATE INDEX idx_diseases_name_normalized ON diseases(disease_name_normalized);

CREATE TABLE claims (
    claim_id INTEGER PRIMARY KEY,
    claim_origin TEXT NOT NULL CHECK (claim_origin IN ('VIDEO', 'MANUAL')),
    product_id INTEGER REFERENCES products(product_id),
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    subject_text TEXT,
    predicate_text TEXT,
    target_text TEXT,
    disease_id INTEGER REFERENCES diseases(disease_id),
    extracted_at TEXT NOT NULL
);

CREATE INDEX idx_claims_product_id ON claims(product_id);
CREATE INDEX idx_claims_disease_id ON claims(disease_id);

CREATE TABLE evidence (
    evidence_id INTEGER PRIMARY KEY,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(ingredient_id),
    evidence_type TEXT NOT NULL CHECK (evidence_type IN ('OFFICIAL_FUNCTIONALITY', 'OFFICIAL_INTAKE', 'OFFICIAL_PRECAUTION')),
    evidence_text TEXT NOT NULL,
    source_authority TEXT NOT NULL DEFAULT 'MFDS'
);

CREATE INDEX idx_evidence_ingredient_id ON evidence(ingredient_id);

CREATE TABLE claim_evidence_links (
    link_id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES claims(claim_id),
    evidence_id INTEGER NOT NULL REFERENCES evidence(evidence_id),
    match_method TEXT NOT NULL CHECK (match_method IN ('EXACT', 'RULE', 'LLM', 'MANUAL')),
    verdict TEXT NOT NULL CHECK (verdict IN ('SUPPORTED', 'CONTRADICTED', 'INSUFFICIENT', 'REVIEW_REQUIRED')),
    confidence REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    reason TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (claim_id, evidence_id, match_method)
);

CREATE INDEX idx_links_claim_id ON claim_evidence_links(claim_id);
CREATE INDEX idx_links_evidence_id ON claim_evidence_links(evidence_id);

CREATE VIEW v_claim_review_queue AS
SELECT
    c.claim_id, c.claim_origin, p.product_name, c.claim_text, c.claim_type,
    COUNT(l.link_id) AS linked_evidence_count
FROM claims c
LEFT JOIN products p ON p.product_id = c.product_id
LEFT JOIN claim_evidence_links l ON l.claim_id = c.claim_id
GROUP BY c.claim_id;
"""


def load_jsonl(path):
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, start=1):
            if line.strip():
                try:
                    yield line_number, json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Invalid JSONL at {path.name}:{line_number}") from exc


def load_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        yield from enumerate(csv.DictReader(stream), start=2)


def build_database(data_dir, database_path):
    files = {
        "products": data_dir / "health_functional_food_products.jsonl",
        "functional_ingredients": data_dir / "functional_ingredient_status.txt",
        "individual_ingredients": data_dir / "individually_approved_ingredient_info.txt",
        "diseases": data_dir / "disease_codes.jsonl",
    }
    missing = [path.name for path in files.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing input files: {', '.join(missing)}")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()

    connection = sqlite3.connect(database_path)
    # Original JSON/CSV files remain beside the DB; do not duplicate their large payload here.
    connection.execute("PRAGMA journal_mode = DELETE")
    connection.execute("PRAGMA synchronous = NORMAL")
    connection.executescript(SCHEMA)
    loaded_at = utc_now()
    counts = {}
    try:
        product_rows = []
        for product_id, (_, row) in enumerate(load_jsonl(files["products"]), start=1):
            product_rows.append((
                product_id, text(row.get("manufacturing_report_number")), text(row.get("product_name")),
                normalise_name(row.get("product_name")), text(row.get("company_name")), text(row.get("registration_date")),
                text(row.get("main_functionality")), text(row.get("intake_method")), text(row.get("intake_precautions")),
                text(row.get("specification")), text(row.get("appearance")), text(row.get("shelf_life")),
                text(row.get("storage_and_distribution_standard")),
            ))
        connection.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", product_rows)
        counts["products"] = len(product_rows)
        counts["claims"] = 0

        ingredient_rows = []
        for _, row in load_csv(files["functional_ingredients"]):
            name = text(row.get("APLC_RAWMTRL_NM"))
            ingredient_rows.append((
                "FUNCTIONAL_INGREDIENT", text(row.get("HF_FNCLTY_MTRAL_RCOGN_NO")), name, normalise_name(name),
                text(row.get("FNCLTY_CN")), text(row.get("DAY_INTK_CN")), None, None, text(row.get("IFTKN_ATNT_MATR_CN")),
                text(row.get("BSSH_NM")), text(row.get("PRMS_DT")), text(row.get("ADDR")),
            ))
        for _, row in load_csv(files["individual_ingredients"]):
            name = text(row.get("RAWMTRL_NM"))
            ingredient_rows.append((
                "INDIVIDUALLY_APPROVED", text(row.get("HF_FNCLTY_MTRAL_RCOGN_NO")), name, normalise_name(name),
                text(row.get("PRIMARY_FNCLTY")), None, text(row.get("DAY_INTK_LOWLIMIT")), text(row.get("DAY_INTK_HIGHLIMIT")),
                text(row.get("IFTKN_ATNT_MATR_CN")), None, None, None,
            ))
        connection.executemany(
            "INSERT INTO ingredients (ingredient_type, recognition_number, ingredient_name, ingredient_name_normalized, functionality_text, daily_intake_text, daily_intake_min, daily_intake_max, intake_precautions, company_name, approval_date, company_address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ingredient_rows,
        )
        counts["ingredients"] = len(ingredient_rows)

        evidence_rows = []
        for ingredient_id, functionality, intake, minimum, maximum, precautions in connection.execute(
            "SELECT ingredient_id, functionality_text, daily_intake_text, daily_intake_min, daily_intake_max, intake_precautions FROM ingredients"
        ):
            if functionality:
                evidence_rows.append((ingredient_id, "OFFICIAL_FUNCTIONALITY", functionality))
            intake_text = intake or " ".join(item for item in (minimum, maximum) if item)
            if intake_text:
                evidence_rows.append((ingredient_id, "OFFICIAL_INTAKE", intake_text))
            if precautions:
                evidence_rows.append((ingredient_id, "OFFICIAL_PRECAUTION", precautions))
        connection.executemany(
            "INSERT INTO evidence (ingredient_id, evidence_type, evidence_text) VALUES (?, ?, ?)", evidence_rows)
        counts["evidence"] = len(evidence_rows)

        disease_rows = []
        for _, row in load_jsonl(files["diseases"]):
            name = text(row.get("disease_name"))
            disease_rows.append((
                text(row.get("disease_code")), name, normalise_name(name), text(row.get("disease_name_en")),
                text(row.get("sick_type")), text(row.get("sick_type_label")), text(row.get("medicine_type")),
                text(row.get("medicine_type_label")),
            ))
        connection.executemany(
            "INSERT INTO diseases (disease_code, disease_name, disease_name_normalized, disease_name_en, sick_type, sick_type_label, medicine_type, medicine_type_label) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            disease_rows,
        )
        counts["diseases"] = len(disease_rows)

        registry = [
            ("products", files["products"].name, "건강기능식품 제품정보", counts["products"], loaded_at),
            ("functional_ingredients", files["functional_ingredients"].name, "기능성 원료 인정현황", sum(1 for _ in load_csv(files["functional_ingredients"])), loaded_at),
            ("individual_ingredients", files["individual_ingredients"].name, "개별인정형 원료정보", sum(1 for _ in load_csv(files["individual_ingredients"])), loaded_at),
            ("diseases", files["diseases"].name, "질병 코드", counts["diseases"], loaded_at),
        ]
        connection.executemany("INSERT INTO dataset_registry VALUES (?, ?, ?, ?, ?)", registry)
        connection.commit()
        connection.execute("VACUUM")
    except BaseException:
        connection.rollback()
        connection.close()
        raise
    finally:
        connection.close()
    return counts


def build_browser_database(source_path, browser_path):
    """Create a compact, read-only-friendly SQLite copy for VS Code table browsing."""
    if browser_path.exists():
        browser_path.unlink()
    connection = sqlite3.connect(browser_path)
    try:
        connection.execute("ATTACH DATABASE ? AS source", (str(source_path),))
        connection.executescript("""
            CREATE TABLE database_info (note TEXT NOT NULL);
            INSERT INTO database_info VALUES ('Browse copy: claims stays empty until advertising-video claims are extracted; use claim_verification.sqlite for writes.');
            CREATE TABLE products AS
                SELECT product_id, manufacturing_report_number, product_name, product_name_normalized, company_name, registration_date, main_functionality
                FROM source.products;
            CREATE INDEX idx_products_name ON products(product_name);
            CREATE TABLE ingredients AS
                SELECT ingredient_id, ingredient_type, recognition_number, ingredient_name, ingredient_name_normalized, functionality_text, daily_intake_text,
                       daily_intake_min, daily_intake_max, intake_precautions
                FROM source.ingredients;
            CREATE INDEX idx_ingredients_name ON ingredients(ingredient_name);
            CREATE TABLE diseases AS
                SELECT disease_id, disease_code, disease_name, disease_name_normalized, disease_name_en, sick_type_label, medicine_type_label
                FROM source.diseases;
            CREATE INDEX idx_diseases_code ON diseases(disease_code);
            CREATE TABLE evidence AS
                SELECT evidence_id, ingredient_id, evidence_type, evidence_text, source_authority
                FROM source.evidence;
            CREATE TABLE claim_evidence_links AS
                SELECT link_id, claim_id, evidence_id, match_method, verdict, confidence, reason, created_at
                FROM source.claim_evidence_links;
            CREATE TABLE claims (
                claim_id INTEGER PRIMARY KEY,
                claim_origin TEXT NOT NULL,
                product_id INTEGER,
                claim_text TEXT NOT NULL,
                claim_type TEXT NOT NULL,
                subject_text TEXT,
                predicate_text TEXT,
                target_text TEXT,
                disease_id INTEGER,
                extracted_at TEXT NOT NULL
            );
        """)
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--browser-database", type=Path, default=None,
                        help="Optional compact DB for browsing tables in VS Code")
    args = parser.parse_args()
    database = args.database or args.data_dir / "claim_verification.sqlite"
    try:
        counts = build_database(args.data_dir, database)
    except Exception as exc:
        print(f"Database build failed: {exc}")
        return 1
    print(f"Database created: {database}")
    browser_database = args.browser_database or args.data_dir / "claim_verification_browser.sqlite"
    build_browser_database(database, browser_database)
    print(f"Browser database created: {browser_database}")
    for name, count in counts.items():
        print(f"{name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
