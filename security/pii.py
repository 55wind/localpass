"""개인정보 사전 필터링 — AI 분석 전에 전화번호·이메일 등을 비식별화한다.

수집한 블로그 원문은 이 단계를 거친 텍스트만 LLM·GPTZero·화면으로 넘어간다.
"""
import re
from dataclasses import dataclass, field

# 순서가 중요하다: 긴 패턴(주민번호·카드번호)을 먼저 지워야 전화번호 패턴에 잘못 걸리지 않는다.
_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("rrn", re.compile(r"(?<!\d)\d{6}\s*-\s*[1-4]\d{6}(?!\d)")),
    ("card", re.compile(r"(?<!\d)\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}(?!\d)")),
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("phone", re.compile(
        r"(?<!\d)(?:\+82[\s-]?|0)(?:1[016789]|2|[3-6][1-5]|70)[\s.-]?\d{3,4}[\s.-]?\d{4}(?!\d)"
    )),
    ("account", re.compile(
        r"(?:계좌|입금|송금)\s*[:：]?\s*(?:[가-힣A-Za-z]+\s*)?\d{2,6}-\d{2,6}-\d{2,8}(?:-\d{1,4})?"
    )),
    ("kakao", re.compile(r"(?:카톡|카카오톡|kakao)\s*(?:id|ID|아이디)?\s*[:：]\s*[\w.-]{3,}", re.I)),
]

MASKS = {
    "rrn": "[주민번호]",
    "card": "[카드번호]",
    "email": "[이메일]",
    "phone": "[전화번호]",
    "account": "[계좌정보]",
    "kakao": "[메신저ID]",
}


@dataclass
class PiiResult:
    text: str
    found: dict[str, int] = field(default_factory=dict)

    @property
    def count(self) -> int:
        return sum(self.found.values())


def mask_pii(text: str) -> PiiResult:
    found: dict[str, int] = {}
    for kind, pattern in _PATTERNS:
        text, n = pattern.subn(MASKS[kind], text)
        if n:
            found[kind] = n
    return PiiResult(text=text, found=found)
