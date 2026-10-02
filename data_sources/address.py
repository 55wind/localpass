"""한국어 주소 → 영문 주소 (국어의 로마자 표기법 + 도로명주소 영문 표기 순서).

관광공사 외국어 서비스에 없는 장소는 주소가 한국어로만 온다. 주소는 길 찾기에 쓰이므로
LLM 번역(숫자·지명 오류 위험, GPU 기동) 대신 규칙으로 바꾼다.
예: 서울특별시 성동구 왕십리로10길 5-6 → 5-6 Wangsimni-ro 10-gil, Seongdong-gu, Seoul
"""
import re

# ── 로마자 표기 (자음 동화 포함) ─────────────────────────────────────────

_INI = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
_MED = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi",
        "yu", "eu", "ui", "i"]
# 받침 번호(0=없음) → 자모
_FIN = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ",
        "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
_INI_JAMO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
_SOUND = {  # 받침의 대표음
    "ㄱ": "k", "ㄲ": "k", "ㅋ": "k", "ㄳ": "k", "ㄺ": "k",
    "ㄴ": "n", "ㄵ": "n", "ㄶ": "n",
    "ㄷ": "t", "ㅅ": "t", "ㅆ": "t", "ㅈ": "t", "ㅊ": "t", "ㅌ": "t", "ㅎ": "t",
    "ㄹ": "l", "ㄼ": "l", "ㄽ": "l", "ㄾ": "l", "ㅀ": "l",
    "ㅁ": "m", "ㄻ": "m",
    "ㅂ": "p", "ㅍ": "p", "ㅄ": "p", "ㄿ": "p",
    "ㅇ": "ng",
}
_SPLIT = {"ㄳ": ("ㄱ", "ㅅ"), "ㄵ": ("ㄴ", "ㅈ"), "ㄶ": ("ㄴ", "ㅎ"), "ㄺ": ("ㄹ", "ㄱ"), "ㄻ": ("ㄹ", "ㅁ"),
          "ㄼ": ("ㄹ", "ㅂ"), "ㄽ": ("ㄹ", "ㅅ"), "ㄾ": ("ㄹ", "ㅌ"), "ㄿ": ("ㄹ", "ㅍ"), "ㅀ": ("ㄹ", "ㅎ"),
          "ㅄ": ("ㅂ", "ㅅ")}
_NASAL = {"k": "ㅇ", "t": "ㄴ", "p": "ㅁ"}  # 비음화: ㄴ·ㅁ 앞의 ㄱ·ㄷ·ㅂ 소리
_HANGUL = re.compile(r"[가-힣]")


