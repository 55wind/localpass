"""Qwen2.5-7B-Instruct 호출 (OpenAI 호환 API — 로컬 Ollama, HF Router, DashScope 등 공통).

보안 원칙
- 외부 리뷰는 system 프롬프트에 절대 넣지 않고, user 메시지 안에서 <review> 태그로 감싼 '데이터'로만 전달한다.
- 모델은 정해진 JSON 스키마로만 답하게 강제한다 (도구·권한 없음).
"""
import json
import logging
from typing import TypeVar

import requests
from pydantic import BaseModel, ValidationError

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMUnavailable(Exception):
    pass


class LLMInvalidOutput(LLMUnavailable):
    """모델은 응답했지만 스키마를 지키지 못함 (출력이 잘리거나 반복 생성)."""


def _post(payload: dict) -> requests.Response:
    try:
        return requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json=payload,
            timeout=LLM_TIMEOUT,
        )
    except requests.RequestException as e:
        raise LLMUnavailable(str(e)) from e


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

    content = resp.json()["choices"][0]["message"]["content"]
    try:
        return schema.model_validate_json(content)
    except ValidationError as e:
        log.warning("LLM 출력 스키마 불일치: %s", content[:300])
        raise LLMInvalidOutput("invalid structured output") from e


def is_online() -> bool:
    try:
        r = requests.get(f"{LLM_BASE_URL}/models", headers={"Authorization": f"Bearer {LLM_API_KEY}"}, timeout=3)
        return r.ok
    except requests.RequestException:
        return False
