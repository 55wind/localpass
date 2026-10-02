"""네이버 검색 오픈API(블로그) — UGC 원문 후보 수집.

공식 API가 주는 요약(description)만 사용한다. 네이버 블로그 robots.txt는 AI·RAG 목적의
봇 접근을 금지하므로 본문 페이지를 크롤링하지 않는다.
"""
import logging

import requests

import cache
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

log = logging.getLogger(__name__)

ENDPOINT = "https://openapi.naver.com/v1/search/blog.json"
TTL = 6 * 3600
_calls = {"count": 0}  # 일일 한도(25,000회) 관리용 — 프로세스 기준 호출 수


class NaverApiError(Exception):
    pass


def enabled() -> bool:
    return bool(NAVER_CLIENT_ID and NAVER_CLIENT_SECRET)


def call_count() -> int:
    return _calls["count"]


def search_blog_posts(query: str, display: int = 10, sort: str = "sim") -> list[dict]:
    def fetch():
        try:
            resp = requests.get(
                ENDPOINT,
                headers={"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET},
                params={"query": query, "display": display, "sort": sort},
                timeout=10,
            )
        except requests.RequestException as e:
            raise NaverApiError(str(e)) from e
        _calls["count"] += 1
        log.info("네이버 블로그 API 호출 %d회째: %s", _calls["count"], query)
        if resp.status_code == 429:
            raise NaverApiError("일일 호출 한도 초과 (429)")
        if not resp.ok:
            raise NaverApiError(f"HTTP {resp.status_code} {resp.text[:120]}")
        return resp.json().get("items", [])

    return cache.cached("naver_blog", [query, display, sort], fetch, ttl=TTL)
