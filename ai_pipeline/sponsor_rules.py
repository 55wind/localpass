"""협찬·광고 표기 1차 규칙 탐지 (공정위 「추천·보증 등에 관한 표시·광고 심사지침」 표기 패턴)."""
import re

# 명시적 표기 — 하나라도 있으면 협찬으로 확정
_EXPLICIT = [
    r"협찬",
    r"제공\s*받아",
    r"제공\s*받(았|은|고)",
    r"지원\s*받아",
    r"원고료",
    r"소정의\s*(원고료|수수료|대가|금액|제품)",
    r"체험단",
    r"유료\s*광고",
    r"광고\s*(를\s*)?포함",
    r"#\s*광고",
    r"#\s*ad\b",
    r"업체\s*(로부터|에서)\s*.{0,20}(제공|지원|초대)",
    r"(무상|무료)\s*(으로|로)?\s*(제공|초대|지원)\s*받",
    r"파트너스\s*활동",
    r"서포터즈",
    r"sponsored",
]

# 약한 신호 — 단독으로 확정하지 않고 LLM 판단에 참고
_WEAK = [
    r"초대\s*받아",
    r"(할인|쿠폰)\s*코드",
    r"(링크|아래)\s*(를\s*)?(클릭|통해).{0,10}(구매|예약)",
    r"이벤트\s*진행\s*중",
    r"강력\s*추천",
    r"인생\s*(맛집|카페)",
]

# 자비 구매 표기 — 협찬이 아니라는 주장 (그대로 믿지는 않고 참고만)
_SELF_PAID = [r"내\s*돈\s*내\s*산", r"내돈내먹", r"직접\s*(결제|구매)"]

_EXPLICIT_RE = [re.compile(p, re.I) for p in _EXPLICIT]
_WEAK_RE = [re.compile(p, re.I) for p in _WEAK]
_SELF_PAID_RE = [re.compile(p) for p in _SELF_PAID]


def detect_sponsor_markers(text: str) -> dict:
    explicit = [m.group(0) for r in _EXPLICIT_RE if (m := r.search(text))]
    weak = [m.group(0) for r in _WEAK_RE if (m := r.search(text))]
    self_paid = any(r.search(text) for r in _SELF_PAID_RE)
    return {"explicit": explicit, "weak": weak, "self_paid": self_paid}
