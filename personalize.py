"""개인화 — 관심사 태그 부여, 태그 필터링, 신뢰도 기반 정렬."""

INTERESTS = ["nature", "history", "culture", "cafe", "food", "market", "shopping", "night", "free"]

_TITLE_KEYWORDS = {
    "nature": ["공원", "숲", "정원", "수목원", "한강", "호수", "산책로", "해변", "계곡"],
    "history": ["궁", "성당", "사찰", "향교", "서원", "고택", "유적", "성곽", "한옥", "경기전", "문화재", "왕릉", "풍남문"],
    "culture": ["미술관", "갤러리", "전시", "박물관", "문화", "공연", "극장", "아트", "에비뉴"],
    "cafe": ["카페", "커피", "베이커리", "제과", "디저트", "찻집", "빵"],
    "market": ["시장", "장터", "야시장"],
    "shopping": ["거리", "몰", "스토어", "편집숍", "백화점", "아울렛", "공방"],
    "night": ["야시장", "야경", "야간"],
}

# TourAPI 신분류체계(lclsSystm)·구분류(cat) 코드 접두어
_CLASS_PREFIX = {
    "nature": ["NA", "A01"],
    "history": ["HS", "A0201"],
    "culture": ["VE", "A0206"],
    "cafe": ["FD05", "A05020900"],
    "shopping": ["SH", "A04"],
    "market": ["SH06", "A04010200"],
}

_CATEGORY_DEFAULT = {"food": "food", "shopping": "shopping", "culture": "culture", "festival": "culture"}


def derive_tags(place: dict) -> list[str]:
    tags = set(place.get("tags") or [])
    title = place.get("title_ko", "")
    classes = place.get("classes", "").split()
    for tag, words in _TITLE_KEYWORDS.items():
        if any(w in title for w in words):
            tags.add(tag)
    for tag, prefixes in _CLASS_PREFIX.items():
        if any(c.startswith(p) for c in classes for p in prefixes):
            tags.add(tag)
    if default := _CATEGORY_DEFAULT.get(place.get("category", "")):
        tags.add(default)
    if "cafe" in tags:
        tags.add("food")
    return sorted(t for t in tags if t in INTERESTS)


def filter_and_rank(places: list[dict], tags: list[str] | None = None) -> list[dict]:
    """관심 태그로 거른 뒤, 검증된 리뷰가 많은 곳 → 신뢰도 → 사진 있는 곳 → 거리 순으로 정렬."""
    if tags:
        places = [p for p in places if set(tags) & set(p.get("tags", []))]

    def key(p):
        t = p.get("trust") or {}
        try:
            dist = float(p.get("dist") or 0)
        except ValueError:
            dist = 0.0
        return (-(t.get("trusted", 0)), -(t.get("avg", -1)), 0 if p.get("image") else 1, dist)

    return sorted(places, key=key)
