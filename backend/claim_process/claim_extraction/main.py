"""python main.py [영상.mp4 | 폴더]   # 기본 data/ 전부

전체 파이프라인을 한 번에 돌린다. 단계마다 conda env가 달라서 subprocess로 실행한다.
모델 하나당 GPU 한 장. 단계마다 그 시점에 여유 메모리가 가장 큰 카드를 고르고(서버 카드 제외),
MIN_FREE_GB보다 적으면 실행하지 않는다. 큰 모델은 부족한 만큼만 전문가 층을 CPU에 둔다.

  입력 준비: AV1이면 H.264로 변환(data/converted/)
  gpt-oss-120b 서버 (serve_llm.sh) 기동·준비 대기
  scene ON      → Qwen3.5-122B 서버 (serve_vlm.sh) 기동 시작만
  [1] scene|text ON → visual/main.py keyframes --select … [--ocr]
  [2] 병렬: audio ON → audio/main.py [--ocr-context]
            text ON  → visual/main.py text
            scene ON → VLM 준비 대기 → visual/main.py scene → (띄운 경우) 서버 내림
  [3] alignment/main.py --branches …

scene(VLM)은 FRAME_SELECT 중 하나라도 켜져 있으면 ON. 화면 글자 Claim과 시각 Claim을 VLM이 함께 낸다.
  gpt-oss-120b 서버 내림 (띄운 경우)

서버가 이미 떠 있으면 그대로 쓰고 내리지 않는다. 그 서버의 카드 번호는 SERVER_GPUS=0,1 처럼 넘긴다
(이 컨테이너의 nvidia-smi는 프로세스 이름을 보여 주지 않음).
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_PATH = ROOT / "data"
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}     # audio·visual 입력 공통 확장자

# ── 브랜치 on/off. 끈 브랜치는 모델·서버·결과 파일 없음 ──
BRANCHES = {"audio": True, "text": False}       # text = OCR 글자 → gpt-oss Claim 추출. 기본 OFF: 화면 글자 Claim은 VLM(scene)이 낸다. 되돌리려면 True
FRAME_SELECT = {"change": False, "text": True}  # VLM 입력 프레임 선택기. change = V-JEPA 2 변화 프레임, text = OCR 글자 구간 대표 표기 프레임. 하나라도 True면 VLM(scene) 동작

ASR_CONTEXT_FROM_OCR = False    # True면 OCR을 돌린 실행에서 화면 글자를 ASR context로. 말하지 않은 화면 글자가 대본에 섞여 끔

# ── conda env (setup.sh가 만든 이름) ───────────────────
AUDIO_ENV = "truead"
VISUAL_ENV = "truead-visual"
ALIGN_ENV = "truead"

# ── GPU 선택: 단계별 최소 여유 메모리(GB). 이보다 적으면 실행 안 함 ──
MIN_FREE_GB = {"llm": 24, "audio": 8, "keyframe": 8, "vlm": 18}
GPU_MARGIN_GB = 2          # 여유 메모리에서 이만큼은 남겨 둠
SERVER_READY_TIMEOUT = 1800   # 초. NAS에서 가중치 읽는 데 수 분 걸림

# ── gpt-oss-120b (llama.cpp, GGUF UD-Q4_K_XL 63GB) ────
LLM_BASE_GB = 8            # 전문가를 전부 CPU에 뒀을 때 GPU 점유 (추정. 첫 기동 nvidia-smi로 보정)
LLM_EXPERT_LAYER_GB = 1.7  # 전문가 한 층을 GPU에 올릴 때 (추정 61GB / 36층)
LLM_N_LAYERS = 36
LLM_THREADS = 16
LLM_CTX = 32768
LLM_PORT = 8000
LLM_BASE_URL = f"http://localhost:{LLM_PORT}/v1"

# ── Qwen3.5-122B-A10B (llama.cpp, GGUF) ───────────────
VLM_BASE_GB = 8.9          # 전문가를 전부 CPU에 뒀을 때(N_CPU_MOE=48) 서버 프로세스 GPU 점유. 실측 9110MiB(이미지 1024토큰·-ub 2048, 6요청 최고치)
VLM_EXPERT_LAYER_GB = 1.37 # 전문가 한 층을 GPU에 올릴 때. 실측(N_CPU_MOE=23에서 43.1GiB − BASE 8.9) ÷ 25층. 1.25면 N=19에서 기동 OOM
VLM_N_LAYERS = 48
VLM_THREADS = 16
VLM_IMAGE_MAX_TOKENS = 1024  # 이미지 한 장 최대 토큰 (--image-max-tokens)
VLM_UBATCH = 2048          # 물리 배치 (-ub)
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


def pick_gpu(stage: str, exclude: set[int]) -> tuple[int, float, float]:
    gpus = gpu_free_gb()
    idx, free, total = max((g for g in gpus if g[0] not in exclude), key=lambda g: g[1])
    table = ", ".join(f"GPU{i} {f:.1f}/{t:.0f}GB" for i, f, t in gpus) + f", 제외 {sorted(exclude)}"
    if free < MIN_FREE_GB[stage]:
        sys.exit(f"[{stage}] 여유 GPU 없음 (최소 {MIN_FREE_GB[stage]}GB): {table}")
    print(f"[{stage}] GPU{idx} 선택 (여유 {free:.1f}GB)  — {table}", flush=True)
    return idx, free, total


def server_gpus() -> set[int]:
    """이미 떠 있는 서버(재사용)의 카드. nvidia-smi가 프로세스 이름을 못 보여 줘서 환경변수로 받는다."""
    return {int(x) for x in os.environ.get("SERVER_GPUS", "").split(",") if x.strip()}


def llm_n_cpu_moe(free: float) -> int:
    """GPU에 올릴 수 있는 전문가 층 수를 빼고, 나머지 층 수를 CPU에 둔다."""
    on_gpu = int((free - GPU_MARGIN_GB - LLM_BASE_GB) // LLM_EXPERT_LAYER_GB)
    return LLM_N_LAYERS - max(0, min(LLM_N_LAYERS, on_gpu))


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


def prepare_inputs(target: Path) -> list[str]:
    """AV1만 data/converted/<stem>.mp4로 변환(매번). 나머지는 원본 경로."""
    bin_dir = Path(env_python(AUDIO_ENV)).parent
    videos = [target] if target.is_file() else sorted(p for p in target.iterdir() if p.suffix.lower() in VIDEO_EXTS)
    out = []
    for v in videos:
        codec = subprocess.check_output(
            [str(bin_dir / "ffprobe"), "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(v)], text=True).strip()
        if codec == "av1":
            dst = ROOT / "data" / "converted" / f"{v.stem}.mp4"
            dst.parent.mkdir(parents=True, exist_ok=True)
            print(f"AV1 → H.264 변환: {v.name}", flush=True)
            subprocess.run([str(bin_dir / "ffmpeg"), "-y", "-loglevel", "error", "-i", str(v),
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "copy", str(dst)],
                           check=True)
            v = dst
        out.append(str(v))
    return out


def run(env: str, script: str, args: list[str], stage: str | None = None, exclude: set[int] = frozenset(),
        label: str = "") -> None:
    """stage가 있으면 그 단계 몫으로 GPU 한 장을 고른다. None이면 서버 API만 부르는 단계.
    label이 있으면 출력 줄마다 [label]을 붙인다(병렬 실행)."""
    python = env_python(env)
    extra = {}
    if stage:
        extra["CUDA_VISIBLE_DEVICES"] = str(pick_gpu(stage, exclude)[0])
    prefix = f"[{label}] " if label else ""
    print(f"{prefix}$ {''.join(f'{k}={v} ' for k, v in extra.items())}[{env}] python {script} {' '.join(args)}", flush=True)
    proc = subprocess.Popen(
        [python, "-u", str(HERE / script), *args],
        cwd=HERE / Path(script).parent,
        env={**os.environ,
             "PATH": f"{Path(python).parent}{os.pathsep}{os.environ.get('PATH', '')}",   # conda activate와 같은 효과 (env의 ffmpeg 등)
             "LLM_BASE_URL": LLM_BASE_URL, "VLM_BASE_URL": VLM_BASE_URL, **extra},
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    for line in proc.stdout:
        print(prefix + line, end="", flush=True)
    if proc.wait() != 0:
        raise subprocess.CalledProcessError(proc.returncode, script)


def run_parallel(lanes: dict[str, callable]) -> None:
    """lane마다 스레드 하나. 하나라도 실패하면 나머지가 끝난 뒤 종료."""
    failed = []

    def body(name, fn):
        try:
            fn()
        except BaseException as e:
            print(f"[{name}] 실패: {e}", flush=True)
            failed.append(name)

    threads = [threading.Thread(target=body, args=(n, fn)) for n, fn in lanes.items()]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if failed:
        sys.exit(f"실패: {failed}")


def ready(base_url: str) -> bool:
    try:
        urllib.request.urlopen(f"{base_url}/models", timeout=2)
        return True
    except Exception:
        return False


def spawn_server(name: str, script: str, env: dict) -> subprocess.Popen:
    print(f"{name} 서버 시작: " + " ".join(f"{k}={v}" for k, v in env.items()), flush=True)
    return subprocess.Popen(["bash", str(HERE / script)], env={**os.environ, **env}, start_new_session=True)


def wait_ready(name: str, proc: subprocess.Popen | None, base_url: str) -> None:
    if proc is None:
        return
    t0 = time.time()
    while not ready(base_url):
        if proc.poll() is not None:
            sys.exit(f"{name} 서버가 종료됨 (exit {proc.returncode})")
        if time.time() - t0 > SERVER_READY_TIMEOUT:
            sys.exit(f"{name} 서버가 {SERVER_READY_TIMEOUT}초 안에 안 뜸")
        time.sleep(5)
    print(f"{name} 서버 준비됨 (대기 {time.time() - t0:.0f}초)", flush=True)


def stop_server(name: str, proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    print(f"{name} 서버 종료", flush=True)
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)


def start_llm(exclude: set[int]) -> subprocess.Popen | None:
    """이미 떠 있으면 None. 아니면 카드를 골라 띄우고 exclude에 넣는다."""
    if ready(LLM_BASE_URL):
        print(f"LLM 서버가 이미 떠 있음 ({LLM_BASE_URL}) → 그대로 쓰고 내리지 않음", flush=True)
        exclude |= server_gpus()
        return None
    gpu, free, _ = pick_gpu("llm", exclude)
    exclude.add(gpu)
    return spawn_server("LLM", "serve_llm.sh",
                        {"GPUS": str(gpu), "PORT": str(LLM_PORT), "N_CPU_MOE": str(llm_n_cpu_moe(free)),
                         "THREADS": str(LLM_THREADS), "CTX": str(LLM_CTX)})


def start_vlm(exclude: set[int]) -> subprocess.Popen | None:
    if ready(VLM_BASE_URL):
        print(f"VLM 서버가 이미 떠 있음 ({VLM_BASE_URL}) → 그대로 쓰고 내리지 않음", flush=True)
        exclude |= server_gpus()
        return None
    gpu, free, _ = pick_gpu("vlm", exclude)
    exclude.add(gpu)
    return spawn_server("VLM", "serve_vlm.sh",
                        {"GPUS": str(gpu), "PORT": str(VLM_PORT), "N_CPU_MOE": str(vlm_n_cpu_moe(free)),
                         "THREADS": str(VLM_THREADS), "IMAGE_MAX_TOKENS": str(VLM_IMAGE_MAX_TOKENS),
                         "UBATCH": str(VLM_UBATCH)})


def main():
    select = [k for k, v in FRAME_SELECT.items() if v]
    scene_on = bool(select)
    ocr_on = FRAME_SELECT["text"] or BRANCHES["text"]
    on = [b for b, v in BRANCHES.items() if v] + (["scene"] if scene_on else [])
    if not on:
        sys.exit("브랜치가 모두 꺼져 있음")
    target = (Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_PATH).resolve()
    if not (target.is_file() or any(p.suffix.lower() in VIDEO_EXTS for p in target.iterdir())):
        sys.exit(f"입력 영상이 없음: {target}")
    videos = prepare_inputs(target)
    exclude: set[int] = set()
    llm = vlm = None
    try:
        llm = start_llm(exclude)
        wait_ready("LLM", llm, LLM_BASE_URL)
        if "scene" in on:
            vlm = start_vlm(exclude)
        if scene_on or ocr_on:
            ocr = ["--ocr"] if BRANCHES["text"] else []
            run(VISUAL_ENV, "visual/main.py", ["keyframes", *videos, "--select", ",".join(select), *ocr],
                "keyframe", exclude)

        lanes = {}
        if "audio" in on:
            ctx = ["--ocr-context"] if ASR_CONTEXT_FROM_OCR and ocr_on else []
            lanes["audio"] = lambda: run(AUDIO_ENV, "audio/main.py", [*videos, *ctx], "audio", exclude, "audio")
        if "text" in on:
            lanes["text"] = lambda: run(VISUAL_ENV, "visual/main.py", ["text", *videos], label="text")
        if "scene" in on:
            def scene():
                wait_ready("VLM", vlm, VLM_BASE_URL)
                run(VISUAL_ENV, "visual/main.py", ["scene", *videos], label="scene")
                stop_server("VLM", vlm)
            lanes["scene"] = scene
        run_parallel(lanes)

        run(ALIGN_ENV, "alignment/main.py", [*videos, "--branches", ",".join(on)])
    finally:
        stop_server("LLM", llm)
        stop_server("VLM", vlm)
    print(f"\n완료. 결과: {ROOT / 'data' / 'output'}")


if __name__ == "__main__":
    main()
