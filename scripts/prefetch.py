"""시연 전에 데모 지역의 장소·리뷰 분석 결과를 미리 캐시에 채운다.

    python scripts/prefetch.py                # 전 언어, 장소당 리뷰 분석
    python scripts/prefetch.py --langs en ko  # 일부 언어만
    python scripts/prefetch.py --limit 5      # 지역당 상위 5곳만

로컬 Qwen은 리뷰 1건에 4~8초가 걸리므로, 발표 직전이 아니라 미리 돌려 두는 것을 권장한다.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import catalog  # noqa: E402
from config import LANGS, REGIONS  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=list(LANGS), choices=list(LANGS))
    ap.add_argument("--regions", nargs="+", default=list(REGIONS), choices=list(REGIONS))
    ap.add_argument("--limit", type=int, default=12, help="지역당 분석할 장소 수")
    args = ap.parse_args()

    for region in args.regions:
        for lang in args.langs:
            data = catalog.list_places(region, lang)
            places = data["places"][: args.limit]
            print(f"[{region}/{lang}] {data['source']} · 장소 {len(places)}곳")
            for p in places:
                t0 = time.time()
                try:
                    foreign = p.get("foreign") or {}
                    catalog.place_detail(p["id"], p["type_id"], lang, foreign.get("id", ""), foreign.get("type_id", ""))
                except Exception as e:  # 상세가 없어도 리뷰 분석은 계속
                    print(f"   상세 실패: {e}")
                summary = {}
                for event in catalog.review_stream(p["id"], p["title_ko"], region, lang, p["title"]):
                    if event["type"] == "summary":
                        summary = event["trust"]
                print(f"   {p['title_ko']:<20} 리뷰 {summary.get('total', 0)}건 "
                      f"(신뢰 {summary.get('trusted', 0)} / 의심 {summary.get('flagged', 0)}) {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
