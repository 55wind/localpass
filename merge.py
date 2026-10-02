"""TourAPI 장소 ↔ 블로그 글 연결."""
import re

from ai_pipeline.trust_filter import clean_html


def _norm(s: str) -> str:
    return re.sub(r"[\s\W_]+", "", s).lower()


def blog_query(place_title: str, search_hint: str = "") -> str:
    """'어니언 성수' 처럼 지역명이 이미 들어 있으면 중복하지 않는다."""
    title = re.sub(r"\(.*?\)|\[.*?\]", "", place_title).strip()
    if search_hint and search_hint not in title:
        return f"{search_hint} {title}"
    return title


def relevant_posts(place_title: str, posts: list[dict], min_keep: int = 2) -> list[dict]:
    """장소명이 제목·본문에 실제로 들어간 글만 남긴다 (부분 일치). 너무 적으면 원본 유지."""
    core = _norm(re.sub(r"\(.*?\)|\[.*?\]", "", place_title))
    if len(core) < 2:
        return posts
    matched = [p for p in posts
               if core in _norm(clean_html(p.get("title", ""))) or core in _norm(clean_html(p.get("description", "")))]
    return matched if len(matched) >= min_keep else posts


def summarize_trust(results: list[dict]) -> dict:
    counted = [r for r in results if r["badge"] != "blocked"]
    summary = {b: sum(1 for r in results if r["badge"] == b) for b in ("trusted", "caution", "flagged", "blocked")}
    summary["total"] = len(results)
    summary["avg"] = round(sum(r["trust_score"] for r in counted) / len(counted), 2) if counted else None
    return summary
