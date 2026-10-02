// LocalPass 코드 설명서 (A4 2매 이내) — docx-js
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, BorderStyle, LevelFormat, VerticalAlign, Footer, PageNumber, TableLayoutType, LineRuleType,
} = require("docx");

const OUT = process.argv[2] || "LocalPass_코드설명서.docx";
const FONT = "Noto Sans KR";
const INK = "1E2233", SUB = "4A5068", RED = "C8283F", PINK = "FBE4E7", GRAY = "F3F3F6", LINE = "D5D7DE";
const BLUE = "DCEBF5", GREEN = "E2EADB";
const W = 10206; // A4 폭 11906 − 좌우 여백 850×2
const BODY = 19;  // 9.5pt (half-points)
const EX = LineRuleType.EXACT;
const FONTS = { ascii: FONT, hAnsi: FONT, eastAsia: FONT, cs: FONT };
const TR = (o) => new TextRun({ font: FONTS, ...o });

// **굵게**, `코드` 표기를 TextRun으로
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(TR({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(TR({ text: t.slice(2, -2), bold: true, ...base }));
    else out.push(TR({ text: t.slice(1, -1), font: "Consolas", size: (base.size || BODY) - 1, color: INK }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(TR({ text: text.slice(last), ...base }));
  return out;
}
const P = (text, opt = {}) => new Paragraph({ children: runs(text, opt.run || {}), spacing: { after: opt.after ?? 30, line: opt.line ?? 282, lineRule: EX }, alignment: opt.align, keepNext: opt.keepNext });
const B = (text, level = 0) => new Paragraph({ children: runs(text), numbering: { reference: "dot", level }, spacing: { after: 26, line: 282, lineRule: EX } });
const N = (text) => new Paragraph({ children: runs(text), numbering: { reference: "step", level: 0 }, spacing: { after: 24, line: 282, lineRule: EX } });
const H = (num, title) => new Paragraph({
  children: [TR({ text: `${num}. `, bold: true, color: RED, size: 22 }), TR({ text: title, bold: true, color: INK, size: 22 })],
  spacing: { before: 150, after: 70 }, keepNext: true,
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: INK, space: 2 } },
});

const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const thin = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const cellM = { top: 36, bottom: 36, left: 90, right: 90 };
function cell(content, width, o = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map((c) =>
    c instanceof Paragraph ? c : new Paragraph({ children: runs(c, { size: o.size || 18, bold: o.bold, color: o.color }), alignment: o.align, spacing: { after: 0, line: 262, lineRule: EX } }));
  return new TableCell({
    children: paras, width: { size: width, type: WidthType.DXA }, columnSpan: o.span,
    shading: o.fill ? { type: ShadingType.CLEAR, color: "auto", fill: o.fill } : undefined,
    verticalAlign: o.valign || VerticalAlign.CENTER, margins: o.margins || cellM,
    borders: o.borders || { top: thin, bottom: thin, left: thin, right: thin },
  });
}
function table(widths, rows, o = {}) {
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: rows.map((r, ri) => new TableRow({
      cantSplit: true, tableHeader: o.header && ri === 0,
      children: r.map((c, ci) => {
        const head = o.header && ri === 0;
        const spec = typeof c === "object" && !Array.isArray(c) && !(c instanceof Paragraph) ? c : { t: c };
        const width = spec.span ? widths.slice(ci, ci + spec.span).reduce((a, b) => a + b, 0) : widths[ci];
        return cell(spec.t, width, {
          span: spec.span, fill: head ? INK : spec.fill || (o.firstColFill && ci === 0 ? GRAY : undefined),
          bold: head || spec.bold || (o.firstColBold && ci === 0), color: head ? "FFFFFF" : spec.color, size: o.size,
        });
      }),
    })),
  });
}
const gap = (after = 60) => new Paragraph({ children: [], spacing: { after, line: 120 } });

// ── 본문 ─────────────────────────────────────────────────────
const children = [];

