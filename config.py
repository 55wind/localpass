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
# 원격 GPU(Modal)가 꺼져 있다 켜질 때까지 기다리는 최대 시간 (Vercel 함수 최대 300초 안쪽)
LLM_WAKE_TIMEOUT = float(os.getenv("LLM_WAKE_TIMEOUT", "240"))

# AI 작성 판별: local(무료, Fast-DetectGPT를 이 서버에서) | remote(같은 판별기를 Modal에서) | gptzero(유료 API) | off
DETECTOR_URL = os.getenv("DETECTOR_URL", "").rstrip("/")   # deploy/modal_detector.py 주소
AI_DETECTOR = os.getenv("AI_DETECTOR", "gptzero" if GPTZERO_API_KEY else "remote" if DETECTOR_URL else "local")
DETECTOR_MODEL = os.getenv("DETECTOR_MODEL", "Qwen/Qwen2.5-1.5B")
DETECTOR_DEVICE = os.getenv("DETECTOR_DEVICE", "auto")  # auto | cpu | cuda — GPU 없이 쓰려면 cpu
MODELS_DIR = Path(os.getenv("MODELS_DIR", str(ROOT / ".models")))

# 장소당 분석할 블로그 글 수
REVIEWS_PER_PLACE = int(os.getenv("REVIEWS_PER_PLACE", "6"))

# Vercel 함수는 /tmp 에만 쓸 수 있다 (인스턴스가 살아 있는 동안 유지)
CACHE_DIR = Path("/tmp/localpass-cache") if os.getenv("VERCEL") else ROOT / ".cache"
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
    # 지방 확장 — 원도심·전통시장 중심. 법정동 코드는 TourAPI ldongCode2 로 확인
    "busan": {
        "name": {"ko": "부산 남포동·자갈치", "en": "Busan Nampo-dong", "ja": "釜山・南浦洞", "zh": "釜山南浦洞"},
        "short": {"ko": "부산", "en": "Busan", "ja": "釜山", "zh": "釜山"},
        "city": {"ko": "부산 중구", "en": "Jung-gu, Busan", "ja": "釜山・中区", "zh": "釜山中区"},
        "map_x": 129.0300, "map_y": 35.0990, "radius": 1500,
        "ldong_regn": "26", "ldong_signgu": "110",
        "search_hint": "부산",
        "hint_i18n": {"en": "Busan", "ja": "釜山", "zh": "釜山"},
    },
    "gangneung": {
        "name": {"ko": "강릉 중앙시장·원도심", "en": "Gangneung Old Town", "ja": "江陵・中央市場", "zh": "江陵中央市场"},
        "short": {"ko": "강릉", "en": "Gangneung", "ja": "江陵", "zh": "江陵"},
        "city": {"ko": "강원 강릉시", "en": "Gangneung, Gangwon", "ja": "江原・江陵市", "zh": "江原江陵市"},
        "map_x": 128.8990, "map_y": 37.7560, "radius": 2000,
        "ldong_regn": "51", "ldong_signgu": "150",
        "search_hint": "강릉",
        "hint_i18n": {"en": "Gangneung", "ja": "江陵", "zh": "江陵"},
    },
    "gyeongju": {
        "name": {"ko": "경주 황리단길·대릉원", "en": "Gyeongju Hwangnidan-gil", "ja": "慶州・皇理団通り", "zh": "庆州皇理团路"},
        "short": {"ko": "경주", "en": "Gyeongju", "ja": "慶州", "zh": "庆州"},
        "city": {"ko": "경북 경주시", "en": "Gyeongju, Gyeongbuk", "ja": "慶尚北道・慶州市", "zh": "庆北庆州市"},
        "map_x": 129.2160, "map_y": 35.8360, "radius": 1500,
        "ldong_regn": "47", "ldong_signgu": "130",
        "search_hint": "경주",
        "hint_i18n": {"en": "Gyeongju", "ja": "慶州", "zh": "庆州"},
    },
    "jeju": {
        "name": {"ko": "제주 동문시장·원도심", "en": "Jeju City Old Town", "ja": "済州・東門市場", "zh": "济州东门市场"},
        "short": {"ko": "제주", "en": "Jeju", "ja": "済州", "zh": "济州"},
        "city": {"ko": "제주 제주시", "en": "Jeju City, Jeju", "ja": "済州・済州市", "zh": "济州济州市"},
        "map_x": 126.5250, "map_y": 33.5120, "radius": 1500,
        "ldong_regn": "50", "ldong_signgu": "110",
        "search_hint": "제주",
        "hint_i18n": {"en": "Jeju", "ja": "済州", "zh": "济州"},
    },
}

# 신뢰도 배지 기준 (개발 로직 설계 §5)
TRUST_HIGH = 0.7
TRUST_LOW = 0.4
