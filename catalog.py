"""장소·상세·리뷰 조회 서비스 계층.

API 키가 있으면 실데이터(TourAPI·네이버), 없으면 data/demo 샘플로 동작한다.
AI 분석(Qwen)은 어느 쪽이든 실제로 수행한다.
"""
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

import cache
import merge
import personalize
from ai_pipeline import llm, translate
from ai_pipeline.trust_filter import analyze_post
from config import DEMO_DIR, REGIONS, REVIEWS_PER_PLACE
from data_sources import naver_blog, tour_api

log = logging.getLogger(__name__)


# ── 샘플 데이터 ───────────────────────────────────────────────────────────

@lru_cache
def _demo(region_key: str) -> dict:
    return json.loads((DEMO_DIR / f"{region_key}.json").read_text(encoding="utf-8"))


def _demo_place(item: dict, lang: str) -> dict:
    return {
        "id": item["contentid"], "type_id": item["contenttypeid"], "category": item["category"],
        "title_ko": item["title"], "title": item["title_i18n"].get(lang, item["title"]),
        "addr_ko": item["addr1"], "addr": item["addr_i18n"].get(lang, item["addr1"]),
        "image": "", "thumb": "", "mapx": item["mapx"], "mapy": item["mapy"], "tel": item.get("tel", ""),
        "dist": "", "classes": "", "tags": item.get("tags", []),
        "event_start": "", "event_end": "", "foreign": None, "official_translation": False, "sample": True,
    }


def _find_demo_item(place_id: str) -> tuple[str, dict] | tuple[None, None]:
    for key in REGIONS:
        for item in _demo(key)["places"]:
            if item["contentid"] == place_id:
                return key, item
    return None, None


# ── 장소 목록 ─────────────────────────────────────────────────────────────

def _decorate(places: list[dict]) -> list[dict]:
    for p in places:
        p["tags"] = personalize.derive_tags(p)
        p["trust"] = cache.get("place_trust", p["id"])
    return places


def _live_places(region: dict, lang: str) -> list[dict]:
    items = tour_api.location_list("ko", region) + tour_api.festivals("ko", region)
    seen, places = set(), []
    for item in items:
        place = tour_api.normalize(item)
        if place and place["id"] not in seen:
            seen.add(place["id"])
            places.append(place)
    if lang != "ko":
        try:
            foreign = tour_api.location_list(lang, region) + tour_api.festivals(lang, region)
            tour_api.attach_official_translation(places, foreign)
        except tour_api.TourApiError as e:
            log.warning("외국어 서비스 조회 실패(%s): %s", lang, e)
        rest = [p for p in places if not p["official_translation"]]
        for p, name in zip(rest, translate.translate_names([p["title_ko"] for p in rest], lang)):
            if name != p["title_ko"]:
                p["title"], p["machine_translated"] = name, True
    return places


def list_places(region_key: str, lang: str, tags: list[str] | None = None) -> dict:
    region = REGIONS[region_key]
    error = None
    if tour_api.enabled():
        try:
            places, source = _live_places(region, lang), "live"
        except tour_api.TourApiError as e:
            log.error("TourAPI 오류 → 샘플 데이터로 대체: %s", e)
            error, places, source = str(e), None, "sample"
    else:
        places, source = None, "sample"
    if places is None:
        places = [_demo_place(i, lang) for i in _demo(region_key)["places"]]
    places = personalize.filter_and_rank(_decorate(places), tags)
    return {"places": places, "source": source, "error": error}


def search_places(q: str, lang: str) -> dict:
    q = q.strip()[:40]
    if tour_api.enabled():
        try:
            places = [p for p in map(tour_api.normalize, tour_api.keyword_search("ko", q)) if p]
            rest = places if lang != "ko" else []
            for p, name in zip(rest, translate.translate_names([p["title_ko"] for p in rest], lang)):
                if name != p["title_ko"]:
                    p["title"], p["machine_translated"] = name, True
            return {"places": _decorate(places), "source": "live", "error": None}
        except tour_api.TourApiError as e:
            log.error("키워드 검색 실패: %s", e)
    places = [_demo_place(i, lang) for key in REGIONS for i in _demo(key)["places"]
              if q in i["title"] or q.lower() in json.dumps(i["title_i18n"], ensure_ascii=False).lower()]
    return {"places": _decorate(places), "source": "sample", "error": None}


