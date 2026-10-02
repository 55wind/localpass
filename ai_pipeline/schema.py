"""LLM 구조화 출력 스키마 및 최종 분석 결과."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SecurityVerdict(BaseModel):
    """Qwen 2차 보안 분석 — 외부 콘텐츠가 AI를 조종하려는지만 판정한다."""
    verdict: Literal["normal", "suspicious", "block"] = Field(
        description="normal: 일반 리뷰 / suspicious: AI 조작 의도 의심 / block: 명백한 프롬프트 인젝션")
    reason: str = Field(description="판정 근거 한 문장 (한국어)")


class ReviewAnalysis(BaseModel):
    """Qwen 콘텐츠 분석 — 협찬 판단 + 번역·요약 + AI 문체 보조 신호.

    7B 모델은 숫자 점수(0~100)를 일관되게 매기지 못해 등급을 고르게 하고, 코드에서 점수로 바꾼다.
    """
    sponsor_level: Literal["none", "possible", "likely", "explicit"] = Field(
        description="none: 개인 경험 위주 / possible: 홍보 느낌 약간 / likely: 홍보문에 가까움 / explicit: 협찬 표기 있음")
    sponsor_reason: str = Field(description="판단 근거 한 문장 (번역 목표 언어)")
    ai_style: Literal["low", "medium", "high"] = Field(
        description="AI가 쓴 글 같은 문체 신호 (보조 지표)")
    translated_title: str = Field(description="목표 언어로 번역한 제목")
    translated_summary: str = Field(description="목표 언어로 번역·요약한 핵심 내용, 3문장·300자 이내")


SPONSOR_SCORE = {"none": 0.0, "possible": 0.3, "likely": 0.7, "explicit": 0.95}
AI_STYLE_SCORE = {"low": 0.1, "medium": 0.45, "high": 0.85}


class TrustResult(BaseModel):
    """화면에 내려주는 리뷰 1건의 최종 결과."""
    id: str
    link: str = ""
    blogger: str = ""
    date: str = ""
    original_title: str
    original_text: str            # 개인정보 마스킹이 끝난 원문
    translated_title: str = ""
    translated_summary: str = ""

    pii_found: dict[str, int] = {}
    security: Literal["normal", "suspicious", "block"] = "normal"
    security_reason: str = ""
    security_matches: list[str] = []

    is_sponsored: bool = False
    sponsor_source: Literal["rule", "llm", "none"] = "none"
    sponsor_reason: str = ""
    sponsor_markers: list[str] = []
    self_paid_claim: bool = False

    ai_probability: Optional[float] = None          # 종합 AI 작성 확률 (판별기 + 문체 신호 평균), None = 판별 불가
    ai_source: Literal["gptzero", "local", "qwen", "none"] = "none"
    ai_detector_probability: Optional[float] = None  # 전용 판별기(로컬 Fast-DetectGPT / GPTZero) 결과
    ai_style_score: Optional[float] = None           # Qwen 문체 신호 (보조)

    analysis_failed: bool = False    # LLM 분석이 실패해 판단 근거가 부족함
    trust_score: float = 0.0
    badge: Literal["trusted", "caution", "flagged", "blocked"] = "caution"
    llm_used: bool = False