// 머리
children.push(new Paragraph({
  children: [TR({ text: "2026 지역혁신 인재양성 연합 페스티벌 · AI·DX 산출물", size: 17, color: SUB }),
             TR({ text: "   코드 설명서", size: 17, bold: true, color: RED })],
  spacing: { after: 30 },
}));
children.push(new Paragraph({
  children: [TR({ text: "LocalPass", bold: true, size: 40, color: INK }),
             TR({ text: "  외국인 관광객을 위한 로컬 후기 신뢰도 필터링 서비스", bold: true, size: 26, color: INK })],
  spacing: { after: 90 },
}));
const L = (t) => ({ t, fill: GRAY, bold: true });
children.push(table([1300, 3800, 1300, 3806], [
  [L("팀"), "류황규 · 박건우 · 홍승우 · 황지룡", L("지원 분야"), "AI·DX 산출물"],
  [L("서비스 주소"), "https://localpass-kappa.vercel.app", L("제출물"), "코드 설명서, 코드 결과(PPT 20장), 소스 코드"],
], { size: 17 }));

// 1. 배경
children.push(H(1, "개발 배경과 목적"));
children.push(B("외국인이 주로 쓰는 구글맵은 한국 데이터가 부실하고, 가장 믿을 만한 **네이버 블로그 후기는 한국어로만 유통**됩니다. 번역해도 **협찬·광고 글과 AI가 쓴 글은 가려낼 수 없고**, 광고 수익 구조상 콘텐츠가 유명 장소에 쏠려 **지방은 정보 사각지대**로 남습니다."));
children.push(B("LocalPass는 공공 관광데이터(TourAPI)와 블로그 후기를 결합하고 **협찬 여부와 AI 작성 여부를 이중으로 걸러** 진짜 사람이 쓴 후기만 영어·일본어·중국어·한국어로 보여줍니다. 조사한 경쟁 서비스 6곳(크리에이트립, 망고플레이트, 와그, 트래지, 캐치테이블, 네이버지도)에는 이런 검증 기능이 없습니다."));

// 2. 주요 기능
children.push(H(2, "주요 기능"));
children.push(table([1750, 8456], [
  ["구분", "내용"],
  ["장소 탐색", "지역 6곳(성수·전주·부산·강릉·경주·제주)과 전국 키워드 검색, 카테고리 탭(관광지·문화시설·축제·전통시장·맛집), 관심사 9종 필터, 신뢰도순·거리순·이름순 정렬"],
  ["장소 상세", "TourAPI 공식 정보(주소·이용시간·쉬는 날·요금·소개)를 관광공사 공식 외국어 번역으로 우선 표시하고, 없으면 Qwen 번역에 '기계 번역' 표시"],
  ["후기 신뢰도 분석", "장소별 네이버 블로그 후기 6건을 7단계로 검사해 도장 배지(신뢰·참고·의심·차단), 신뢰도 점수, 판단 근거, 번역 요약을 끝나는 대로 한 건씩 표시 (진행 건수·경과 시간 표시)"],
  ["의심 후기 처리", "의심·차단 후기는 기본으로 숨기되 지우지 않고, 펼치면 판단 근거를 공개. 한국어 원문과 블로그 원본 링크 제공"],
  ["직접 후기 검사", "후기를 붙여 넣으면 같은 7단계로 검사 (샘플: 진짜 후기 · 협찬 글 · 프롬프트 인젝션)"],
  ["다국어 · 모바일", "화면 문구·후기 요약·장소명 4개 언어, 한글 원래 이름 병기, 스마트폰(390px) 대응, 키보드 초점·'움직임 줄이기' 설정 지원"],
  ["GPU 온디맨드", "AI 서버는 사이트를 쓸 때만 켜지고 5분간 쓰지 않으면 꺼짐. 켜지는 동안(2~4분) 화면 하단에 경과 시간 안내"],
], { header: true, firstColFill: true, firstColBold: true }));

