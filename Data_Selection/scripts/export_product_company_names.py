"""Export product/company pairs without changing the source SQLite database."""

import json
import re
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "Data_List_Claim_Verification"

# Only suffixes observed in this database are removed. Do not strip arbitrary
# final words: names such as 경북과학대학식품공장 must remain intact.
LOCATIONS = (
    "논산", "익산", "제천", "충주", "대구", "진천", "세종", "반월",
    "인천", "광혜원", "오송", "홍천", "천안", "평택", "선유", "전주",
    "금산", "나주", "군산", "안성", "아산", "진안", "문산", "포천",
    "당진", "청운", "원성", "음성", "봉동",
)
SITE_SUFFIX = re.compile(
    r"\s*(?:" + "|".join(LOCATIONS)
    + r")\s*(?:제?\s*\d+)?(?:공장|지점)$"
)
NUMBERED_FACTORY = re.compile(r"\s*제?\s*\d+공장(?:\s*,\s*제?\s*\d+공장)*$")
SPECIAL_SUFFIXES = {
    "안성인삼농업협동조합 인삼가공공장": "안성인삼농업협동조합",
    "유진하이텍(주) 오송바이오공장": "유진하이텍(주)",
}


def clean_company_name(name):
    name = re.sub(r"\s+", " ", name or "").strip()
    if name in SPECIAL_SUFFIXES:
        return SPECIAL_SUFFIXES[name]
    cleaned = SITE_SUFFIX.sub("", name)
    cleaned = NUMBERED_FACTORY.sub("", cleaned).strip()
    return cleaned or name


def main():
    db = DATA_DIR / "claim_verification.sqlite"
    connection = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        rows = connection.execute(
            "SELECT product_name, company_name FROM products ORDER BY product_id"
        ).fetchall()
    finally:
        connection.close()

    products = [
        {"product_name": product, "company_name": clean_company_name(company)}
        for product, company in rows
    ]
    changes = [
        {"original": company, "cleaned": clean_company_name(company)}
        for company in sorted({company for _, company in rows if company})
        if company != clean_company_name(company)
    ]
    destination = DATA_DIR / "product_company_names_cleaned.json"
    destination.write_text(
        json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    audit = DATA_DIR / "company_name_cleanup_mapping.json"
    audit.write_text(
        json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"products": len(products), "changed_companies": len(changes),
                      "output": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
