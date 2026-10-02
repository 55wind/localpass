# LocalPass — 외국인 관광객을 위한 로컬 정보 신뢰도 필터링 서비스

공공 관광데이터(TourAPI)와 네이버 블로그 후기를 결합하고, **협찬 여부·AI 작성 여부를 이중으로 걸러** 다국어(영·일·중·한)로 보여주는 웹 서비스입니다.
2026 지역혁신 인재양성 연합 페스티벌 · AI·DX 산출물 (팀: 류황규, 박건우, 홍승우, 황지룡)

## 실행

```bash
# 1) 파이썬 3.11 가상환경
py -3.11 -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 2) Qwen2.5-7B-Instruct (로컬, GPU 약 5GB)
ollama pull qwen2.5:7b-instruct
#    AI 작성 판별용 Qwen2.5-1.5B(약 3GB)는 처음 쓸 때 .models/ 에 자동으로 내려받습니다
#    (PyTorch CUDA: pip install torch --index-url https://download.pytorch.org/whl/cu124)

# 3) API 키 (선택 — 없으면 샘플 데이터로 동작)
copy .env.example .env             # 값 채우기

# 4) 실행 → http://127.0.0.1:8000
python app.py
```

- API 키가 하나도 없어도 **샘플 데이터(성수동·전주) + 실제 Qwen 분석**으로 전체 흐름을 시연할 수 있습니다.
- 발표 전 `python scripts/prefetch.py` 로 분석 결과를 캐시에 미리 채워 두면 화면이 즉시 뜹니다 (리뷰 1건당 Qwen 4~8초).
- 테스트: `python -m pytest -q`

## 필요한 API 키

| 키 | 발급처 | 용도 | 없을 때 |
|---|---|---|---|
| `TOUR_API_KEY` | data.go.kr → "한국관광공사_국문 관광정보 서비스_GW" + 영문·일문·중문 서비스 각각 활용신청 | 장소·축제·운영시간, 공식 외국어 번역 | 샘플 장소 |
| `NAVER_CLIENT_ID/SECRET` | NAVER API HUB (네이버 클라우드 콘솔) → 블로그 검색 선택 → 애플리케이션 등록 | 블로그 후기 수집 (현재 임시 무료) | 샘플 후기 |
| (없음) | — | AI 작성 판별: **무료 로컬 판별기**(Fast-DetectGPT + Qwen2.5-1.5B)가 기본 | — |
| `GPTZERO_API_KEY` (선택) | gptzero.me 유료 API | 넣으면 GPTZero로 전환 | 로컬 판별기 사용 |
| `LLM_*` | 로컬 Ollama (기본값) 또는 OpenRouter 등 OpenAI 호환 API | 보안 분석·협찬 판단·번역 | 규칙 기반 검사만 (최대 '참고' 배지) |

> TourAPI는 **디코딩(Decoding) 키**를 넣어야 합니다. 인코딩 키를 넣으면 이중 인코딩으로 `SERVICE_KEY_IS_NOT_REGISTERED` 오류가 납니다.
> 외국어 서비스(EngService2 등)는 국문과 **별도로 활용신청**해야 공식 번역이 나옵니다. 신청하지 않으면 Qwen 번역으로 대체됩니다.

## 신뢰도 파이프라인

```
수집 원문 (네이버 블로그 검색 API 요약)
 → ① 개인정보 비식별화        security/pii.py        전화·이메일·주민·카드·계좌·메신저ID 마스킹
 → ② 인젝션 1차 규칙 탐지     security/injection.py   차단 시 LLM에 전달하지 않음, ChatML 토큰 제거
 → ③ 협찬 표기 규칙           ai_pipeline/sponsor_rules.py  공정위 표기(협찬·제공받아·원고료·체험단…)
 → ④ Qwen 2차 보안 분석       정상 / 의심 / 차단 (구조화 출력만 반환)
 → ⑤ Qwen 문맥 분석·번역      표기 없는 홍보 판단, AI 문체 보조 신호, 다국어 요약
 → ⑥ AI 작성 판별             로컬 Fast-DetectGPT(무료, 기본) 또는 GPTZero — 원문(한국어) 기준
 → ⑦ 신뢰도 점수·도장         신뢰 / 참고 / 협찬·AI 의심 / 차단
```

