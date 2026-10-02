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


def relevant_posts(place_title: str, posts: list[dict], hint: str = "") -> list[dict]:
    """장소명의 단어(2글자 이상)가 제목·요약에 모두 들어간 글만 남긴다.

    '어니언 성수' → '어니언'과 '성수'가 각각 있으면 인정 ('성수동 어니언', '어니언성수' 모두 통과).
    제목엔 없고 본문에만 스치듯 나오는 글은 지역명(hint)도 함께 있어야 인정한다
    — '남부시장'처럼 흔한 이름이 '베트남 남부 시장' 같은 엉뚱한 글에 걸리지 않도록.
    엉뚱한 글을 분석해 보여주느니 0건이 낫기 때문에, 맞는 글이 없으면 빈 목록을 돌려준다.
    """
    tokens = _tokens(place_title)
    need_hint = _norm(hint) if hint and hint not in place_title else ""

    def ok(p: dict) -> bool:
        title = _norm(clean_html(p.get("title", "")))
        body = title + _norm(clean_html(p.get("description", "")))
        if not all(t in body for t in tokens):
            return False
        return all(t in title for t in tokens) or not need_hint or need_hint in body
    return [p for p in posts if ok(p)]


def _tokens(place_title: str) -> list[str]:
    tokens = [_norm(t) for t in re.sub(r"\(.*?\)|\[.*?\]", "", place_title).split()]
    return [t for t in tokens if len(t) >= 2] or [_norm(place_title)]


def pick_posts(place_title: str, *result_lists: list[dict], limit: int, hint: str = "") -> list[dict]:
    """여러 검색 결과(최신순·관련도순)를 합쳐 중복을 빼고 관련 글만 limit개 고른다.

    제목에 장소명이 들어간 글(그 장소에 대한 후기)을 먼저, 본문에 스치듯 언급한 글은 나중에 — 같은 순위면 최신 글 우선.
    """
    seen, merged = set(), []
    for posts in result_lists:
        for p in posts:
            if p.get("link") not in seen:
                seen.add(p.get("link"))
                merged.append(p)
    tokens = _tokens(place_title)

    def rank(p: dict):
        in_title = all(t in _norm(clean_html(p.get("title", ""))) for t in tokens)
        return (0 if in_title else 1, -int(p.get("postdate") or 0))

    return sorted(relevant_posts(place_title, merged, hint), key=rank)[:limit]


def summarize_trust(results: list[dict]) -> dict:
    counted = [r for r in results if r["badge"] != "blocked"]
    summary = {b: sum(1 for r in results if r["badge"] == b) for b in ("trusted", "caution", "sponsored", "flagged", "blocked")}
    summary["total"] = len(results)
    summary["avg"] = round(sum(r["trust_score"] for r in counted) / len(counted), 2) if counted else None
    return summary
