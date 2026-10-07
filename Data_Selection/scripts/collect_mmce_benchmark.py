"""Collect joycelynt/MMCE as a test-only visual claim extraction benchmark."""

import argparse
import csv
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
REPO_ID = "joycelynt/MMCE"
DATA_FILE = "data.json"
IMAGE_ARCHIVE = "all_images.zip"
OUTPUT_ROOT = ROOT / "text_test_data"
OUTPUT_CSV = OUTPUT_ROOT / "mmce.csv"
OUTPUT_IMAGES = OUTPUT_ROOT / "images"
MANIFEST = OUTPUT_ROOT / "mmce_manifest.json"
REQUIRED_SOURCE_FIELDS = {"full_text", "claim_text", "claim_images"}


def load_source(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("MMCE data.json is not valid JSON.") from exc
    if not isinstance(value, list) or not value:
        raise RuntimeError("MMCE data.json must be a non-empty JSON list.")
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            raise RuntimeError(f"MMCE row {index} is not an object.")
        missing = REQUIRED_SOURCE_FIELDS - set(row)
        if missing:
            raise RuntimeError(f"MMCE row {index} is missing source fields: {sorted(missing)}")
        if not isinstance(row["full_text"], str) or not isinstance(row["claim_text"], str):
            raise RuntimeError(f"MMCE row {index} has non-text full_text or claim_text.")
        if not isinstance(row["claim_images"], list) or not all(isinstance(name, str) for name in row["claim_images"]):
            raise RuntimeError(f"MMCE row {index} has an invalid claim_images value.")
    return value


def archive_image_map(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        mapping = {}
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = Path(member.filename).name
            if not name:
                continue
            if name in mapping:
                raise RuntimeError(f"Duplicate image basename in MMCE archive: {name}")
            mapping[name] = member.filename
    return mapping


def extract_images(archive_path, names, target):
    target.mkdir(parents=True, exist_ok=True)
    mapping = archive_image_map(archive_path)
    missing = sorted(set(names) - set(mapping))
    if missing:
        preview = ", ".join(missing[:5])
        raise RuntimeError(f"{len(missing)} referenced images are absent from {IMAGE_ARCHIVE}: {preview}")
    with zipfile.ZipFile(archive_path) as archive:
        for name in sorted(set(names)):
            destination = target / name
            with archive.open(mapping[name]) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)


def build_rows(records):
    rows = []
    for source_index, record in enumerate(records):
        metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
        image_names = record["claim_images"]
        image_paths = [f"text_test_data/images/{Path(name).name}" for name in image_names]
        rows.append({
            # Required benchmark contract columns. text and gold_claim are explicit aliases
            # for the source's full_text and claim_text respectively.
            "sample_id": f"mmce_train_{source_index:04d}",
            "text": record["full_text"],
            "gold_claim": record["claim_text"],
            # A JSON list preserves every image for multi-image rows in one CSV record.
            "image_path": json.dumps(image_paths, ensure_ascii=False),
            # Original source fields retained for traceability.
            "source_index": source_index,
            "article": record.get("article", ""),
            "date": record.get("date", ""),
            "label": record.get("label", ""),
            "location": record.get("location", ""),
            "full_text": record["full_text"],
            "claim_text": record["claim_text"],
            "claim_images": json.dumps(image_names, ensure_ascii=False),
            "original_language": metadata.get("original_language", ""),
            "original_language_text": metadata.get("original_language_text", ""),
        })
    return rows


def write_csv(path, rows):
    fields = [
        "sample_id", "text", "gold_claim", "image_path", "source_index", "article", "date", "label", "location",
        "full_text", "claim_text", "claim_images", "original_language", "original_language_text",
    ]
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def collect():
    data_path = Path(hf_hub_download(repo_id=REPO_ID, repo_type="dataset", filename=DATA_FILE))
    archive_path = Path(hf_hub_download(repo_id=REPO_ID, repo_type="dataset", filename=IMAGE_ARCHIVE))
    records = load_source(data_path)
    rows = build_rows(records)
    image_names = [name for row in records for name in row["claim_images"]]
    unique_image_names = set(image_names)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUTPUT_ROOT, prefix="mmce_images_") as temporary_dir:
        staged_images = Path(temporary_dir) / "images"
        extract_images(archive_path, image_names, staged_images)
        if OUTPUT_IMAGES.exists():
            shutil.rmtree(OUTPUT_IMAGES)
        staged_images.replace(OUTPUT_IMAGES)
    write_csv(OUTPUT_CSV, rows)
    manifest = {
        "repository": REPO_ID,
        "source_data_file": DATA_FILE,
        "source_image_archive": IMAGE_ARCHIVE,
        "source_split": "train",
        "source_schema": sorted(records[0]),
        "text_mapping": "full_text",
        "gold_claim_mapping": "claim_text",
        "image_mapping": "claim_images -> data/images/<original filename>",
        "record_count": len(rows),
        "image_references": len(image_names),
        "unique_images": len(unique_image_names),
        "output_csv": OUTPUT_CSV.relative_to(ROOT).as_posix(),
        "output_images": OUTPUT_IMAGES.relative_to(ROOT).as_posix(),
        "purpose": "test-only visual claim extraction benchmark; not for model training",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        manifest = collect()
    except Exception as exc:
        print(f"MMCE collection failed: {exc}")
        return 1
    print("MMCE benchmark collection completed")
    print(f"records: {manifest['record_count']}")
    print(f"image references: {manifest['image_references']}")
    print(f"unique images: {manifest['unique_images']}")
    print(f"CSV: {manifest['output_csv']}")
    print(f"Images: {manifest['output_images']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