// 3. 시스템 구성
children.push(H(3, "시스템 구성과 기술 스택"));
const box = (fill, lines) => lines.map((l, i) => new Paragraph({ children: runs(l, { size: i === 0 ? 18 : 16, bold: i === 0, color: i === 0 ? INK : SUB }), spacing: { after: i === 0 ? 20 : 0, line: i === 0 ? 250 : 222, lineRule: EX } }));
const arrow = () => new Paragraph({ children: [TR({ text: "→", size: 26, bold: true, color: SUB })], alignment: AlignmentType.CENTER });
const noB = { top: none, bottom: none, left: none, right: none };
const svc = (fill, title, desc) => new TableCell({
  children: box(fill, [title, desc]), width: { size: 3850, type: WidthType.DXA },
  shading: { type: ShadingType.CLEAR, color: "auto", fill }, margins: { top: 30, bottom: 30, left: 110, right: 90 },
  borders: { top: { style: BorderStyle.SINGLE, size: 12, color: "FFFFFF" }, bottom: { style: BorderStyle.SINGLE, size: 12, color: "FFFFFF" }, left: none, right: none },
  verticalAlign: VerticalAlign.CENTER,
});
const services = [
  [GRAY, "한국관광공사 TourAPI 4.0", "장소·축제·운영시간, 공식 번역(국·영·일·중)"],
  [GRAY, "NAVER API HUB 블로그 검색", "후기 원문 후보 (검색 API 요약만 사용)"],
  [BLUE, "Modal GPU(L4) · Qwen2.5-7B-Instruct", "vLLM · 보안 분류 · 협찬 문맥 · 번역 · 요약"],
  [BLUE, "Modal CPU · Fast-DetectGPT", "Qwen2.5-1.5B 기반 AI 작성 확률"],
];
children.push(new Table({
  width: { size: W, type: WidthType.DXA }, columnWidths: [1750, 420, 3766, 420, 3850], layout: TableLayoutType.FIXED,
  rows: services.map((s, i) => new TableRow({
    children: [
      ...(i === 0 ? [
        new TableCell({ rowSpan: 4, width: { size: 1750, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: "auto", fill: GRAY }, borders: noB, margins: { top: 60, bottom: 60, left: 110, right: 80 }, verticalAlign: VerticalAlign.CENTER,
          children: box(GRAY, ["외국인 관광객", "브라우저 · 모바일", "영·일·중·한"]) }),
        new TableCell({ rowSpan: 4, width: { size: 420, type: WidthType.DXA }, borders: noB, verticalAlign: VerticalAlign.CENTER, children: [arrow()] }),
        new TableCell({ rowSpan: 4, width: { size: 3766, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: "auto", fill: INK }, borders: noB, margins: { top: 80, bottom: 80, left: 130, right: 100 }, verticalAlign: VerticalAlign.CENTER,
          children: [
            new Paragraph({ children: [TR({ text: "Vercel · FastAPI (서울 리전)", bold: true, size: 19, color: "FFFFFF" })], spacing: { after: 50 } }),
            ...["① 개인정보 비식별화 · 인젝션 규칙 차단", "② 협찬 표기 규칙 · 신뢰도 점수 · 도장 배지", "③ 장소·후기 조회, 관련 글 선별, 캐시", "④ 원격 GPU 기동 상태 확인 (콜드 스타트 안내)"]
              .map((t) => new Paragraph({ children: [TR({ text: t, size: 16, color: "E6E8F0" })], spacing: { after: 20, line: 228, lineRule: EX } })),
          ] }),
        new TableCell({ rowSpan: 4, width: { size: 420, type: WidthType.DXA }, borders: noB, verticalAlign: VerticalAlign.CENTER, children: [arrow()] }),
      ] : []),
      svc(...s),
    ],
  })),
}));
children.push(gap(70));
children.push(table([1750, 4300, 4156], [
  ["구성", "기술", "비고"],
  ["화면", "HTML · CSS · JavaScript (프레임워크 없음)", "4개 언어, 반응형, NDJSON 실시간 스트리밍"],
  ["서버", "Python · FastAPI · Pydantic · requests", "Vercel Hobby(무료), 함수 최대 300초"],
  ["AI 모델", "Qwen2.5-7B-Instruct(vLLM), Fast-DetectGPT", "Modal 무료 크레딧 월 $30, 사용 시에만 과금"],
  ["테스트 · 관리", "pytest 35개, GitHub 비공개 저장소", "API 키는 저장소에 두지 않음"],
], { header: true, firstColFill: true, firstColBold: true }));
children.push(P("**주요 소스** `app.py` API 서버 · `catalog.py` 장소·후기 서비스 계층 · `ai_pipeline/trust_filter.py` 판정 핵심 · `security/` 개인정보·인젝션 · `data_sources/` TourAPI·네이버 · `static/` 화면 · `deploy/` Modal 배포", { run: { size: 16, color: SUB }, after: 0, line: 250 }));

