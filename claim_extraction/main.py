"""python main.py [영상.mp4 | 폴더]   # 기본 data/ 전부

전체 파이프라인을 한 번에 돌린다. 단계마다 conda env가 달라서 subprocess로 실행한다.
모델 하나당 GPU 한 장. 단계마다 그 시점에 여유 메모리가 가장 큰 카드를 고르고,
MIN_FREE_GB보다 적으면 실행하지 않는다. 큰 모델은 부족한 만큼만 CPU에 둔다.

  1. gpt-oss-120b 서버 (serve_llm.sh, vLLM)      → audio/main.py      → 서버 내림
  2. visual/main.py keyframes
  3. Qwen3.5-122B 서버 (serve_vlm.sh, llama.cpp) → visual/main.py claims → 서버 내림
  4. gpt-oss-120b 서버                            → alignment/main.py  → 서버 내림
"""
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INPUT_PATH = ROOT / "data"

# ── conda env (setup.sh가 만든 이름) ───────────────────
AUDIO_ENV = "truead"
VISUAL_ENV = "truead-visual"
ALIGN_ENV = "truead"

# ── GPU 선택: 단계별 최소 여유 메모리(GB). 이보다 적으면 실행 안 함 ──
MIN_FREE_GB = {"llm": 24, "audio": 8, "keyframe": 8, "vlm": 18}
GPU_MARGIN_GB = 2          # 여유 메모리에서 이만큼은 남겨 둠
SERVER_READY_TIMEOUT = 1800   # 초. NAS에서 가중치 읽는 데 수 분 걸림

# ── gpt-oss-120b (vLLM) ───────────────────────────────
LLM_WEIGHTS_GB = 66        # GPU에 전부 올릴 때 가중치. 10-06 실측: 24GiB 오프로딩 상태에서 41.9 GiB → 합 약 66
LLM_KV_GB = 8              # KV 캐시 몫. 여유가 이만큼 안 되면 그 차이를 CPU로 오프로딩
LLM_PORT = 8000
LLM_BASE_URL = f"http://localhost:{LLM_PORT}/v1"

# ── Qwen3.5-122B-A10B (llama.cpp, GGUF) ───────────────
VLM_BASE_GB = 14           # 전문가를 전부 CPU에 뒀을 때 GPU 점유 (10-12 실측: 비전 인코더·attention·KV·버퍼)
VLM_EXPERT_LAYER_GB = 1.25 # 전문가 한 층을 GPU에 올릴 때 (약 60GB / 48층)
VLM_N_LAYERS = 48
VLM_THREADS = 16
VLM_PORT = 8002
VLM_BASE_URL = f"http://localhost:{VLM_PORT}/v1"


# ── GPU ───────────────────────────────────────────────
def gpu_free_gb() -> list[tuple[int, float, float]]:
    """[(index, free_gb, total_gb), ...]"""
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,memory.used,memory.total", "--format=csv,noheader,nounits"], text=True)
    gpus = []
    for line in out.strip().splitlines():
        i, used, total = (float(x) for x in line.split(","))
        gpus.append((int(i), (total - used) / 1024, total / 1024))
    return gpus


def pick_gpu(stage: str) -> tuple[int, float, float]:
    gpus = gpu_free_gb()
    idx, free, total = max(gpus, key=lambda g: g[1])
    table = ", ".join(f"GPU{i} {f:.1f}/{t:.0f}GB" for i, f, t in gpus)
    if free < MIN_FREE_GB[stage]:
        sys.exit(f"[{stage}] 여유 GPU 없음 (최소 {MIN_FREE_GB[stage]}GB): {table}")
    print(f"[{stage}] GPU{idx} 선택 (여유 {free:.1f}GB)  — {table}", flush=True)
    return idx, free, total


def llm_offload(free: float, total: float) -> tuple[float, float]:
    """(gpu_memory_utilization, cpu_offload_gb). 가중치+KV가 여유를 넘는 만큼만 CPU로."""
    budget = free - GPU_MARGIN_GB
    return round(budget / total, 3), round(max(0.0, LLM_WEIGHTS_GB + LLM_KV_GB - budget), 1)


