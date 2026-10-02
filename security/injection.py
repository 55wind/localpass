"""악성 프롬프트(프롬프트 인젝션) 1차 규칙 탐지.

외부 블로그·리뷰는 '신뢰할 수 없는 입력'으로 취급한다.
- block: 명백한 지시 탈취 시도 → LLM에 아예 전달하지 않음
- suspicious: 의심 신호 → Qwen 보안 분석(2차)에서 문맥으로 재판단
또한 Qwen의 채팅 템플릿 토큰(<|im_start|> 등)은 데이터와 명령의 경계를 깨뜨릴 수 있으므로 무력화한다.
"""
import re
from dataclasses import dataclass, field

_BLOCK = [
    r"(이전|위의?|앞의?|기존|모든)\s*(지시|명령|지침|규칙|프롬프트)(사항)?[을를은는]?\s*(모두\s*)?(무시|잊어|따르지)",
    r"시스템\s*프롬프트[를을]?\s*(출력|보여|공개|알려|노출)",
    r"ignore\s+(all\s+|any\s+)?(the\s+)?(previous|prior|above|earlier)\s+(instructions|prompts?|rules)",
    r"disregard\s+(all\s+|the\s+)?(previous|prior|above)\s+",
    r"(reveal|print|show|output)\s+(your\s+|the\s+)?system\s+prompt",
    r"(너는|당신은)\s*이제(부터)?\s*.{0,20}(이다|입니다|역할)",
    r"you\s+are\s+now\s+(a|an|in)\s+",
    r"(developer|dan|jailbreak)\s*mode",
    r"(평가|판정|판단|점수)[를을]?\s*(무조건|반드시)?\s*(신뢰|정상|만점|100)",
    r"(is_sponsored|trust_score|verdict)\s*[:=]",
]

_SUSPICIOUS = [
    r"(지시|명령)[를을]?\s*(따르|수행|실행)",
    r"(AI|에이아이|인공지능|LLM|GPT|챗봇|모델)\s*(에게|야|는|님)",
    r"\b(system|assistant|user)\s*:",
    r"\[\s*(INST|SYS)\s*\]",
    r"###\s*(instruction|system)",
    r"(출력|응답)\s*형식[을를]?\s*(바꿔|변경)",
    r"(번역|요약)\s*하지\s*말",
]

# Qwen(ChatML)·Llama 계열 특수 토큰 — 데이터 안에 있으면 역할 경계를 위조할 수 있다.
_CONTROL_TOKENS = re.compile(r"<\|[^|>]{1,30}\|>|</?s>|\[/?INST\]|<<SYS>>|<</SYS>>", re.I)

_BLOCK_RE = [re.compile(p, re.I) for p in _BLOCK]
_SUSPICIOUS_RE = [re.compile(p, re.I) for p in _SUSPICIOUS]


@dataclass
class InjectionResult:
    level: str  # "normal" | "suspicious" | "block"
    matches: list[str] = field(default_factory=list)
    text: str = ""  # 제어 토큰을 제거한 텍스트


def strip_control_tokens(text: str) -> str:
    return _CONTROL_TOKENS.sub(" ", text)


def scan_injection(text: str) -> InjectionResult:
    cleaned, n_tokens = _CONTROL_TOKENS.subn(" ", text)
    matches = [m.group(0) for r in _BLOCK_RE if (m := r.search(cleaned))]
    if matches:
        return InjectionResult("block", matches, cleaned)
    matches = [m.group(0) for r in _SUSPICIOUS_RE if (m := r.search(cleaned))]
    if n_tokens:
        matches.append("special-token")
    return InjectionResult("suspicious" if matches else "normal", matches, cleaned)
