"""판정 결과(04_final_results.json)에 gpt-oss 설명문 explanation을 넣는다.

claim 행마다 LLM 호출 1회로 행 요약·A.checks 항목별·B 설명을 함께 받는다.
모든 행이 성공한 뒤에만 파일을 덮어쓴다. 실패는 예외로 올린다.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from pathlib import Path

from claim_process.claim_extraction import main as llm_main
from claim_process.claim_extraction.common import LLMClient, parse_json_object
from claim_process.claim_verification.verdict_a.claim_verification.finding import (
    OVERCLAIM,
    VIOLATION,
)
from claim_process.claim_verification.verdict_b import summarize
from files import load_json, save_json

from .prompts import (
    POPUP_SCHEMA,
    POPUP_SYSTEM,
    SYSTEM,
    explain_schema,
    format_popup,
    format_user,
)

LLM_BASE_URL = llm_main.LLM_BASE_URL
LLM_MODEL = "gpt-oss-120b"
REASONING_EFFORT = "low"
TEMPERATURE = 0.0
MAX_TOKENS = 1024
TIMEOUT = 300.0          # 초. urlopen 블로킹 작업 1회 상한
PARALLEL = 4             # llama-server 슬롯 수
EXPLANATION_CHARS = 140  # 설명 1개 길이 점검 상한

B_KEYS = ("label", "reason_code", "reason", "evidence_text", "scores", "all_findings", "flags", "parts",
          "duplicate_of")
RULE_GROUP_EAT = "대상 일치(섭취 가능 표현, C 임계값 없음)"
RULE_C_HIGH = f"C≥{summarize.TAU_HIGH} 및 대상·상황 일치"


@contextmanager
def llm_server():
    proc = None
    try:
        try:
            proc = llm_main.start_llm(set())
            llm_main.wait_ready("LLM", proc, LLM_BASE_URL)
        except SystemExit as e:
            raise RuntimeError(f"LLM 서버 준비 실패: {e}") from e
        yield
    finally:
        llm_main.stop_server("LLM", proc)


def _conflict(c: dict, b_record: dict) -> dict | None:
    prem = next((ev for _, code, ev in summarize.findings_of(c) if code == "PRECAUTION_CONFLICT"), None)
    if prem is None:
        return None
    hits = [x for x in c.get("checks") or [] if x["evidence_type"] == "PRECAUTION" and x["premise"] == prem]
    return {"ref": hits[0]["ref"] if hits else None, "premise": prem,
            "pairs": [{"hypothesis": x["hypothesis"], "hyp_source": x["hyp_source"], "C": x["C"]} for x in hits],
            "C_max": max((x["C"] for x in hits), default=None),
            "rule": RULE_GROUP_EAT if summarize.GROUP_EAT.search(c.get("text") or "") else RULE_C_HIGH,
            "is_main": b_record["reason_code"] == "PRECAUTION_CONFLICT"}


def _nli(c: dict, b_record: dict) -> dict:
    function = reverse = precaution = None
    if c.get("max_entail_function") is not None:
        function = {"ref": c["best_function_ref"], "premise": c["best_function_text"],
                    "hypothesis": c["best_function_hypothesis"], "hyp_source": c["best_function_hyp_source"],
                    "E": c["max_entail_function"]}
    if c.get("reverse_max_E") is not None:
        reverse = {"ref": c["reverse_best_ref"], "premise": c["reverse_best_hypothesis"],
                   "hypothesis": c["reverse_best_text"], "E": c["reverse_max_E"]}
    if c.get("max_contra_precaution") is not None:
        precaution = {"ref": c["best_precaution_ref"], "premise": c["best_precaution_text"],
                      "C": c["max_contra_precaution"]}
    parts = None
    if c.get("parts"):
        parts = [{"text": p["text"],
                  "forward": {"premise": p.get("best_text"), "hypothesis": p["hypothesis"], "E": p.get("max_E")},
                  "reverse": {"premise": p["hypothesis"], "hypothesis": p.get("reverse_best_text"),
                              "E": p.get("reverse_E")}}
                 for p in c["parts"]]
    return {"subject": c.get("subject"), "basis": c.get("basis"), "basis_reason": c.get("basis_reason"),
            "candidate_count": c.get("candidate_count"), "is_question": c.get("is_question"),
            "is_health_claim_raw": c.get("is_health_claim"),
            "is_health_claim": summarize._recompute_flags(c)["is_health_claim"],
            "health_claim_E": c.get("health_claim_E"),
            "function": function, "reverse": reverse, "precaution_max": precaution,
            "conflict": _conflict(c, b_record),
            "templates": {name: {"status": t["status"], "E": t["E"]} for name, t in (c.get("templates") or {}).items()},
            "parts": parts}


def build_input(row: dict, product: dict | None, b_record: dict | None, nli_claim: dict | None) -> dict:
    a = row["A"]
    b = None
    if row["B"] is not None:
        b = {**{k: b_record[k] for k in B_KEYS}, "nli": _nli(nli_claim, b_record) if nli_claim else None}
    return {"claim": {"id": row["claim_id"], "text": row["text"], "claim_type": row["claim_type"],
                      "parsed": row["parsed"]},
            "product": ({"product_name": product["product_name"], "match_status": product["match_status"]}
                        if product else None),
            "final": {"label": row["final_label"], "decided_by": row["decided_by"],
                      "skipped_reason": row["skipped_reason"]},
            "A": None if a is None else {"label": a["label"], "reason_codes": a["reason_codes"],
                                         "checks": [{"n": i, **_without(ck)} for i, ck in enumerate(a["checks"])]},
            "B": b}


def explain_row(llm, payload: dict, n_checks: int, has_b: bool) -> dict:
    raw = llm.chat(SYSTEM, format_user(payload), schema=explain_schema(n_checks, has_b))
    out = parse_json_object(raw)
    cid = payload["claim"]["id"]
    if not isinstance(out, dict):
        raise ValueError(f"설명 출력이 객체가 아님: {cid}")  # noqa: TRY004
    checks = out.get("checks")
    if not isinstance(checks, list) or len(checks) != n_checks:
        raise ValueError(f"checks 개수 불일치: {cid}")
    texts = [out.get("claim"), *checks] + ([out.get("B")] if has_b else [])
    if any(not isinstance(t, str) or not t.strip() for t in texts):
        raise ValueError(f"설명이 비었거나 문자열이 아님: {cid}")
    if not has_b and out.get("B") is not None:
        raise ValueError(f"B가 없는데 B 설명이 있음: {cid}")
    return out


def _without(d: dict) -> dict:
    return {k: v for k, v in d.items() if k != "explanation"}


def insert(row: dict, out: dict) -> dict:
    new = {}
    for k, v in _without(row).items():
        if k == "A" and v is not None:
            v = {**v, "checks": [{**_without(ck), "explanation": e} for ck, e in zip(v["checks"], out["checks"])]}
        elif k == "B" and v is not None:
            v = {**_without(v), "explanation": out["B"]}
        new[k] = v
        if k == "skipped_reason":
            new["explanation"] = out["claim"]
    return new


def explain(final: dict, b_doc: dict, nli_results: list[dict], llm, parallel: int = PARALLEL) -> dict:
    rows = final["results"]
    products = {(v["video_id"], p["product_ref"]): p for v in final["videos"] for p in v["products"]}
    b_index = {(r["video_id"], r["product_ref"], r["claim_id"]): r for r in b_doc["results"]}
    nli_index = {(v["video_id"], v["product_ref"], c["claim_id"]): c for v in nli_results for c in v["nli_claims"]}
    tasks = []
    for row in rows:
        k = (row["video_id"], row["product_ref"], row["claim_id"])
        payload = build_input(row, products.get(k[:2]), b_index.get(k), nli_index.get(k))
        tasks.append((payload, len(row["A"]["checks"]) if row["A"] else 0, row["B"] is not None))
    outs = [None] * len(tasks)
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        index = {pool.submit(explain_row, llm, p, n, hb): i for i, (p, n, hb) in enumerate(tasks)}
        try:
            for f in as_completed(index):
                outs[index[f]] = f.result()
        except BaseException:
            pool.shutdown(cancel_futures=True)
            raise
    final["results"] = [insert(row, out) for row, out in zip(rows, outs)]
    return final


def popup_summary(rows: list[dict], llm) -> str:
    items = [{"label": r["final_label"], "text": r["text"], "explanation": r["explanation"]}
             for r in rows if r["final_label"] in (VIOLATION, OVERCLAIM)]
    v = sum(r["final_label"] == VIOLATION for r in rows)
    o = sum(r["final_label"] == OVERCLAIM for r in rows)
    case = "both" if v and o else "violation" if v else "overclaim" if o else "none"
    payload = {"counts": {"violation": v, "overclaim": o, "claims": len(rows)}, "items": items}
    out = parse_json_object(llm.chat(POPUP_SYSTEM, format_popup(case, payload), schema=POPUP_SCHEMA))
    text = out.get("summary") if isinstance(out, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise ValueError("팝업 요약이 비었거나 문자열이 아님")
    return text


def add_popup_summary(final: dict, llm) -> dict:
    for video in final["videos"]:
        rows = [r for r in final["results"] if r["video_id"] == video["video_id"]]
        video["popup_summary"] = popup_summary(rows, llm)
    return final


def run(run_dir: Path) -> dict:
    final = load_json(run_dir / "04_final_results.json")
    b_doc = load_json(run_dir / "03_verdict_b.json")
    nli_results = load_json(run_dir / "03_nli_results.json")
    with llm_server():
        llm = LLMClient(LLM_BASE_URL, LLM_MODEL, TEMPERATURE, REASONING_EFFORT, max_tokens=MAX_TOKENS,
                        timeout=TIMEOUT)
        final = explain(final, b_doc, nli_results, llm)
        final = add_popup_summary(final, llm)
    save_json(run_dir / "04_final_results.json", final)
    return final