- 외부 글은 시스템 프롬프트에 넣지 않고 `<review>` 태그 안의 **데이터**로만 전달하며, 태그 탈출 문자열을 무력화합니다.
- 모델 출력은 JSON 스키마로 강제(Ollama `json_schema`)하고 Pydantic으로 검증합니다. 7B 모델이 숫자 점수를 일관되게 못 매겨 **등급(none/possible/likely/explicit)** 으로 받아 코드에서 점수화합니다.
- LLM 분석이 실패하거나 꺼져 있으면 근거가 부족하므로 '신뢰'를 주지 않고 최대 '참고'로 제한합니다.
- 프론트엔드는 블로그 원문을 `textContent`로만 렌더링합니다(XSS 방지).

## 구조

```
app.py                 FastAPI 서버 (API + 정적 파일)
catalog.py             장소·상세·리뷰 스트리밍 서비스 계층 (실데이터 ↔ 샘플 전환)
config.py              환경변수, 지역·카테고리 설정
data_sources/          tour_api.py (TourAPI 4.0), naver_blog.py (NAVER API HUB 블로그 검색)
security/              pii.py, injection.py
ai_pipeline/           trust_filter.py (핵심), llm.py (Qwen), ai_detect.py, local_detector.py (Fast-DetectGPT), translate.py, schema.py
merge.py               장소 ↔ 블로그 글 매칭, 신뢰도 요약
personalize.py         관심사 태그·정렬
static/                index.html, styles.css, app.js, i18n.js
data/demo/             API 키 없을 때 쓰는 샘플 (리뷰는 데모용 가상 글)
scripts/prefetch.py    시연 전 캐시 예열
scripts/calibrate_detector.py  KatFish 벤치마크로 AI 판별기 보정 → data/detector_calibration.json
tests/                 규칙 모듈 단위 테스트
```

## 설계 문서 대비 변경점

| 항목 | 설계 문서 | 구현 | 이유 |
|---|---|---|---|
| 프론트엔드 | Streamlit | FastAPI + HTML/CSS/JS | 한국관광공사·공정관광 사이트 수준의 디자인 구현, 리뷰 분석 결과 실시간 스트리밍 |
| LLM | Claude Sonnet | Qwen2.5-7B-Instruct (보안추가본 기준) | 로컬 실행으로 외부 전송 없음, OpenAI 호환이라 호스팅 전환 쉬움 |
| 지역 조회 | `areaCode` / `sigunguCode` | 좌표+반경(`locationBasedList2`), 축제는 법정동 코드 | 2025 TourAPI 개편으로 areaCode는 삭제 예정 |
| 블로그 본문 | iframe 크롤링(선택) | 검색 API 요약만 사용 | 네이버 블로그 robots.txt가 AI·RAG 목적 봇 접근을 명시적으로 금지 |
| AI 작성 판별 | GPTZero API (유료) | Fast-DetectGPT 로컬 판별기 (무료, GPTZero는 선택) | 비용 0원, 리뷰 원문이 외부 서비스로 나가지 않음 |

## 한계 (코딩설명서 기재용)

- AI 작성 판별은 **참고 지표**입니다. 검색 API 요약은 짧아(약 100~200자) 판별 신뢰도가 떨어지며, 60자 미만은 판별하지 않습니다.
  로컬 판별기는 학생 에세이·논문 초록(KatFish)으로 보정했기 때문에 블로그 후기에서는 성능이 다를 수 있습니다. 보정 결과는 `data/detector_calibration.json` 참고.
- Qwen 7B는 고유명사 음차·번역에서 가끔 오류를 냅니다. 공식 번역(TourAPI 외국어 서비스)을 1순위로, 장소명은 원문에 공식 표기를 덧붙여 보정합니다.
- 협찬 문맥 판단은 표기 없는 홍보를 완벽히 잡지 못합니다. 판정 근거를 화면에 그대로 보여주고, 의심 글도 숨기지 않고 토글로 볼 수 있게 했습니다.