// 4. 핵심 로직
children.push(H(4, "핵심 로직 — 신뢰도 판정 7단계"));
children.push(N("**수집**: TourAPI 좌표·반경 조회(`locationBasedList2`, 반경 1.5km)로 장소를 모으고, 네이버 블로그 검색(최신순+관련도순)에서 장소명이 들어간 글만 고름. 본문에만 스치듯 나온 글은 지역명도 있어야 인정"));
children.push(N("**개인정보 가리기**: 전화·이메일·주민번호·카드·계좌·메신저 ID를 정규식으로 가리고 건수 표시 (`security/pii.py`)"));
children.push(N("**숨은 명령 1차 차단**: '이전 지시 무시' 같은 한·영 인젝션 규칙에 걸리면 AI에 보내지 않고 '차단' (`security/injection.py`)"));
children.push(N("**협찬 표기 찾기**: 공정위 지침 표기(협찬·제공받아·원고료·체험단·#광고 등)가 있으면 협찬 확정 (`sponsor_rules.py`)"));
children.push(N("**문맥 읽기 (Qwen2.5-7B)**: 보안 2차 분류(정상·의심·차단), 표기 없는 홍보의 협찬 등급(none·possible·likely·explicit), AI 문체 등급, 번역·요약을 JSON 스키마로만 받음. 7B 모델이 숫자 점수를 일관되게 못 매겨 등급으로 받고 코드에서 점수화"));
children.push(N("**AI 작성 판별**: Fast-DetectGPT(Qwen2.5-1.5B) 확률과 Qwen 문체 신호를 평균. 한 모델로 확정하지 않으며 60자 미만은 판별하지 않음"));
children.push(N("**판정 도장**: 아래 식으로 점수를 내고 배지를 붙임. AI 분석이 실패하면 근거가 부족하므로 최대 '참고'(0.6)로 제한"));
children.push(new Paragraph({
  children: runs("신뢰도 = 1.0 − 협찬(표기 발견 0.5 / 없으면 0.5 × 문맥 등급 0~0.95) − 0.5 × AI 작성 확률 − 0.2(보안 '의심')", { size: 17, bold: true, color: INK }),
  shading: { type: ShadingType.CLEAR, color: "auto", fill: PINK }, spacing: { before: 40, after: 50, line: 250, lineRule: EX }, indent: { left: 120, right: 120 },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: RED, space: 6 } },
}));
children.push(table([1750, 4700, 3756], [
  ["배지", "조건", "화면 표시"],
  [{ t: "신뢰", color: "1F6F57", bold: true }, "점수 0.70 이상", "기본 노출"],
  [{ t: "참고", color: "9A6410", bold: true }, "0.40 이상 0.70 미만, 또는 AI 분석 실패", "기본 노출"],
  [{ t: "협찬·AI 의심", color: RED, bold: true }, "협찬 판정(표기 발견 또는 문맥 likely 이상), 또는 0.40 미만", "기본 숨김, 펼치면 근거 공개"],
  [{ t: "차단", bold: true }, "프롬프트 인젝션 탐지", "분석하지 않고 사유만 표시"],
], { header: true, firstColFill: true }));

// 5. 보안
children.push(H(5, "보안 설계"));
children.push(B("**인젝션 3중 방어**: ① 규칙 탐지로 차단 ② Qwen 보안 분류 ③ 외부 글은 시스템 프롬프트가 아닌 `<review>` 데이터 태그로만 전달하고 태그 탈출 문자열·특수 토큰 제거. 모델 출력은 JSON 스키마 + Pydantic 검증, 모델에 도구·권한 없음"));
children.push(B("**키·접근 관리**: API 키는 `.env`, Vercel 환경변수(민감 값), Modal Secret에만 보관하고 저장소에 커밋하지 않음. Modal GPU·판별기는 API 키 인증(키 없이 호출하면 401)"));
children.push(B("**수집 최소화**: 네이버 블로그 robots.txt가 AI·RAG 목적 봇을 금지하므로 본문을 크롤링하지 않고 공식 검색 API 요약만 사용. 사용자 계정·개인정보는 수집하지 않으며, 블로그 글은 `textContent`로만 출력해 스크립트 실행(XSS) 차단"));

