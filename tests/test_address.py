"""한국어 주소 → 영문 주소 변환 테스트. 기대값은 관광공사 영문 서비스(EngService2)의 공식 주소 표기."""
import pytest

from data_sources.address import romanize, romanize_address


@pytest.mark.parametrize("word,expected", [
    ("왕십리", "wangsimni"),    # ㅂ+ㄹ → ㅁㄴ
    ("강릉", "gangneung"),      # ㅇ+ㄹ → ㅇㄴ
    ("종로", "jongno"),
    ("신림", "sillim"),         # ㄴ+ㄹ → ㄹㄹ
    ("독립문", "dongnimmun"),
    ("국물", "gungmul"),        # 비음화
    ("한옥", "hanok"),          # 연음
    ("해운대", "haeundae"),
])
def test_romanize_assimilation(word, expected):
    assert romanize(word) == expected


@pytest.mark.parametrize("ko,en", [
    ("서울특별시 성동구 왕십리로10길 5-6", "5-6 Wangsimni-ro 10-gil, Seongdong-gu, Seoul"),
    ("서울특별시 성동구 성수이로7길 41-1", "41-1 Seongsui-ro 7-gil, Seongdong-gu, Seoul"),
    ("전북특별자치도 전주시 완산구 경기전길 135", "135 Gyeonggijeon-gil, Wansan-gu, Jeonju-si, Jeonbuk-do"),
    ("전북특별자치도 전주시 완산구 풍남문1길 19-3", "19-3 Pungnammun 1-gil, Wansan-gu, Jeonju-si, Jeonbuk-do"),
    ("부산광역시 중구 구덕로48번길 4", "4 Gudeok-ro 48beon-gil, Jung-gu, Busan"),
    ("서울특별시 성동구 뚝섬로1가길 14 (성수동1가)", "14 Ttukseom-ro 1ga-gil, Seongdong-gu, Seoul"),
    ("서울특별시 성동구 왕십리로 83-21 아크로 서울포레스트", "83-21 Wangsimni-ro, Seongdong-gu, Seoul"),
    ("서울특별시 성동구 연무장길 20 2층", "2F, 20 Yeonmujang-gil, Seongdong-gu, Seoul"),
    ("부산광역시 중구 중앙대로 지하17 (중앙동6가)", "B17 Jungang-daero, Jung-gu, Busan"),
    ("서울특별시 성동구 성수동2가 333-16", "333-16 Seongsu-dong 2-ga, Seongdong-gu, Seoul"),
    ("제주특별자치도 제주시 이도일동", "Ido 1-dong, Jeju-si, Jeju-do"),
    ("강원특별자치도 강릉시 임영로180번길 16", "16 Imyeong-ro 180beon-gil, Gangneung-si, Gangwon-do"),
])
def test_romanize_address(ko, en):
    assert romanize_address(ko) == en


def test_romanize_address_keeps_non_korean():
    assert romanize_address("") == ""
    assert romanize_address("5-6 Wangsimni-ro 10-gil, Seongdong-gu, Seoul") == "5-6 Wangsimni-ro 10-gil, Seongdong-gu, Seoul"
