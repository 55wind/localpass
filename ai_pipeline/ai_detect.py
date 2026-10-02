"""GPTZero API — AI 작성 여부 판별.

- 원문(한국어, 개인정보 마스킹 후)을 그대로 보낸다. 번역본을 보내면 정확도가 떨어진다.
- 종량제라 실패해도 재시도하지 않고 None(판별 불가)으로 폴백한다.
- 너무 짧은 글은 판별 신뢰도가 낮아 호출하지 않는다.
"""
import logging

import requests

import cache
from config import GPTZERO_API_KEY

log = logging.getLogger(__name__)

ENDPOINT = "https://api.gptzero.me/v2/predict/text"
MIN_CHARS = 120


def enabled() -> bool:
    return bool(GPTZERO_API_KEY)


def _extract_ai_prob(data: dict) -> float | None:
    doc = (data.get("documents") or [{}])[0]
    probs = doc.get("class_probabilities") or {}
    if "ai" in probs:
        # 혼합(mixed) 문서는 절반만 AI 작성으로 본다
        return float(probs["ai"]) + 0.5 * float(probs.get("mixed", 0))
    if "completely_generated_prob" in doc:
        return float(doc["completely_generated_prob"])
    return None


def check_ai_written(text: str, cache_key: str) -> float | None:
    if not enabled() or len(text) < MIN_CHARS:
        return None
    hit = cache.get("gptzero", cache_key)
    if hit is not None:
        return hit.get("ai")
    try:
        resp = requests.post(
            ENDPOINT,
            headers={"x-api-key": GPTZERO_API_KEY, "Content-Type": "application/json"},
            json={"document": text, "multilingual": True},
            timeout=30,
        )
        resp.raise_for_status()
        prob = _extract_ai_prob(resp.json())
    except (requests.RequestException, ValueError) as e:
        log.warning("GPTZero 호출 실패: %s", e)
        return None
    if prob is not None:
        cache.put("gptzero", cache_key, {"ai": prob})
    return prob