def vlm_n_cpu_moe(free: float) -> int:
    """GPU에 올릴 수 있는 전문가 층 수를 빼고, 나머지 층 수를 CPU에 둔다."""
    on_gpu = int((free - GPU_MARGIN_GB - VLM_BASE_GB) // VLM_EXPERT_LAYER_GB)
    return VLM_N_LAYERS - max(0, min(VLM_N_LAYERS, on_gpu))


# ── 실행 ──────────────────────────────────────────────
def env_python(name: str) -> str:
    envs = json.loads(subprocess.check_output(["conda", "env", "list", "--json"]))["envs"]
    for p in envs:
        if Path(p).name == name:
            return str(Path(p) / "bin" / "python")
    sys.exit(f"conda env 없음: {name}  → bash setup.sh")


def run(env: str, script: str, args: list[str], stage: str) -> None:
    gpu, free, _ = pick_gpu(stage)
    python = env_python(env)
    cmd = [python, str(HERE / script), *args]
    print(f"$ CUDA_VISIBLE_DEVICES={gpu} [{env}] python {script} {' '.join(args)}", flush=True)
    subprocess.run(
        cmd,
        cwd=HERE / Path(script).parent,
        env={**os.environ,
             "PATH": f"{Path(python).parent}{os.pathsep}{os.environ.get('PATH', '')}",   # conda activate와 같은 효과 (env의 ffmpeg 등)
             "CUDA_VISIBLE_DEVICES": str(gpu),
             "LLM_BASE_URL": LLM_BASE_URL, "VLM_BASE_URL": VLM_BASE_URL},
        check=True,
    )


def ready(base_url: str) -> bool:
    try:
        urllib.request.urlopen(f"{base_url}/models", timeout=2)
        return True
    except Exception:
        return False


def start_server(name: str, script: str, base_url: str, env: dict) -> subprocess.Popen | None:
    if ready(base_url):
        print(f"{name} 서버가 이미 떠 있음 ({base_url}) → 그대로 쓰고 내리지 않음")
        return None
    print(f"{name} 서버 시작: " + " ".join(f"{k}={v}" for k, v in env.items()), flush=True)
    proc = subprocess.Popen(["bash", str(HERE / script)], env={**os.environ, **env}, start_new_session=True)
    t0 = time.time()
    while not ready(base_url):
        if proc.poll() is not None:
            sys.exit(f"{name} 서버가 종료됨 (exit {proc.returncode})")
        if time.time() - t0 > SERVER_READY_TIMEOUT:
            stop_server(name, proc)
            sys.exit(f"{name} 서버가 {SERVER_READY_TIMEOUT}초 안에 안 뜸")
        time.sleep(5)
    print(f"{name} 서버 준비됨 ({time.time() - t0:.0f}초)", flush=True)
    return proc


def stop_server(name: str, proc: subprocess.Popen | None) -> None:
    if proc is None:
        return
    print(f"{name} 서버 종료", flush=True)
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)


def start_llm() -> subprocess.Popen | None:
    if ready(LLM_BASE_URL):
        return start_server("LLM", "serve_llm.sh", LLM_BASE_URL, {})
    gpu, free, total = pick_gpu("llm")
    util, offload = llm_offload(free, total)
    return start_server("LLM", "serve_llm.sh", LLM_BASE_URL,
                        {"GPUS": str(gpu), "PORT": str(LLM_PORT), "MEM_UTIL": str(util), "OFFLOAD_GB": str(offload)})


def start_vlm() -> subprocess.Popen | None:
    if ready(VLM_BASE_URL):
        return start_server("VLM", "serve_vlm.sh", VLM_BASE_URL, {})
    gpu, free, _ = pick_gpu("vlm")
    return start_server("VLM", "serve_vlm.sh", VLM_BASE_URL,
                        {"GPUS": str(gpu), "PORT": str(VLM_PORT), "N_CPU_MOE": str(vlm_n_cpu_moe(free)),
                         "THREADS": str(VLM_THREADS)})


def main():
    target = str((Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_PATH).resolve())
    llm = vlm = None
    try:
        llm = start_llm()
        run(AUDIO_ENV, "audio/main.py", [target], "audio")
        stop_server("LLM", llm); llm = None

        run(VISUAL_ENV, "visual/main.py", ["keyframes", target], "keyframe")

        vlm = start_vlm()
        run(VISUAL_ENV, "visual/main.py", ["claims", target], "audio")   # API 호출만. GPU 안 씀
        stop_server("VLM", vlm); vlm = None

        llm = start_llm()
        run(ALIGN_ENV, "alignment/main.py", [target], "audio")           # API 호출만. GPU 안 씀
    finally:
        stop_server("LLM", llm)
        stop_server("VLM", vlm)
    print(f"\n완료. 결과: {ROOT / 'data' / 'output'}")


if __name__ == "__main__":
    main()
