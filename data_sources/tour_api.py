"""한국관광공사 TourAPI 4.0 (KorService2 / EngService2 / JpnService2 / ChsService2) 연동.

- serviceKey는 '디코딩' 키를 넣는다 (requests가 인코딩하므로 인코딩 키를 넣으면 이중 인코딩 → 인증 오류).
- 인증·한도 오류는 _type=json이어도 XML로 오므로 따로 처리한다.
- 결과가 0건이면 items가 "", 1건이면 리스트가 아닌 객체로 온다.
"""
import logging
import math
import re
from datetime import date, timedelta

import requests

import cache
from config import APP_NAME, CATEGORIES, LANGS, TOUR_API_KEY

log = logging.getLogger(__name__)

BASE = "https://apis.data.go.kr/B551011"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LocalPass/1.0"
LIST_TTL = 6 * 3600
DETAIL_TTL = 24 * 3600

# contentTypeId → 화면 카테고리 (국문·외국어 코드 모두)
TYPE_TO_CATEGORY = {code: cat for cat, codes in CATEGORIES.items() for code in codes.values()}
TYPE_TO_CATEGORY.update({"28": "attraction", "75": "attraction"})  # 레포츠는 관광지 탭에 포함


class TourApiError(Exception):
    pass


def enabled() -> bool:
    return bool(TOUR_API_KEY)


def _call(service: str, operation: str, **params) -> list[dict]:
    if not enabled():
        raise TourApiError("TOUR_API_KEY 미설정")
    try:
        resp = requests.get(
            f"{BASE}/{service}/{operation}",
            params={"serviceKey": TOUR_API_KEY, "MobileOS": "ETC", "MobileApp": APP_NAME, "_type": "json", **params},
            headers={"User-Agent": UA},
            timeout=15,
        )
    except requests.RequestException as e:
        raise TourApiError(f"네트워크 오류: {e}") from e

    body = resp.text.strip()
    if resp.status_code >= 400 or body.startswith("<"):
        msg = re.search(r"<(?:errMsg|returnAuthMsg)>([^<]+)<", body)
        code = re.search(r"<returnReasonCode>([^<]+)<", body)
        raise TourApiError(f"HTTP {resp.status_code} {msg.group(1) if msg else ''} {code.group(1) if code else ''}".strip())

    data = resp.json()
    header = data.get("response", {}).get("header", {})
    if header.get("resultCode") not in ("0000", "00"):
        raise TourApiError(f"{header.get('resultCode')} {header.get('resultMsg')}")
    items = data["response"].get("body", {}).get("items") or {}
    item = items.get("item", []) if isinstance(items, dict) else []
    return item if isinstance(item, list) else [item]


def _service(lang: str) -> str:
    return LANGS[lang]["service"]


def _https(url: str) -> str:
    return url.replace("http://", "https://", 1) if url else ""


def _distance_m(a: dict, b: dict) -> float:
    try:
        x1, y1, x2, y2 = float(a["mapx"]), float(a["mapy"]), float(b["mapx"]), float(b["mapy"])
    except (KeyError, ValueError):
        return math.inf
    dx = (x2 - x1) * 111_320 * math.cos(math.radians((y1 + y2) / 2))
    dy = (y2 - y1) * 110_540
    return math.hypot(dx, dy)


def location_list(lang: str, region: dict, rows: int = 100) -> list[dict]:
    """좌표+반경 기준 관광정보 (전 카테고리 1회 호출)."""
    def fetch():
        return _call(_service(lang), "locationBasedList2",
                     mapX=region["map_x"], mapY=region["map_y"], radius=region["radius"],
                     arrange="E", numOfRows=rows, pageNo=1)
    return cache.cached("tour_location", [lang, region["map_x"], region["map_y"], region["radius"], rows],
                        fetch, ttl=LIST_TTL)


def festivals(lang: str, region: dict) -> list[dict]:
    """진행 중이거나 다가오는 축제 (법정동 코드 기준)."""
    start = (date.today() - timedelta(days=60)).strftime("%Y%m%d")
    today = date.today().strftime("%Y%m%d")

    def fetch():
        return _call(_service(lang), "searchFestival2", eventStartDate=start,
                     lDongRegnCd=region["ldong_regn"], lDongSignguCd=region["ldong_signgu"],
                     arrange="A", numOfRows=50, pageNo=1)
    items = cache.cached("tour_festival", [lang, region["ldong_regn"], region["ldong_signgu"], start], fetch, ttl=LIST_TTL)
    return [i for i in items if (i.get("eventenddate") or "99999999") >= today]


