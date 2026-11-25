import os

from claim_process.claim_extraction import main as llm_main

_proc = None


def start() -> None:
    global _proc
    gpus: set[int] = set()
    _proc = llm_main.start_llm(gpus)
    if _proc is not None:
        os.environ["SERVER_GPUS"] = ",".join(str(g) for g in sorted(gpus))


def wait() -> None:
    try:
        if llm_main.ready(llm_main.LLM_BASE_URL):
            return
        if _proc is None or _proc.poll() is not None:
            start()
        llm_main.wait_ready("LLM", _proc, llm_main.LLM_BASE_URL)
    except SystemExit as e:
        raise RuntimeError(f"LLM 서버 준비 실패: {e}") from e


def stop() -> None:
    global _proc
    llm_main.stop_server("LLM", _proc)
    _proc = None