// 6. 실행
children.push(H(6, "실행 방법"));
children.push(B("**웹(설치 불필요)**: https://localpass-kappa.vercel.app 접속 → 지역 선택 → 장소 카드 → '후기 검사'. GPU가 꺼져 있으면 첫 분석 전 2~4분간 켜지며 하단에 경과 시간이 표시됨"));
children.push(B("**로컬**: `pip install -r requirements.txt` → `.env.example`을 `.env`로 복사해 키 입력(없으면 샘플 데이터로 동작) → `python app.py` → http://127.0.0.1:8000. 언어 모델은 Ollama(`qwen2.5:7b-instruct`) 또는 `deploy/modal_qwen.py`로 Modal에 배포. 테스트 `python -m pytest -q`"));

// 7. 검증과 한계
children.push(H(7, "검증 결과와 한계"));
children.push(B("**AI 작성 판별기**: KatFish 한국어 벤치마크(ACL 2025)로 보정하고, 보정에 쓰지 않은 200건으로 평가. 1,000자 AUROC 0.76(에세이 0.92), 블로그 요약 길이인 200자에서는 0.66"));
children.push(B("**실제 데이터 시연**: 성수 '누메로뜨레쓰' 후기 6건 → 신뢰 3 · 참고 1 · 의심 2 (해시태그 홍보, 할인·예약 유도 탐지). 직접 검사: 협찬 글 '의심'(37점), 진짜 후기 '신뢰'(89점), 인젝션 '차단'과 개인정보 1건 가림. 단위 테스트 35개 통과, Modal 판별기와 로컬 계산 점수 일치"));
children.push(B("**한계**: AI 작성 판별은 증거가 아닌 참고 지표이며 짧은 글에서 정확도가 떨어짐. 판별기 보정 데이터(에세이·논문 초록)는 블로그 후기와 분야가 다름. 7B 모델은 고유명사 번역을 틀릴 수 있어 한글 원래 이름을 함께 표시하고 공식 번역을 우선함. 표기 없는 협찬은 완벽히 잡지 못하므로 근거를 공개하고, 숨기되 지우지 않음"));

// 8. 기대 효과
children.push(H(8, "기대 효과와 향후 계획"));
children.push(B("외국인 관광객도 한국인처럼 로컬 후기를 신뢰도와 함께 보고 고를 수 있고, 광고 예산 없는 지방·골목 상권도 노출됨"));
children.push(B("지역은 좌표만 추가하면 전국으로 확장(추가 크롤링 없음). 향후 블로그 후기 라벨 데이터로 판별기를 다시 보정하고, 후기 출처를 넓혀 판정 정확도를 높일 계획"));

const doc = new Document({
  creator: "LocalPass 팀", title: "LocalPass 코드 설명서",
  // 문서 기본 글꼴(docDefaults)에 Noto Sans KR을 넣으면 Word PDF에서 한글이 맑은 고딕으로 바뀐다 → 글꼴은 TR()에서만 지정
  styles: { default: { document: { run: { size: BODY, color: INK } } } },
  numbering: { config: [
    { reference: "dot", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 260, hanging: 200 } }, run: { color: RED, font: FONTS } } }] },
    { reference: "step", levels: [{ level: 0, format: LevelFormat.DECIMAL_ENCLOSED_CIRCLE, text: "%1", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 300, hanging: 260 } }, run: { color: RED, bold: true, font: FONTS } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 720, bottom: 720, left: 850, right: 850, footer: 360 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      TR({ text: "LocalPass 코드 설명서  ", size: 15, color: SUB }),
      TR({ children: [PageNumber.CURRENT], size: 15, color: SUB }), TR({ text: " / ", size: 15, color: SUB }),
      TR({ children: [PageNumber.TOTAL_PAGES], size: 15, color: SUB }),
    ] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT); });