def keyword_search(lang: str, keyword: str, rows: int = 40) -> list[dict]:
    def fetch():
        return _call(_service(lang), "searchKeyword2", keyword=keyword, arrange="Q", numOfRows=rows, pageNo=1)
    return cache.cached("tour_keyword", [lang, keyword, rows], fetch, ttl=LIST_TTL)


def detail(lang: str, content_id: str, content_type_id: str) -> dict:
    """detailCommon2(개요·홈페이지) + detailIntro2(운영시간 등)."""
    def fetch():
        common = _call(_service(lang), "detailCommon2", contentId=content_id)
        intro = _call(_service(lang), "detailIntro2", contentId=content_id, contentTypeId=content_type_id)
        return {**(common[0] if common else {}), **(intro[0] if intro else {})}
    return cache.cached("tour_detail", [lang, content_id, content_type_id], fetch, ttl=DETAIL_TTL)


# ── 정규화 ────────────────────────────────────────────────────────────────

def normalize(item: dict) -> dict | None:
    category = TYPE_TO_CATEGORY.get(str(item.get("contenttypeid", "")))
    if not category:
        return None  # 숙박·여행코스·교통은 MVP 범위 밖
    return {
        "id": str(item["contentid"]),
        "type_id": str(item.get("contenttypeid", "")),
        "category": category,
        "title_ko": item.get("title", ""),
        "title": item.get("title", ""),
        "addr_ko": item.get("addr1", ""),
        "addr": item.get("addr1", ""),
        "image": _https(item.get("firstimage", "")),
        "thumb": _https(item.get("firstimage2", "") or item.get("firstimage", "")),
        "mapx": item.get("mapx", ""),
        "mapy": item.get("mapy", ""),
        "tel": item.get("tel", ""),
        "dist": item.get("dist", ""),
        "classes": " ".join(filter(None, [item.get(k, "") for k in ("lclsSystm1", "lclsSystm2", "lclsSystm3", "cat1", "cat2", "cat3")])),
        "event_start": item.get("eventstartdate", ""),
        "event_end": item.get("eventenddate", ""),
        "foreign": None,
        "official_translation": False,
    }


_KO_SUFFIX = re.compile(r"\s*[（(]([^()（）]*[가-힣][^()（）]*)[)）]\s*$")
_HANGUL = re.compile(r"[가-힣]")


def split_foreign_title(title: str) -> tuple[str, str]:
    """'Seongsu Stage 35 (스테이지35 성수)' → ('Seongsu Stage 35', '스테이지35 성수')"""
    m = _KO_SUFFIX.search(title or "")
    return (title[: m.start()].strip(), m.group(1).strip()) if m else ((title or "").strip(), "")


def _key(s: str) -> str:
    return re.sub(r"[\s\W_]+", "", s)


def attach_official_translation(places: list[dict], foreign_items: list[dict], max_m: float = 40) -> None:
    """국문 목록(마스터)에 외국어 서비스의 공식 번역을 붙인다.

    국문·외국어 서비스는 contentid가 서로 다르다. 외국어 제목 끝 괄호의 한글 이름이 같으면 그걸로 매칭하고,
    없으면 좌표로 매칭하되 반경 안에 후보가 딱 하나일 때만 인정한다 (같은 건물의 가게들, 같은 행사장의
    축제들을 서로 잘못 잇지 않도록). 축제는 행사장 좌표를 공유하는 일이 많아 이름으로만 매칭한다.
    """
    pool = []
    for f in foreign_items:
        name, ko = split_foreign_title(f.get("title", ""))
        if name and not _HANGUL.search(name):  # 제목이 한글뿐이면 번역이 안 된 항목
            pool.append((f, name, _key(ko)))
    by_ko = {ko: (f, name) for f, name, ko in pool if ko}
    for place in places:
        hit = by_ko.get(_key(place["title_ko"]))
        best, best_name = hit if hit else (None, "")
        if not hit and place["category"] != "festival":
            near = [(f, name) for f, name, _ in pool
                    if TYPE_TO_CATEGORY.get(str(f.get("contenttypeid"))) == place["category"]
                    and _distance_m(place, f) < max_m]
            if len(near) == 1:
                best, best_name = near[0]
        if best:
            place["title"] = best_name
            place["addr"] = best.get("addr1") or place["addr"]
            place["image"] = place["image"] or _https(best.get("firstimage", ""))
            place["thumb"] = place["thumb"] or _https(best.get("firstimage2", ""))
            place["foreign"] = {"id": str(best["contentid"]), "type_id": str(best.get("contenttypeid", ""))}
            place["official_translation"] = True