# ── 상세 정보 ─────────────────────────────────────────────────────────────

_HOURS = ["usetime", "usetimeculture", "playtime", "usetimeleports", "opentime", "opentimefood"]
_CLOSED = ["restdate", "restdateculture", "restdateleports", "restdateshopping", "restdatefood"]
_FEE = ["usefee", "usetimefestival", "usefeeleports"]


def _text(v: str) -> str:
    v = re.sub(r"<br\s*/?>", "\n", v or "", flags=re.I)
    return re.sub(r"<[^>]+>", "", v).strip()


def _first(d: dict, keys: list[str]) -> str:
    return next((_text(d[k]) for k in keys if d.get(k)), "")


def place_detail(place_id: str, type_id: str, lang: str, foreign_id: str = "", foreign_type: str = "") -> dict:
    if place_id.startswith("demo-"):
        _, item = _find_demo_item(place_id)
        if not item:
            return {}
        tr = translate.translate_detail(item.get("overview", ""), item.get("hours", ""), item.get("fee", ""), lang)
        return {**tr, "closed": "", "tel": item.get("tel", ""), "homepage": "", "event": "", "translated_by": "qwen" if lang != "ko" else ""}

    official = lang != "ko" and foreign_id
    d = tour_api.detail(lang if official else "ko", foreign_id if official else place_id,
                        foreign_type if official else type_id)
    overview, hours, fee = _text(d.get("overview", "")), _first(d, _HOURS), _first(d, _FEE)
    translated_by = "official" if official else ""
    if lang != "ko" and not official:
        tr = translate.translate_detail(overview, hours, fee, lang)
        overview, hours, fee, translated_by = tr["overview"], tr["hours"], tr["fee"], "qwen"
    homepage = re.search(r'href="([^"]+)"', d.get("homepage", "") or "")
    event = f"{d['eventstartdate']} ~ {d.get('eventenddate', '')}" if d.get("eventstartdate") else ""
    return {"overview": overview, "hours": hours, "fee": fee, "closed": _first(d, _CLOSED),
            "tel": _text(d.get("tel", "") or d.get("infocenter", "")), "event": event,
            "homepage": homepage.group(1) if homepage else "", "translated_by": translated_by}


# ── 리뷰 수집 + 신뢰도 분석 (스트리밍) ──────────────────────────────────

def _collect_posts(place_id: str, title_ko: str, region_key: str) -> tuple[list[dict], str, str]:
    hint = REGIONS.get(region_key, {}).get("search_hint", "")
    query = merge.blog_query(title_ko, hint)
    if naver_blog.enabled():
        try:
            posts = naver_blog.search_blog_posts(query, display=max(10, REVIEWS_PER_PLACE * 2))
            return merge.relevant_posts(title_ko, posts)[:REVIEWS_PER_PLACE], "live", query
        except naver_blog.NaverApiError as e:
            log.error("네이버 API 오류 → 샘플로 대체: %s", e)
    key, _ = _find_demo_item(place_id)
    posts = _demo(key)["reviews"].get(place_id, []) if key else []
    return posts, "sample", query


def review_stream(place_id: str, title_ko: str, region_key: str, lang: str, title_tr: str = ""):
    posts, source, query = _collect_posts(place_id, title_ko, region_key)
    use_llm = llm.is_online()
    yield {"type": "meta", "source": source, "query": query, "count": len(posts), "llm": use_llm}

    glossary = {title_ko: title_tr} if title_tr else {}
    region = REGIONS.get(region_key)
    if region and lang in region["hint_i18n"]:
        glossary[region["search_hint"]] = region["hint_i18n"][lang]
    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(analyze_post, p, lang, use_llm, glossary) for p in posts]
        for f in as_completed(futures):
            try:
                r = f.result().model_dump()
            except Exception as e:  # 한 건 실패가 전체 스트림을 끊지 않도록
                log.exception("리뷰 분석 실패: %s", e)
                continue
            results.append(r)
            yield {"type": "review", "review": r}

    summary = merge.summarize_trust(results)
    if results:
        cache.put("place_trust", place_id, summary)
    yield {"type": "summary", "trust": summary}


def analyze_text(title: str, text: str, lang: str) -> dict:
    return analyze_post({"title": title[:200], "description": text[:3000]}, lang, llm.is_online()).model_dump()
