"""Qwen2.5-7B-Instruct 호출 (OpenAI 호환 API — 로컬 Ollama, HF Router, DashScope 등 공통).

보안 원칙
- 외부 리뷰는 system 프롬프트에 절대 넣지 않고, user 메시지 안에서 <review> 태그로 감싼 '데이터'로만 전달한다.
- 모델은 정해진 JSON 스키마로만 답하게 강제한다 (도구·권한 없음).
"""
import json
import logging
import threading
import time
from typing import TypeVar

import requests
from pydantic import BaseModel, ValidationError

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_SCALEDOWN_SEC, LLM_TIMEOUT, LLM_WAKE_TIMEOUT

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMUnavailable(Exception):
    pass


class LLMInvalidOutput(LLMUnavailable):
    """모델은 응답했지만 스키마를 지키지 못함 (출력이 잘리거나 반복 생성)."""


def _post(payload: dict) -> requests.Response:
    for attempt in range(2):
        try:
            resp = requests.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                json=payload,
                timeout=LLM_TIMEOUT,
            )
        except requests.RequestException as e:
            raise LLMUnavailable(str(e)) from e
        # Modal은 GPU 컨테이너가 켜지는 동안 503을 돌려준다 → 준비될 때까지 기다렸다 한 번 더
        if resp.status_code == 503 and not is_local() and attempt == 0:
            log.info("원격 GPU 준비 중(503) → 켜질 때까지 대기")
            if not _wait_until_warm():
                break
            continue
        return resp
    raise LLMUnavailable("원격 GPU가 준비되지 않음")


def chat_json(system: str, user: str, schema: type[T], max_tokens: int = 600) -> T:
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema(), "strict": True},
        },
    }
    resp = _post(payload)
    if resp.status_code == 400:
        # json_schema 미지원 제공자 → json_object 모드로 재시도 (스키마는 프롬프트로 안내)
        payload["response_format"] = {"type": "json_object"}
        payload["messages"][0]["content"] += "\n\nJSON 스키마:\n" + json.dumps(schema.model_json_schema(), ensure_ascii=False)
        resp = _post(payload)
    if resp.status_code >= 400:
        raise LLMUnavailable(f"{resp.status_code} {resp.text[:200]}")

    _mark_ok()  # 방금 응답했으니 원격 GPU는 켜져 있다
    content = resp.json()["choices"][0]["message"]["content"]
    try:
        return schema.model_validate_json(content)
    except ValidationError as e:
        log.warning("LLM 출력 스키마 불일치: %s", content[:300])
        raise LLMInvalidOutput("invalid structured output") from e


def is_local() -> bool:
    return any(h in LLM_BASE_URL for h in ("127.0.0.1", "localhost"))


def is_online() -> bool:
    """로컬 Ollama는 바로 확인한다. 원격(Modal 등)은 꺼져 있다 켜지는 데 1~2분이 걸려
    짧은 확인으로는 '꺼짐'으로 오판하므로 설정돼 있으면 켜져 있다고 보고, 실패하면 호출 단계에서 규칙 검사로 폴백한다."""
    if not is_local():
        return True
    try:
        r = requests.get(f"{LLM_BASE_URL}/models", headers={"Authorization": f"Bearer {LLM_API_KEY}"}, timeout=3)
        return r.ok
    except requests.RequestException:
        return False


# ── 원격 GPU(Modal) 콜드 스타트 상태 ─────────────────────────────────────
# Modal은 요청이 없으면 LLM_SCALEDOWN_SEC 뒤에 꺼진다(요금 0). 사이트에 사람이 들어왔을 때만 깨우고,
# 켜지는 동안의 상태를 화면에 보여준다. 마지막 성공 호출 시각으로 아직 켜져 있을지 추정한다.
_warm = {"state": "cold", "started": 0.0, "last_ok": 0.0}
_warm_lock = threading.Lock()


def _mark_ok() -> None:
    _warm.update(state="ready", last_ok=time.time())


def _health_url() -> str:
    base = LLM_BASE_URL[:-3] if LLM_BASE_URL.endswith("/v1") else LLM_BASE_URL
    return f"{base}/health"


def _wake() -> None:
    """GPU 컨테이너가 뜰 때까지 /health 를 몇 초마다 확인한다 (켜지는 동안은 503).
    준비되면 확인을 멈춘다 — 계속 두드리면 Modal이 꺼지지 않아 요금이 나간다."""
    deadline = _warm["started"] + LLM_WAKE_TIMEOUT
    while time.time() < deadline:
        try:
            if requests.get(_health_url(), timeout=30).status_code == 200:
                _mark_ok()
                log.info("원격 LLM 준비 완료 (%.0f초)", time.time() - _warm["started"])
                return
        except requests.RequestException:
            pass
        time.sleep(4)
    _warm["state"] = "offline"
    log.warning("원격 LLM이 %.0f초 안에 켜지지 않음", LLM_WAKE_TIMEOUT)


def _wait_until_warm() -> bool:
    with _warm_lock:
        if _warm["state"] == "ready":  # 켜져 있다고 추정했는데 503 → 그새 꺼졌다
            _warm["state"] = "cold"
    warm_status(wake=True)
    deadline = time.time() + LLM_WAKE_TIMEOUT
    while time.time() < deadline:
        if _warm["state"] == "ready":
            return True
        if _warm["state"] == "offline":
            return False
        time.sleep(2)
    return False


def warm_status(wake: bool = True) -> dict:
    """{'remote', 'state': ready|starting|cold|offline, 'elapsed'} — wake=True면 꺼져 있을 때 켠다."""
    if is_local():
        return {"remote": False, "state": "ready", "elapsed": 0}
    with _warm_lock:
        now = time.time()
        if _warm["state"] == "ready" and now - _warm["last_ok"] > LLM_SCALEDOWN_SEC - 10:
            _warm["state"] = "cold"  # 그동안 아무도 안 써서 Modal이 꺼졌을 것
        if wake and _warm["state"] in ("cold", "offline"):
            _warm.update(state="starting", started=now)
            threading.Thread(target=_wake, daemon=True).start()
        elapsed = int(now - _warm["started"]) if _warm["state"] == "starting" else 0
        return {"remote": True, "state": _warm["state"], "elapsed": elapsed, "scaledown": LLM_SCALEDOWN_SEC}
