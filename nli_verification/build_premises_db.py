"""
NLI용 SQLite DB 만들기
evidence_prep.py로 정리한 전제 문장 CSV를 SQLite 테이블로 넣고,
앞으로 NLI 결과를 저장할 테이블도 함께 만든다.

실행:
    python build_premises_db.py                  # 같은 폴더에 nli_premises.sqlite 생성
    python build_premises_db.py 다른이름.sqlite    # 파일 이름 지정

필요한 파일(같은 폴더): premises_product.csv, premises_ingredient.csv
선택 파일(있으면 함께 넣음): nli_test_results.csv, hyp_test_results.csv

만들어지는 테이블
    premise_product     제품별 정리된 기능성·주의사항 문장 (core, 주어 없음)
    premise_ingredient  원료별 정리된 문장
    nli_result          NLI 결과 저장용 (지금은 비어 있음)
    test_nli / test_hyp 1·2차 실험 결과 (CSV가 있을 때만)
"""
import csv
import os
import sqlite3
import sys

csv.field_size_limit(10**8)
DB = sys.argv[1] if len(sys.argv) > 1 else "nli_premises.sqlite"

SCHEMA = """
CREATE TABLE premise_product (
    ref                TEXT PRIMARY KEY,      -- product:{id}:F0 (기능성) / P0 (주의사항)
    product_id         INTEGER NOT NULL,
    evidence_type      TEXT NOT NULL,         -- FUNCTIONALITY / PRECAUTION
    ingredient_label   TEXT,                  -- 원문에 적힌 원료명 (없으면 NULL)
    core               TEXT NOT NULL,         -- NLI 전제로 쓸 정리된 문장 (주어 없음)
    inferred_predicate INTEGER NOT NULL,      -- 서술어를 추정해서 붙였으면 1
    status             TEXT NOT NULL,         -- OK / CHECK
    is_raw_material    INTEGER NOT NULL,      -- 소비자용이 아닌 원료 제품이면 1
    raw                TEXT                   -- 정리 전 원문 조각
);
CREATE INDEX idx_pp_product ON premise_product(product_id, evidence_type);
CREATE INDEX idx_pp_label   ON premise_product(ingredient_label);

CREATE TABLE premise_ingredient (
    ref             TEXT PRIMARY KEY,         -- evidence:{evidence_id}:{번호}
    ingredient_id   INTEGER NOT NULL,
    evidence_id     INTEGER NOT NULL,
    evidence_type   TEXT NOT NULL,            -- OFFICIAL_FUNCTIONALITY / OFFICIAL_PRECAUTION
    stated_subject  TEXT,                     -- 원문이 "OO은 ~"으로 시작할 때의 주어
    core            TEXT NOT NULL,
    status          TEXT NOT NULL,
    raw             TEXT
);
CREATE INDEX idx_pi_ingredient ON premise_ingredient(ingredient_id, evidence_type);

CREATE TABLE nli_result (
    result_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id      TEXT NOT NULL,              -- 광고 주장 ID
    premise_ref   TEXT NOT NULL,              -- premise_product.ref 또는 premise_ingredient.ref
    evidence_type TEXT,
    target        TEXT,                       -- 전제·가설에 붙인 주어
    premise       TEXT NOT NULL,              -- 주어를 붙인 전제 문장
    hypothesis    TEXT NOT NULL,              -- 주어를 맞춘 가설 문장
    p_entail      REAL NOT NULL,
    p_neutral     REAL NOT NULL,
    p_contra      REAL NOT NULL,
    model         TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE INDEX idx_nr_claim ON nli_result(claim_id);
"""


def load(con, table, path, columns, ints=()):
    with open(path, encoding="utf-8-sig") as f:
        rows = []
        for r in csv.DictReader(f):
            row = []
            for c in columns:
                v = r.get(c, "")
                if c in ints:
                    v = int(v) if v not in ("", None) else 0
                elif v == "":
                    v = None
                row.append(v)
            rows.append(row)
    q = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})"
    con.executemany(q, rows)
    print(f"  {table:<20} {len(rows):>8,}행  ← {path}")


def load_any(con, table, path):
    """실험 결과 CSV는 열 이름 그대로 테이블을 만든다."""
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    cols = ", ".join(f'"{h}" TEXT' for h in header)
    con.execute(f"CREATE TABLE {table} ({cols})")
    con.executemany(f"INSERT INTO {table} VALUES ({', '.join('?' * len(header))})", rows)
    print(f"  {table:<20} {len(rows):>8,}행  ← {path}")


def main():
    if os.path.exists(DB):
        print(f"[중단] {DB} 파일이 이미 있어요. 지우거나 다른 이름을 지정하세요.")
        sys.exit(1)
    for need in ("premises_product.csv", "premises_ingredient.csv"):
        if not os.path.exists(need):
            print(f"[중단] {need}가 없어요. 먼저 evidence_prep.py를 실행하세요.")
            sys.exit(1)

    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    print(f"{DB} 만드는 중…")
    with con:
        load(con, "premise_product", "premises_product.csv",
             ["ref", "product_id", "evidence_type", "ingredient_label", "core",
              "inferred_predicate", "status", "is_raw_material", "raw"],
             ints=("product_id", "inferred_predicate", "is_raw_material"))
        load(con, "premise_ingredient", "premises_ingredient.csv",
             ["ref", "ingredient_id", "evidence_id", "evidence_type", "stated_subject",
              "core", "status", "raw"],
             ints=("ingredient_id", "evidence_id"))
        for table, path in (("test_nli", "nli_test_results.csv"), ("test_hyp", "hyp_test_results.csv")):
            if os.path.exists(path):
                load_any(con, table, path)

    # 확인용 조회: 2번 제품의 기능성 문장
    print("\n확인: product_id = 2 의 기능성 문장")
    for ref, core in con.execute(
            "SELECT ref, core FROM premise_product WHERE product_id = 2 AND evidence_type = 'FUNCTIONALITY'"):
        print(f"  {ref:<16} {core}")
    con.close()
    print(f"\n완료: {DB} ({os.path.getsize(DB) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