def romanize(word: str) -> str:
    """한글 단어를 로마자로 (연음·비음화·유음화·ㄹ의 비음화 반영). 한글 외 글자는 그대로 둔다."""
    syl = []  # [초성 자모, 중성 번호, 받침 자모] 또는 한글이 아닌 글자
    for ch in word:
        code = ord(ch) - 0xAC00
        if 0 <= code < 11172:
            syl.append([_INI_JAMO[code // 588], (code % 588) // 28, _FIN[code % 28]])
        else:
            syl.append(ch)
    for a, b in zip(syl, syl[1:]):
        if not (isinstance(a, list) and isinstance(b, list)) or not a[2]:
            continue
        fin, ini = a[2], b[0]
        sound = _SOUND[fin]
        if ini == "ㅇ" and fin != "ㅇ":                      # 연음
            keep, move = _SPLIT.get(fin, ("", fin))
            a[2], b[0] = keep, ("ㅇ" if move == "ㅎ" else move)
        elif ini == "ㄹ":
            if sound in ("n", "l"):                          # 신림 → 실림
                a[2] = "ㄹ"
            elif sound in ("m", "ng"):                       # 종로 → 종노, 강릉 → 강능
                b[0] = "ㄴ"
            else:                                            # 십리 → 심니, 독립 → 동닙
                a[2], b[0] = _NASAL[sound], "ㄴ"
        elif ini in ("ㄴ", "ㅁ"):
            if sound in _NASAL:                              # 국물 → 궁물
                a[2] = _NASAL[sound]
            elif sound == "l" and ini == "ㄴ":               # 설날 → 설랄
                b[0] = "ㄹ"
    out, prev_fin = [], ""
    for s in syl:
        if isinstance(s, str):
            out.append(s)
            prev_fin = ""
            continue
        ini, med, fin = s
        lead = "l" if ini == "ㄹ" and prev_fin == "ㄹ" else _INI[_INI_JAMO.index(ini)]  # 받침 ㄹ + 초성 ㄹ = ll
        out.append(lead + _MED[med] + (_SOUND[fin] if fin else ""))
        prev_fin = fin
    return "".join(out)


def _rom(word: str) -> str:
    r = romanize(word)
    return r[:1].upper() + r[1:]


# ── 주소 ─────────────────────────────────────────────────────────────

_PROVINCE = {
    "서울특별시": "Seoul", "서울": "Seoul", "부산광역시": "Busan", "대구광역시": "Daegu", "인천광역시": "Incheon",
    "광주광역시": "Gwangju", "대전광역시": "Daejeon", "울산광역시": "Ulsan", "세종특별자치시": "Sejong-si",
    "경기도": "Gyeonggi-do", "강원특별자치도": "Gangwon-do", "강원도": "Gangwon-do",
    "충청북도": "Chungcheongbuk-do", "충청남도": "Chungcheongnam-do",
    "전북특별자치도": "Jeonbuk-do", "전라북도": "Jeollabuk-do", "전라남도": "Jeollanam-do",
    "경상북도": "Gyeongsangbuk-do", "경상남도": "Gyeongsangnam-do", "제주특별자치도": "Jeju-do",
}
_SUB = "가나다라마바사아자차카타파하"  # 왕십리로14나길 같은 가지길 글자
_ROAD = re.compile(rf"^([가-힣]+?)(대로|로|길)(?:(\d+)([{_SUB}]?)(번길|길))?$")  # 성수이로7길, 구덕로48번길, 경기전길
_ROAD_NUM = re.compile(rf"^([가-힣]+?)(\d+)([{_SUB}]?)(번길|길)$")              # 풍남문1길, 상원6나길
_NUM_DONG = re.compile(r"^([가-힣]{2,})([일이삼사오육칠팔구])동$")                 # 이도일동 → Ido 1-dong
_DIGIT = {c: str(i) for i, c in enumerate("일이삼사오육칠팔구", 1)}
_GA = re.compile(r"^([가-힣]+?)(\d+)가$")            # 성수동1가, 을지로3가
_NUM = re.compile(r"^(산|지하)?(\d+(?:-\d+)?)(번지)?$")
_FLOOR = re.compile(r"^(지하)?(\d+)층$")
_UNIT = re.compile(r"^(\d+)호$")
_ADMIN = {"시": "si", "군": "gun", "구": "gu", "읍": "eup", "면": "myeon", "동": "dong", "리": "ri"}


def _branch(num: str, letter: str, sub: str) -> str:
    """'14', '나', '길' → '14na-gil' / '48', '', '번길' → '48beon-gil'"""
    return f"{num}{romanize(letter) if letter else ''}{'beon-gil' if sub == '번길' else '-gil'}"


def _road(tok: str) -> str:
    if m := _ROAD.match(tok):
        name, kind, num, letter, sub = m.groups()
        out = f"{_rom(name)}-{ {'대로': 'daero', '로': 'ro', '길': 'gil'}[kind]}"
        return f"{out} {_branch(num, letter, sub)}" if num else out
    if m := _ROAD_NUM.match(tok):
        name, num, letter, sub = m.groups()
        return f"{_rom(name)} {_branch(num, letter, sub)}"
    return ""


def romanize_address(addr: str) -> str:
    """'전북특별자치도 전주시 완산구 경기전길 135' → '135 Gyeonggijeon-gil, Wansan-gu, Jeonju-si, Jeonbuk-do'"""
    if not addr or not _HANGUL.search(addr):
        return addr or ""
    text = re.sub(r"[(（][^)）]*[)）]", " ", addr).replace(",", " ")
    province = city = district = town = village = road = number = ""
    extras, underground = [], False
    for tok in text.split():
        if tok in _PROVINCE:
            province = _PROVINCE[tok]
        elif m := _NUM.match(tok):
            if number:  # 번호가 두 번 나오면 뒤쪽은 상세 주소
                extras.append(m.group(2))
            else:
                number = {"산": "San ", "지하": "B"}.get(m.group(1) or "", "") + m.group(2)
        elif m := _FLOOR.match(tok):
            extras.append(f"B{m.group(2)}F" if m.group(1) else f"{m.group(2)}F")
        elif m := _UNIT.match(tok):
            extras.append(f"#{m.group(1)}")
        elif not number and not road and (m := _GA.match(tok)):
            base = m.group(1)
            base = f"{_rom(base[:-1])}-dong" if base.endswith("동") and len(base) > 1 else _rom(base)
            village = f"{base} {m.group(2)}-ga"
        elif tok == "지하":
            underground = True
        elif not number and (m := _NUM_DONG.match(tok)):
            village = f"{_rom(m.group(1))} {_DIGIT[m.group(2)]}-dong"
        elif not number and not road and (r := _road(tok)):
            road = r
        elif not number and len(tok) > 1 and tok[-1] in _ADMIN and _HANGUL.fullmatch(tok[0]):
            unit = f"{_rom(tok[:-1])}-{_ADMIN[tok[-1]]}"
            if tok[-1] == "구":
                district = unit
            elif tok[-1] in "시군":
                city = unit
            elif tok[-1] in "읍면":
                town = unit
            else:
                village = unit
        elif tok.endswith(("특별시", "광역시", "특별자치시", "특별자치도", "도")) and not province and not number:
            province = _rom(re.sub(r"(특별시|광역시|특별자치시|특별자치도|도)$", "", tok)) + ("-do" if tok.endswith("도") else "")
        elif not _HANGUL.search(tok):
            extras.append(tok)  # B1, 2F 처럼 이미 영문인 상세 주소
        # 그 밖의 한글(건물명·'일원' 등)은 공식 영문 주소처럼 쓰지 않는다
    if underground and number and not number.startswith("B"):
        number = "B" + number
    # 도로명주소는 동 이름을 쓰지 않고, 지번주소는 동 이름 앞에 번지를 붙인다
    street = " ".join(filter(None, [number, road or village]))
    parts = [", ".join(extras), street, town, district, city, province]
    return ", ".join(p for p in parts if p)
