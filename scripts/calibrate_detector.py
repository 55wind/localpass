"""로컬 AI 판별기(Fast-DetectGPT) 보정 — KatFish 한국어 벤치마크(ACL 2025)의 사람/LLM 글로
점수 분포를 구해 data/detector_calibration.json 에 저장하고 AUROC를 출력한다.

    git clone https://github.com/Shinwoo-Park/katfishnet  (또는 katfish_dataset/*.jsonl 만 내려받기)
    python scripts/calibrate_detector.py --katfish <katfish_dataset 폴더>

- short: 앞 200자만 사용 (네이버 검색 API 요약문 길이에 맞춤)
- long : 앞 1000자 사용 (직접 붙여 넣은 후기 검사용)
- 절반으로 보정(분포 추정), 나머지 절반으로 평가해 과적합된 수치를 피한다.
"""
import argparse
import json
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_pipeline import local_detector  # noqa: E402
from config import DETECTOR_MODEL, ROOT  # noqa: E402

BUCKETS = {"short": 200, "long": 1000}


def auroc(pos: list[float], neg: list[float]) -> float:
    """Mann–Whitney U 기반 AUROC (pos 점수가 neg보다 클 확률)."""
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def best_threshold(pos: list[float], neg: list[float]) -> float:
    """Youden's J(TPR - FPR)가 최대인 임계값."""
    best, best_j = 0.0, -1.0
    for t in sorted(pos + neg):
        j = sum(p >= t for p in pos) / len(pos) - sum(n >= t for n in neg) / len(neg)
        if j > best_j:
            best, best_j = t, j
    return best


def load(katfish: Path, genres: list[str], per_class: int, seed: int) -> list[dict]:
    rows = []
    for g in genres:
        data = [json.loads(line) for line in (katfish / f"{g}.jsonl").open(encoding="utf-8")]
        rng = random.Random(seed)
        for label in (0, 1):  # 0 = 사람, 1 = LLM
            group = [r for r in data if int(r["label"]) == label and len(r["text"]) >= 120]
            rng.shuffle(group)
            rows += [{"genre": g, "label": label, "text": r["text"], "by": r.get("written_by", "")}
                     for r in group[:per_class]]
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--katfish", type=Path, required=True)
    ap.add_argument("--genres", nargs="+", default=["essay", "abstract"])
    ap.add_argument("--per-class", type=int, default=100, help="장르·라벨별 표본 수")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rows = load(args.katfish, args.genres, args.per_class, args.seed)
    print(f"표본 {len(rows)}개 (사람 {sum(r['label'] == 0 for r in rows)} / LLM {sum(r['label'] == 1 for r in rows)})")
    t0 = time.time()
    for i, r in enumerate(rows):
        for b, n in BUCKETS.items():
            r[b] = local_detector.discrepancy(r["text"][:n])
        if i % 50 == 0:
            print(f"  {i}/{len(rows)}  {time.time() - t0:.0f}s")

    random.Random(args.seed).shuffle(rows)
    fit, held = rows[::2], rows[1::2]
    out = {"model": DETECTOR_MODEL, "method": "Fast-DetectGPT analytic (same reference/scoring model)",
           "dataset": f"KatFish {'+'.join(args.genres)}", "n_fit": len(fit), "n_eval": len(held)}
    for b in BUCKETS:
        human = [r[b] for r in fit if r["label"] == 0]
        ai = [r[b] for r in fit if r["label"] == 1]
        h_eval = [r[b] for r in held if r["label"] == 0]
        a_eval = [r[b] for r in held if r["label"] == 1]
        thr = best_threshold(ai, human)
        out[b] = {
            "chars": BUCKETS[b],
            "human": {"mu": statistics.mean(human), "sigma": statistics.stdev(human)},
            "ai": {"mu": statistics.mean(ai), "sigma": statistics.stdev(ai)},
            "threshold": thr,
            "auroc_eval": round(auroc(a_eval, h_eval), 4),
            "tpr_eval": round(sum(a >= thr for a in a_eval) / len(a_eval), 4),
            "fpr_eval": round(sum(h >= thr for h in h_eval) / len(h_eval), 4),
        }
        per_genre = {}
        for g in args.genres:
            ge = [r for r in held if r["genre"] == g]
            per_genre[g] = round(auroc([r[b] for r in ge if r["label"] == 1], [r[b] for r in ge if r["label"] == 0]), 4)
        out[b]["auroc_eval_by_genre"] = per_genre
        print(f"[{b}] AUROC {out[b]['auroc_eval']}  TPR {out[b]['tpr_eval']}  FPR {out[b]['fpr_eval']}  {per_genre}")

    path = ROOT / "data" / "detector_calibration.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {path}")


if __name__ == "__main__":
    main()
