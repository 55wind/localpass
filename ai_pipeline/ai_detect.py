"""AI 작성 여부 판별 — 무료 로컬 판별기(기본) 또는 GPTZero API.

- 원문(한국어, 개인정보 마스킹 후)을 그대로 넣는다. 번역본을 넣으면 정확도가 떨어진다.
- 실패해도 재시도하지 않고 None(판별 불가)으로 폴백한다.
- 너무 짧은 글은 판별 신뢰도가 낮아 판별하지 않는다.
"""
import logging

import requests

import cache
from ai_pipeline import local_detector, remote
from config import AI_DETECTOR, DETECTOR_MODEL, DETECTOR_URL, GPTZERO_API_KEY, LLM_API_KEY, LLM_WAKE_TIMEOUT

log = logging.getLogger(__name__)

GPTZERO_ENDPOINT = "https://api.gptzero.me/v2/predict/text"
MIN_CHARS = {"gptzero": 120, "local": 60, "remote": 60}


def backend() -> str:
    """현재 사용하는 판별기: 'local' | 'gptzero' | 'off'"""
    if AI_DETECTOR == "gptzero" and GPTZERO_API_KEY:
        return "gptzero"
    if AI_DETECTOR == "remote" and DETECTOR_URL:
        return "remote"
    if AI_DETECTOR == "local" and local_detector.available():
        return "local"
    return "off"


def health_url() -> str | None:
    return f"{DETECTOR_URL}/health" if backend() == "remote" else None


def enabled() -> bool:
    return backend() != "off"


def _gptzero(text: str) -> float | None:
    try:
        resp = requests.post(
            GPTZERO_ENDPOINT,
            headers={"x-api-key": GPTZERO_API_KEY, "Content-Type": "application/json"},
            json={"document": text, "multilingual": True},
            timeout=30,
        )
        resp.raise_for_status()
        doc = (resp.json().get("documents") or [{}])[0]
    except (requests.RequestException, ValueError) as e:
        log.warning("GPTZero 호출 실패: %s", e)
        return None
    probs = doc.get("class_probabilities") or {}
    if "ai" in probs:
        return float(probs["ai"]) + 0.5 * float(probs.get("mixed", 0))  # 혼합 문서는 절반만 AI로
    return float(doc["completely_generated_prob"]) if "completely_generated_prob" in doc else None


def _local(text: str) -> float | None:
    try:
        return local_detector.ai_probability(text)
    except Exception as e:  # 모델 로드 실패·메모리 부족 등 — 판별 불가로 처리
        log.warning("로컬 AI 판별 실패: %s", e)
        return None


def _remote(text: str) -> float | None:
    """Modal에 올린 같은 판별기(deploy/modal_detector.py)에 점수를 묻고, 확률 변환은 여기서 한다."""
    for attempt in range(2):
        try:
            resp = requests.post(f"{DETECTOR_URL}/discrepancy", json={"text": text[:5000]},
                                 headers={"Authorization": f"Bearer {LLM_API_KEY}"}, timeout=LLM_WAKE_TIMEOUT)
        except requests.RequestException as e:
            log.warning("원격 AI 판별 실패: %s", e)
            return None
        if resp.status_code in (502, 503) and attempt == 0 and remote.wait_ready(f"{DETECTOR_URL}/health", LLM_WAKE_TIMEOUT):
            continue
        if not resp.ok:
            log.warning("원격 AI 판별 응답 오류: %s %s", resp.status_code, resp.text[:120])
            return None
        return local_detector.to_probability(resp.json()["score"], len(text))
    return None


def check_ai_written(text: str, cache_key: str) -> tuple[float, str] | None:
    """(AI 작성 확률, 판별기 이름) 또는 None."""
    name = backend()
    if name == "off" or len(text) < MIN_CHARS[name]:
        return None
    source = "gptzero" if name == "gptzero" else "local"  # remote도 같은 Fast-DetectGPT 판별기
    ck = [cache_key, source, DETECTOR_MODEL if source == "local" else ""]
    hit = cache.get("ai_detect", ck)
    if hit is not None:
        return hit["ai"], source
    prob = {"gptzero": _gptzero, "local": _local, "remote": _remote}[name](text)
    if prob is None:
        return None
    cache.put("ai_detect", ck, {"ai": prob})
    return prob, source
