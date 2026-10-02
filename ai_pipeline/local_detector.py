"""무료 로컬 AI 작성 판별기 — Fast-DetectGPT (Bao et al., ICLR 2024) 해석적 기준.

언어모델이 직접 쓴 글은 '모델이 가장 고를 법한 토큰'만 골라 쓰는 경향이 있다.
글의 실제 로그우도가 모델 분포의 기대값보다 얼마나 높은지를 표준화한 값(sampling discrepancy)이
클수록 AI가 썼을 가능성이 높다. 학습이 필요 없고, 한 번의 forward pass로 계산된다.

- 점수 모델: Qwen2.5-1.5B (한국어 토크나이저 지원, 약 3GB) — 외부 API·과금 없음
- 확률 변환: KatFish(ACL 2025, 한국어 사람/LLM 글 벤치마크)로 보정한 분포
  (scripts/calibrate_detector.py → data/detector_calibration.json)
"""
import json
import logging
import math
import os
import threading

from config import DETECTOR_MODEL, MODELS_DIR, ROOT

log = logging.getLogger(__name__)

CALIBRATION_PATH = ROOT / "data" / "detector_calibration.json"
SHORT_CHARS = 400          # 이보다 짧으면 '요약문' 보정값을 쓴다
MAX_TOKENS = 512

_lock = threading.Lock()
_state: dict = {}


def _load():
    if "model" in _state:
        return _state["model"], _state["tok"], _state["device"]
    os.environ.setdefault("HF_HOME", str(MODELS_DIR))  # C 드라이브 대신 프로젝트 폴더에 저장
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device, dtype = "cpu", torch.float32
    if torch.cuda.is_available():
        free, _ = torch.cuda.mem_get_info()
        if free > 4 * 1024 ** 3:  # Ollama(Qwen 7B)가 VRAM을 쓰고 있으면 CPU로
            device, dtype = "cuda", torch.bfloat16
    # .models/<모델명>/ 에 미리 받아 둔 파일이 있으면 그걸 쓰고, 없으면 Hugging Face에서 받는다
    local = MODELS_DIR / DETECTOR_MODEL.split("/")[-1]
    source = str(local) if (local / "config.json").exists() and (local / "model.safetensors").exists() else DETECTOR_MODEL
    log.info("로컬 AI 판별 모델 로드: %s (%s)", source, device)
    tok = AutoTokenizer.from_pretrained(source, cache_dir=MODELS_DIR)
    model = AutoModelForCausalLM.from_pretrained(source, dtype=dtype, cache_dir=MODELS_DIR).to(device).eval()
    _state.update(model=model, tok=tok, device=device)
    return model, tok, device


def discrepancy(text: str) -> float:
    """Fast-DetectGPT sampling discrepancy (점수 모델 = 참조 모델). 높을수록 AI 작성에 가깝다."""
    import torch

    with _lock:
        model, tok, device = _load()
        ids = tok(text, return_tensors="pt", truncation=True, max_length=MAX_TOKENS).input_ids.to(device)
        if ids.shape[1] < 8:
            raise ValueError("text too short")
        with torch.no_grad():
            logits = model(ids).logits[:, :-1].float()
    labels = ids[:, 1:]
    lprobs = torch.log_softmax(logits, dim=-1)
    probs = lprobs.exp()
    log_likelihood = lprobs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    mean_ref = (probs * lprobs).sum(-1)
    var_ref = (probs * lprobs.square()).sum(-1) - mean_ref.square()
    return ((log_likelihood.sum(-1) - mean_ref.sum(-1)) / var_ref.sum(-1).sqrt()).item()


def _calibration() -> dict | None:
    if "calib" not in _state:
        try:
            _state["calib"] = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _state["calib"] = None
    return _state["calib"]


def _normal_pdf(x: float, mu: float, sigma: float) -> float:
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def to_probability(score: float, n_chars: int) -> float:
    """보정 분포(사람/AI 각각 정규분포)로 사후확률 P(AI | score) 계산 — 사전확률은 반반."""
    calib = _calibration()
    if not calib:
        return 1 / (1 + math.exp(-(score - 1.0)))  # 보정 파일이 없을 때의 대략값
    c = calib["short" if n_chars < SHORT_CHARS else "long"]
    p_ai = _normal_pdf(score, c["ai"]["mu"], c["ai"]["sigma"])
    p_h = _normal_pdf(score, c["human"]["mu"], c["human"]["sigma"])
    return p_ai / (p_ai + p_h) if p_ai + p_h > 0 else (1.0 if score > c["threshold"] else 0.0)


def ai_probability(text: str) -> float:
    return to_probability(discrepancy(text), len(text))


def warmup() -> None:
    """서버 시작 시 백그라운드에서 모델을 올리고 한 번 돌려 둔다 (첫 로드·CUDA 초기화에 1~2분)."""
    try:
        discrepancy("성수동 카페에 다녀왔어요. 라떼가 고소하고 자리가 넓어서 좋았어요.")
        log.info("로컬 AI 판별 모델 준비 완료")
    except Exception as e:
        log.warning("로컬 AI 판별 모델 준비 실패: %s", e)


def available() -> bool:
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
        return True
    except ImportError:
        return False
