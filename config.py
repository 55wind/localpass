"""환경변수 로드 및 상수 정의."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

APP_NAME = os.getenv("APP_NAME", "LocalPass")

# 외부 API 키 (없으면 해당 소스는 샘플 데이터로 동작)
TOUR_API_KEY = os.getenv("TOUR_API_KEY", "")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
GPTZERO_API_KEY = os.getenv("GPTZERO_API_KEY", "")

# Qwen2.5-7B-Instruct — OpenAI 호환 엔드포인트 (기본: 로컬 Ollama)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "90"))

# AI 작성 판별: local(무료, Fast-DetectGPT) | gptzero(유료 API) | off
# 기본값은 GPTZero 키가 있으면 gptzero, 없으면 local
AI_DETECTOR = os.getenv("AI_DETECTOR", "gptzero" if GPTZERO_API_KEY else "local")
DETECTOR_MODEL = os.getenv("DETECTOR_MODEL", "Qwen/Qwen2.5-1.5B")
MODELS_DIR = Path(os.getenv("MODELS_DIR", str(ROOT / ".models")))

# 장소당 분석할 블로그 글 수
REVIEWS_PER_PLACE = int(os.getenv("REVIEWS_PER_PLACE", "6"))

CACHE_DIR = ROOT / ".cache"
DEMO_DIR = ROOT / "data" / "demo"

# UI 언어 → TourAPI 서비스 / LLM 번역 목표 언어
LANGS = {
    "en": {"service": "EngService2", "label": "English"},
    "ja": {"service": "JpnService2", "label": "Japanese (日本語)"},
    "zh": {"service": "ChsService2", "label": "Simplified Chinese (简体中文)"},
    "ko": {"service": "KorService2", "label": "Korean (한국어)"},
}

# 카테고리 → contentTypeId (국문 / 외국어 서비스는 코드 체계가 다름)
CATEGORIES = {
    "attraction": {"kor": "12", "foreign": "76"},
    "culture": {"kor": "14", "foreign": "78"},
    "festival": {"kor": "15", "foreign": "85"},
    "shopping": {"kor": "38", "foreign": "79"},
    "food": {"kor": "39", "foreign": "82"},
}

# MVP 데모 지역 — 좌표+반경만 바꾸면 전국 어디로든 확장된다.
REGIONS = {
    "seongsu": {
        "name": {"ko": "성수동", "en": "Seongsu-dong", "ja": "聖水洞", "zh": "圣水洞"},
        "short": {"ko": "성수동", "en": "Seongsu", "ja": "聖水洞", "zh": "圣水洞"},
        "city": {"ko": "서울 성동구", "en": "Seongdong-gu, Seoul", "ja": "ソウル・城東区", "zh": "首尔城东区"},
        "map_x": 127.0480, "map_y": 37.5440, "radius": 1500,
        # 법정동 코드 (2025 TourAPI 개편 — areaCode/sigunguCode는 삭제 예정)
        "ldong_regn": "11", "ldong_signgu": "200",
        "search_hint": "성수",
        "hint_i18n": {"en": "Seongsu", "ja": "聖水", "zh": "圣水"},
    },
    "jeonju": {
        "name": {"ko": "전주 한옥마을·남부시장", "en": "Jeonju Hanok Village", "ja": "全州韓屋村", "zh": "全州韩屋村"},
        "short": {"ko": "전주", "en": "Jeonju", "ja": "全州", "zh": "全州"},
        "city": {"ko": "전북 전주시", "en": "Jeonju, Jeonbuk", "ja": "全羅北道・全州市", "zh": "全北全州市"},
        "map_x": 127.1505, "map_y": 35.8145, "radius": 1500,
        "ldong_regn": "52", "ldong_signgu": "111",  # 전북특별자치도 전주시 완산구
        "search_hint": "전주",
        "hint_i18n": {"en": "Jeonju", "ja": "全州", "zh": "全州"},
    },
}

# 신뢰도 배지 기준 (개발 로직 설계 §5)
TRUST_HIGH = 0.7
TRUST_LOW = 0.4
