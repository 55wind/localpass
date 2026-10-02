// LocalPass 기능명세서 (.pptx) — pptxgenjs, 구조화 덱(테마·레이아웃·섹션)
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("C:/Users/nthin/.claude/skills/synced/852e62f4-8860-4507-9905-9f406e349d53_af7062a4-7454-4963-a2a6-4470897d45ee/pptx/scripts/apply_theme.js");

const OUT = process.argv[2] || "LocalPass_기능명세서.pptx";
const IMG = (n) => path.join(__dirname, "img", n);
const URL = "https://localpass-kappa.vercel.app";

const THEME = {
  name: "LocalPass",
  headFontFace: "Noto Sans KR",
  bodyFontFace: "Noto Sans KR",
  colors: {
    dk1: "1E2233", lt1: "FFFFFF", dk2: "4A5068", lt2: "F5F5F7",
    accent1: "C8283F", accent2: "1F6F57", accent3: "9A6410",
    accent4: "FBE4E7", accent5: "DCEBF5", accent6: "E2EADB",
    hlink: "C8283F", folHlink: "4A5068",
  },
};
const MUTED = "868B9E";      // 각주·쪽번호 (hex 전용 옵션용)
const BORDER = "D9DBE3";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "LocalPass 기능명세서";
pres.author = "류황규, 박건우, 홍승우, 황지룡";
pres.company = "2026 지역혁신 인재양성 연합 페스티벌";
const C = pres.SchemeColor;
const S = pres.ShapeType;

// ── 레이아웃 ────────────────────────────────────────────────
const footer = [
  { text: { text: "LocalPass 기능명세서", options: { x: 0.6, y: 7.0, w: 6, h: 0.32, fontSize: 11, color: C.text2, margin: 0 } } },
];
const slideNumber = { x: 12.15, y: 7.0, w: 0.6, h: 0.32, fontSize: 11, color: MUTED, align: "right" };

pres.defineSlideMaster({
  title: "COVER",
  background: { color: C.accent4 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", align: "left", x: 0.7, y: 1.35, w: 5.9, h: 2.1, fontSize: 46, bold: true, color: C.text1, valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: 0.7, y: 3.6, w: 5.9, h: 1.1, fontSize: 22, color: C.text2, valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "meta", type: "body", x: 0.7, y: 5.0, w: 5.9, h: 1.9, fontSize: 15, color: C.text2, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DIVIDER",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "num", type: "body", x: 0.7, y: 2.3, w: 4, h: 0.6, fontSize: 20, bold: true, color: C.accent4, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", align: "left", x: 0.7, y: 2.9, w: 11.9, h: 1.3, fontSize: 48, bold: true, color: C.background1, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "desc", type: "body", x: 0.7, y: 4.3, w: 11.5, h: 1.0, fontSize: 20, color: "C9CCD8", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    ...footer,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: 0.6, y: 0.38, w: 12.1, h: 0.8, fontSize: 30, bold: true, color: C.text1, valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber,
});
pres.defineSlideMaster({
  title: "FEATURE",
  background: { color: C.background1 },
  objects: [
    ...footer,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: 1.95, y: 0.38, w: 10.75, h: 0.8, fontSize: 30, bold: true, color: C.text1, valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber,
});
pres.defineSlideMaster({
  title: "CLOSING",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", align: "left", x: 0.7, y: 1.55, w: 12.1, h: 2.0, fontSize: 48, bold: true, color: C.background1, margin: 0, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 4.1, w: 11.9, h: 2.7, fontSize: 24, lineSpacingMultiple: 1.25, color: "C9CCD8", valign: "top", margin: 0 }, text: "" } },
  ],
});

// ── 공통 조각 ────────────────────────────────────────────────
function seal(slide, id, x = 0.6, y = 0.47) {
  slide.addText(id, {
    shape: S.roundRect, x, y, w: 1.15, h: 0.64, rectRadius: 0.1, rotate: -5,
    fill: { color: C.accent1 }, line: { color: C.accent1, width: 1 },
    color: C.background1, fontSize: id.length > 5 ? 14 : 17, bold: true, align: "center", valign: "middle", margin: 0,
    objectName: `seal ${id}`,
  });
}

// 스크린샷: 테두리 + 그림자 액자 위에 이미지
function shot(slide, file, x, y, w, h, name) {
  slide.addShape(S.rect, {
    x: x - 0.04, y: y - 0.04, w: w + 0.08, h: h + 0.08,
    fill: { color: C.background1 }, line: { color: BORDER, width: 0.75 },
    shadow: { type: "outer", blur: 8, offset: 2, angle: 90, color: "1E2233", opacity: 0.18 },
    objectName: `frame ${name}`,
  });
  slide.addImage({ path: IMG(file), x, y, w, h, objectName: `screen ${name}`, altText: name });
}

function caption(slide, text, x, y, w) {
  slide.addText(text, { x, y, w, h: 0.38, fontSize: 13, color: C.text2, margin: 0, isTextBox: true });
}

// 설명 패널: [{h: 소제목, items: [...]}, {h, text}]
function panel(slide, sections, x, y, w, h, size = 14.5) {
  const runs = [];
  sections.forEach((sec, si) => {
    runs.push({ text: sec.h, options: { bold: true, fontSize: size + 2, color: C.accent1, breakLine: true, paraSpaceBefore: si ? 14 : 0, paraSpaceAfter: 5 } });
    if (sec.text) runs.push({ text: sec.text, options: { fontSize: size - 0.5, color: C.text2, breakLine: true, paraSpaceAfter: 2 } });
    (sec.items || []).forEach((it) => runs.push({ text: it, options: { bullet: { indent: 15 }, fontSize: size, color: C.text1, breakLine: true, paraSpaceAfter: 6 } }));
  });
  delete runs[runs.length - 1].options.breakLine;
  slide.addText(runs, { x, y, w, h, valign: "top", margin: 0, lineSpacingMultiple: 0.95, isTextBox: true, objectName: "description" });
}

function featureSlide(id, title, section) {
  const s = pres.addSlide({ masterName: "FEATURE", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  seal(s, id);
  return s;
}

// 이미지 비율
const DESK = 1200 / 1920, DRAWER = 1440 / 989, MOBILE = 1688 / 780;

// ═════════════════════════════════════════════════════════════
// 1. 표지
pres.addSection({ title: "표지" });
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: "표지" });
  s.addText("LocalPass\n기능명세서", { placeholder: "title" });
  s.addText("외국인 관광객을 위한 로컬 후기 신뢰도 필터링 서비스", { placeholder: "sub" });
  s.addText([
    { text: "2026 지역혁신 인재양성 연합 페스티벌 · AI·DX 산출물", options: { breakLine: true } },
    { text: "팀  류황규 · 박건우 · 홍승우 · 황지룡", options: { breakLine: true } },
    { text: `서비스  ${URL}`, options: { breakLine: true, hyperlink: { url: URL } } },
    { text: "작성일  2026. 10. 02" },
  ], { placeholder: "meta" });
  shot(s, "00_hero_clean.jpg", 6.95, 1.55, 5.85, 5.85 * (1040 / 1920), "메인 화면");
  seal(s, "찐", 6.75, 1.2);
  // 사이트 바로가기 QR (스캔하면 운영 사이트로)
  s.addShape(S.roundRect, { x: 11.05, y: 4.95, w: 1.75, h: 2.05, rectRadius: 0.08, fill: { color: C.background1 }, line: { color: C.background1 }, objectName: "qr card" });
  s.addImage({ path: IMG("qr_site.png"), x: 11.15, y: 5.03, w: 1.55, h: 1.55, objectName: "qr site", altText: `사이트 QR 코드 ${URL}` });
  s.addText("사이트 바로가기", { x: 11.05, y: 6.6, w: 1.75, h: 0.32, fontSize: 12, bold: true, color: C.text1, align: "center", margin: 0, isTextBox: true });
}

// 2. 개요
pres.addSection({ title: "개요" });
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "개요" });
  s.addText("서비스 개요", { placeholder: "title" });
  s.addText("공공 관광데이터와 네이버 블로그 후기를 결합하고, 숨은 광고·AI 작성 글은 걸러내고 협찬 글은 표시해 진짜 사람의 로컬 추천을 다국어로 제공합니다.", {
    x: 0.6, y: 1.3, w: 12.1, h: 0.85, fontSize: 18, color: C.text2, margin: 0, isTextBox: true,
  });
  const cards = [
    { t: "문제", fill: C.accent4, k: "정보 접근 비대칭", b: ["신뢰도 높은 로컬 정보는 한국어 네이버 블로그에만 있음", "번역해도 숨은 광고·AI 작성 글을 외국인은 가려낼 수 없음", "광고 수익 구조상 유명 장소에만 콘텐츠가 쏠려 지방은 사각지대"] },
    { t: "해결", fill: C.accent6, k: "이중 신뢰도 필터 + 공식 데이터", b: ["한국관광공사 TourAPI로 전국 관광지·축제·전통시장 확보", "협찬 글은 '협찬 고지', 숨은 광고는 Qwen이 판단", "AI 작성: Fast-DetectGPT로 판별", "판정 근거를 도장 배지와 함께 투명하게 공개"] },
    { t: "차별점", fill: C.accent5, k: "경쟁 6곳 모두 검증 없음", b: ["크리에이트립, 망고플레이트, 와그, 트래지, 캐치테이블, 네이버지도 모두 신뢰도 검증 없음", "광고 수익과 이해상충이 없는 제3자 필터링", "개인정보 비식별화·프롬프트 인젝션 차단까지 포함"] },
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.1, y = 2.35, w = 3.85, h = 4.45;
    s.addShape(S.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: c.fill }, line: { color: c.fill }, objectName: `card ${c.t}` });
    s.addText(c.t, { x: x + 0.3, y: y + 0.28, w: w - 0.6, h: 0.42, fontSize: 16, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(c.k, { x: x + 0.3, y: y + 0.72, w: w - 0.6, h: 1.0, fontSize: 22, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    s.addText(c.b.map((t, j) => ({ text: t, options: { bullet: { indent: 15 }, breakLine: j < c.b.length - 1, paraSpaceAfter: 12 } })),
      { x: x + 0.3, y: y + 1.75, w: w - 0.5, h: h - 1.85, fontSize: 17, lineSpacingMultiple: 0.95, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  });
}

// 3. 시스템 구성도
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "개요" });
  s.addText("시스템 구성도", { placeholder: "title" });
  const box = (x, y, w, h, fill, title, body, name) => {
    s.addShape(S.roundRect, { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line: { color: BORDER, width: 0.75 }, objectName: name });
    s.addText([
      { text: title, options: { bold: true, fontSize: 15.5, color: C.text1, breakLine: !!body } },
      ...(body ? [{ text: body, options: { fontSize: 13, color: C.text2 } }] : []),
    ], { x: x + 0.18, y: y + 0.08, w: w - 0.36, h: h - 0.16, valign: "middle", margin: 0, isTextBox: true });
  };
  const arrow = (x1, y1, x2, y2) => s.addShape(S.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipV: y2 < y1, line: { color: C.text2, width: 1.5, endArrowType: "triangle" } });

  box(0.6, 2.85, 2.4, 1.8, C.background2, "외국인 관광객", "브라우저 · 모바일\n영·일·중·한 4개 언어", "user");
  // Vercel
  s.addShape(S.roundRect, { x: 3.5, y: 1.45, w: 4.3, h: 4.75, rectRadius: 0.12, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "vercel" });
  s.addText([{ text: "Vercel · FastAPI", options: { bold: true, fontSize: 18, color: C.background1, breakLine: true } },
             { text: "서울 리전(icn1) · 쓸 때만 실행", options: { fontSize: 13, color: "C9CCD8" } }],
    { x: 3.75, y: 1.6, w: 3.8, h: 0.75, margin: 0, valign: "top", isTextBox: true });
  ["① 개인정보 비식별화 · 인젝션 규칙 차단", "② 협찬 표기 규칙 · 신뢰도 점수 · 도장 배지", "③ 장소·후기 조회, 관련 글 선별, 캐시", "④ 원격 GPU 기동 상태 확인(콜드 스타트 안내)"].forEach((t, i) => {
    s.addText(t, { shape: S.roundRect, x: 3.75, y: 2.5 + i * 0.88, w: 3.8, h: 0.72, rectRadius: 0.08, fill: { color: "2E3348" }, line: { color: "2E3348" }, fontSize: 13, color: C.background1, margin: 6, valign: "middle", objectName: `vercel step ${i + 1}` });
  });
  arrow(3.0, 3.75, 3.5, 3.75);
  const ext = [
    [C.background2, "한국관광공사 TourAPI 4.0", "장소·축제·운영시간, 공식 번역(국·영·일·중)"],
    [C.background2, "NAVER API HUB · 블로그 검색", "후기 원문 후보 (공식 API 요약만 사용)"],
    [C.accent5, "Modal GPU (L4) · Qwen2.5-7B-Instruct", "vLLM · 보안 분석 · 협찬 문맥 판단 · 번역"],
    [C.accent5, "Modal CPU · Fast-DetectGPT", "Qwen2.5-1.5B 기반 AI 작성 판별"],
  ];
  ext.forEach(([fill, t, b], i) => {
    const y = 1.45 + i * 1.22;
    box(8.45, y, 4.25, 1.02, fill, t, b, `ext ${i + 1}`);
    arrow(7.8, 3.83, 8.45, y + 0.51);
  });
  s.addText("Modal 두 서비스는 요청이 있을 때만 켜지고, 마지막 사용 5분 뒤 자동으로 꺼집니다 (대기 중 요금 0원). 모든 원격 호출은 API 키로 인증합니다.", {
    x: 0.6, y: 6.35, w: 12.1, h: 0.55, fontSize: 14, color: C.text2, margin: 0, isTextBox: true });
}

// 4. 기능 목록
const FEATURES = [
  ["F-01", "메인 화면 · 언어 전환", "서비스 소개, 실제 검사 과정 데모, 전국 장소 검색창, 4개 언어 전환", "5"],
  ["F-02", "지역 선택", "성수 · 전주 · 부산 · 강릉 · 경주 · 제주 + 전국 검색, 좌표·반경 기반 조회", "6"],
  ["F-03", "장소 목록 · 카테고리", "관광지·문화시설·축제·전통시장·맛집 탭, 사진·번역명·후기 검사 요약 카드", "6"],
  ["F-04", "관심사 필터 · 정렬", "9개 관심사 다중 선택, 신뢰도순 · 가까운 순 · 이름순 정렬", "7"],
  ["F-05", "지방 커버리지 · 전국 검색", "지방 축제·전통시장, TourAPI 키워드 검색으로 전국 확장", "7"],
  ["F-06", "장소 상세 정보", "운영시간·요금·소개, 관광공사 공식 번역 우선 (없으면 Qwen 번역)", "8"],
  ["F-07", "후기 신뢰도 분석", "블로그 후기 7단계 검사, 도장 배지·점수·근거를 실시간 표시", "9"],
  ["F-08", "분석 진행 표시", "스피너 · n/6건 완료 · 경과 시간, 남은 후기 자리 표시", "10"],
  ["F-09", "의심 후기 숨김 · 근거 공개", "숨은 광고·AI 의심 글은 기본 숨김, 협찬 글은 '협찬 고지' 표시", "11"],
  ["F-10", "원문 확인", "개인정보가 가려진 한국어 원문 보기, 원본 글 링크", "11"],
  ["F-11", "직접 후기 검사", "후기를 붙여 넣어 같은 7단계로 검사, 샘플 3종 제공", "12"],
  ["F-12", "인젝션 차단 · 개인정보 가림", "AI 조작 문구 차단(분석 안 함), 연락처 등 비식별화", "12"],
  ["F-13", "다국어 지원", "화면·후기 요약·장소명·주소를 영·일·중·한으로, 출력 언어 검증", "13"],
  ["F-14", "GPU 온디맨드 · 콜드 스타트 안내", "쓸 때만 GPU 기동, 켜지는 동안 경과 시간 표시", "14"],
  ["F-15", "모바일 반응형", "390px 폭에서 모든 기능 제공", "15"],
];
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "개요" });
  s.addText("기능 목록", { placeholder: "title" });
  const head = ["기능 ID", "기능명", "설명", "쪽"].map((t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text1 } } }));
  const rows = FEATURES.map(([id, n, d, p]) => [
    { text: id, options: { bold: true, color: C.accent1 } }, { text: n, options: { bold: true } }, d, { text: p, options: { align: "center" } },
  ]);
  s.addTable([head, ...rows], {
    x: 0.6, y: 1.25, w: 12.1, colW: [1.0, 3.1, 7.4, 0.6], fontSize: 12.5, color: C.text1,
    border: { type: "solid", pt: 0.5, color: BORDER }, rowH: 0.35, valign: "middle", margin: [0.03, 0.06, 0.03, 0.06],
    fill: { color: C.background1 }, objectName: "feature table",
  });
}

// ═════════════════════════════════════════════════════════════
// 화면별 기능 명세
const SEC = "화면별 기능 명세";
pres.addSection({ title: SEC });
// 데스크톱 1장 + 오른쪽 설명
function deskFeature(id, title, file, sections, cap, size = 15) {
  const s = featureSlide(id, title, SEC);
  const w = 7.3, h = w * DESK;
  shot(s, file, 0.6, 1.5, w, h, title);
  if (cap) caption(s, cap, 0.6, 1.5 + h + 0.15, w);
  panel(s, sections, 8.25, 1.45, 4.5, 5.45, size);
  return s;
}
// 데스크톱 2장 나란히 + 아래 설명 2단
function deskPair(id, title, a, b, capA, capB, secA, secB, size = 15) {
  const s = featureSlide(id, title, SEC);
  const w = 5.5, h = w * DESK;
  shot(s, a, 0.6, 1.4, w, h, capA);
  shot(s, b, 7.2, 1.4, w, h, capB);
  caption(s, capA, 0.6, 1.4 + h + 0.12, w);
  caption(s, capB, 7.2, 1.4 + h + 0.12, w);
  panel(s, secA, 0.6, 5.5, 5.6, 1.45, size);
  panel(s, secB, 7.2, 5.5, 5.55, 1.45, size);
  return s;
}
// 드로어(세로) 1~2장 + 설명
function drawerFeature(id, title, files, caps, sections, size) {
  const s = featureSlide(id, title, SEC);
  const h = 5.05, w = h / DRAWER;
  files.forEach((f, i) => {
    const x = 0.6 + i * (w + 0.35);
    shot(s, f, x, 1.4, w, h, caps[i]);
  });
  files.forEach((f, i) => caption(s, caps[i], 0.6 + i * (w + 0.35), 1.4 + h + 0.12, w));
  const px = 0.6 + files.length * (w + 0.35) + 0.25;
  panel(s, sections, px, 1.4, 12.75 - px, 5.5, size || (files.length > 1 ? 16 : 18.5));
  return s;
}

deskFeature("F-01", "메인 화면 · 언어 전환", "00_hero_clean.jpg", [
  { h: "기능 설명", items: ["서비스 한 줄 소개와 실제 검사 과정 데모 (표기 없는 홍보 발견 → '의심' 도장)", "전국 어디든 장소 검색창", "상단 바에서 EN · 日本語 · 中文 · 한국어 전환, 데이터 상태(실데이터/샘플) 표시"] },
  { h: "처리 방식", items: ["첫 접속 시 /api/status로 TourAPI·네이버·AI 연결 상태 확인", "선택 언어는 브라우저에 저장해 다음 방문에도 유지", "검사 데모 애니메이션은 첫 진입 1회만, '움직임 줄이기' 설정 존중"] },
  { h: "디자인 근거", text: "한국관광공사(knto.or.kr) 구성 + 공정관광(GDWEB 수상작)의 파스텔 밴드·라인 일러스트" },
], "메인 화면 (한국어)");

deskPair("F-02·03", "지역 선택 · 장소 목록", "02_regions_grid.jpg", "03_place_cards.jpg",
  "지역 7개 패널 (성수동 선택 시 101곳)", "성수동 장소 카드 · 후기 검사 요약",
  [{ h: "F-02 지역 선택", items: ["성수·전주 데모 지역 + 부산·강릉·경주·제주, 전국 검색", "TourAPI locationBasedList2: 중심 좌표 + 반경 1.5km"] }],
  [{ h: "F-03 장소 목록 · 카테고리", items: ["관광지·문화시설·축제·전통시장·맛집 탭, 번역명 + 한글 이름", "카드마다 후기 검사 요약: 신뢰 n · 협찬 n · 의심 n"] }]);

deskPair("F-04·05", "필터 · 정렬 · 전국 검색", "22_sort_busan_food.jpg", "18_search_anywhere.jpg",
  "부산 맛집 · 가까운 순 정렬", "전국 검색: '안동 하회마을'",
  [{ h: "F-04 관심사 필터 · 정렬", items: ["관심사 9종 다중 선택 (자연·역사·카페·음식·시장·야간 등)", "신뢰도순(기본) · 가까운 순 · 이름순 정렬"] }],
  [{ h: "F-05 지방 커버리지 · 전국 검색", items: ["지방 축제·전통시장도 공식 데이터로 (전주 29곳)", "searchKeyword2로 전국 어디든 검색, 후기 분석도 그대로"] }]);

drawerFeature("F-06", "장소 상세 정보", ["07_detail_official.jpg", "08_detail_en.jpg"], ["전주 남부시장 (한국어)", "누메로뜨레쓰 (영어)"], [
  { h: "기능 설명", items: ["대표 사진, 주소, 이용시간, 쉬는 날, 요금, 축제 기간, 전화, 홈페이지, 소개", "번역 출처 표시: 관광공사 공식 번역 / Qwen 기계 번역"] },
  { h: "처리 방식", items: ["TourAPI detailCommon2(소개·홈페이지) + detailIntro2(운영시간 등)", "외국어 1순위: 관광공사 영·일·중 서비스, 괄호 속 한글명·좌표로 같은 장소 매칭", "공식 번역이 없으면 Qwen 번역 + 지명 용어집(전주→Jeonju 등)"] },
]);

{
  const s = featureSlide("F-07", "후기 신뢰도 분석", SEC);
  const h = 5.05, w = h / DRAWER;
  shot(s, "09_reviews_trusted_en.jpg", 0.6, 1.4, w, h, "후기 분석");
  caption(s, "누메로뜨레쓰 후기 6건 (영어)", 0.6, 1.4 + h + 0.12, w);
  panel(s, [
    { h: "기능 설명", items: ["장소를 열면 네이버 블로그 후기 6건을 수집해 7단계 검사", "후기마다 도장(신뢰·참고·협찬 고지·의심·차단), 점수, 판단 근거, 번역 요약", "분석이 끝나는 대로 한 건씩 화면에 표시 (실시간 스트리밍)"] },
    { h: "후기 선별", items: ["NAVER API HUB 최신순 + 관련도순 병합, 장소명이 들어간 글만", "제목에 장소명이 있는 글 우선, 본문에만 스친 글은 지역명도 있어야 인정"] },
  ], 4.65, 1.4, 8.1, 2.95, 16);
  const head = ["표시 신호", "판단 근거", "담당"].map((t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text1 } } }));
  const rows = [
    ["협찬 고지", "공정위 표기(협찬·제공받아·체험단) → 그대로 표시", "규칙"],
    ["숨은 광고", "표기 없는 할인·예약 유도, 단점 없는 과장", "Qwen2.5-7B"],
    ["AI 작성 확률", "문장이 언어모델에게 얼마나 예측 가능한지", "Fast-DetectGPT"],
    ["AI 문체 (보조)", "격식체 상투구, 개인 일화 부재", "Qwen2.5-7B"],
    ["AI 조작 문구", "'이전 지시 무시' 등 숨은 명령", "규칙 + Qwen"],
    ["개인정보 가림", "전화·이메일·계좌 등 마스킹 건수", "규칙"],
  ];
  s.addTable([head, ...rows], { x: 4.65, y: 4.35, w: 8.1, colW: [1.8, 4.45, 1.85], fontSize: 13, color: C.text1, rowH: 0.36, margin: 0.05, valign: "middle", border: { type: "solid", pt: 0.5, color: BORDER }, objectName: "signal table" });
}

drawerFeature("F-08", "분석 진행 표시", ["23_review_progress.jpg", "24_review_done.jpg"], ["분석 중: 0/6건 완료 · 0:13", "완료: 6건 · 1분 15초"], [
  { h: "기능 설명", items: ["후기 한 건을 AI 모델 두 개가 읽어 몇 초씩 걸리므로, 돌아가고 있음을 계속 보여줌", "스피너, 'n/6건 완료', 경과 시간을 1초마다 갱신", "아직 안 끝난 후기는 자리 표시로 남은 개수를 보여줌", "완료되면 소요 시간 표시"] },
  { h: "처리 방식", items: ["분석 결과를 한 건씩 스트리밍(NDJSON)으로 받아 끝나는 대로 표시", "GPU가 꺼져 있으면 하단 '켜는 중' 안내도 함께 표시 (F-14)"] },
], 17.5);

drawerFeature("F-09·10", "의심 후기 숨김 · 원문 확인", ["11_flagged_shown_en.jpg", "12_original_korean.jpg"], ["펼친 의심 후기와 판단 근거", "번역 요약 아래 한국어 원문"], [
  { h: "F-09 의심 후기 숨김 · 근거 공개", items: ["숨은 광고·AI 의심, 차단 글은 숨기고 건수 안내", "협찬을 밝힌 글은 '협찬 고지'로 표시", "'보기'로 펼치면 근거 공개, 지우지 않음"] },
  { h: "F-10 원문 확인", items: ["번역 요약 아래 한국어 원문, 블로그 원본 글 링크", "개인정보를 가린 원문만 textContent로 출력 (XSS 차단)"] },
], 18);

deskPair("F-11·12", "직접 후기 검사 · 인젝션 차단", "13_check_sponsored.jpg", "14_check_injection_blocked.jpg",
  "협찬 글 → '협찬 고지' (신뢰도 57)", "인젝션 → '차단' + 개인정보 1건 가림",
  [{ h: "F-11 직접 후기 검사", items: ["붙여 넣은 후기를 같은 7단계로 검사 (샘플 3종)", "협찬 글 '협찬 고지'(57) · 진짜 후기 '신뢰'(89)"] }],
  [{ h: "F-12 인젝션 차단 · 개인정보 가림", items: ["'이전 지시 무시' 같은 글은 AI에 보내지 않고 '차단'", "전화번호 등 개인정보는 분석 전에 가림"] }], 16.5);

deskPair("F-13", "다국어 지원", "16_lang_japanese.jpg", "17_lang_chinese_cards.jpg",
  "일본어 화면", "중국어 화면 (카드별 검사 요약)",
  [{ h: "기능 설명", items: ["화면 문구·후기 번역 요약·장소명을 영·일·중·한으로", "주소는 영문 표기 + 한국어 주소 병기 (택시·지도 앱용)"] }],
  [{ h: "번역 품질 관리", items: ["출력 언어 검증(한글·가나·한자 비율) 후 어긋나면 재요청", "7B 모델의 고유명사 음차 오류 → '기계 번역' 표시"] }], 16);

{
  const s = featureSlide("F-14", "GPU 온디맨드 · 콜드 스타트 안내", SEC);
  const w = 7.3, h = w * DESK;
  shot(s, "01_main_coldstart.jpg", 0.6, 1.5, w, h, "콜드 스타트 안내");
  caption(s, "GPU가 꺼져 있을 때 접속 → 하단에 기동 경과 시간 표시", 0.6, 1.5 + h + 0.15, w);
  panel(s, [
    { h: "기능 설명", items: ["사이트 접속·분석 시작 때만 Modal GPU를 깨우고, 앱 서버만 켜서는 기동하지 않음", "켜지는 동안 'AI 분석 서버(GPU)를 켜는 중 · m:ss' 표시, 준비되면 '준비 완료'", "기동 중 들어온 분석 요청은 실패하지 않고 준비될 때까지 대기"] },
    { h: "비용 정책", items: ["마지막 사용 5분 뒤 자동 종료 → 대기 중 요금 0원", "준비되면 상태 확인 중단 → 사용이 없으면 GPU가 제때 꺼짐"] },
  ], 8.25, 1.45, 4.5, 4.2, 15);
  const stats = [["2분 41초", "GPU 콜드 스타트"], ["3.6초", "켜진 뒤 응답 1건"], ["5분", "미사용 시 자동 종료"]];
  stats.forEach(([n, l], i) => {
    const x = 8.25 + i * 1.52;
    s.addText([{ text: n, options: { fontSize: 22, bold: true, color: C.accent1, breakLine: true } }, { text: l, options: { fontSize: 12, color: C.text2 } }],
      { x, y: 5.8, w: 1.48, h: 1.0, margin: 0, valign: "top", isTextBox: true });
  });
}

{
  const s = featureSlide("F-15", "모바일 반응형", SEC);
  const h = 5.0, w = h / MOBILE;
  ["19_mobile_main.jpg", "20_mobile_regions.jpg", "21_mobile_reviews.jpg"].forEach((f, i) => shot(s, f, 0.6 + i * (w + 0.4), 1.4, w, h, f));
  ["메인", "지역 선택", "후기 분석"].forEach((c, i) => caption(s, c, 0.6 + i * (w + 0.4), 1.4 + h + 0.12, w));
  const px = 0.6 + 3 * (w + 0.4) + 0.3;
  panel(s, [  // 모바일
    { h: "기능 설명", items: ["스마트폰(390px 폭)에서도 모든 기능 제공", "지역 패널은 세로로 쌓고, 카테고리 탭은 가로 스크롤", "장소 상세는 전체 화면 시트로 표시"] },
    { h: "접근성", items: ["키보드 초점 표시, 상세 시트 Esc로 닫기", "'움직임 줄이기' 설정 시 애니메이션 최소화", "도장 배지와 글자 라벨을 함께 표시해 색에만 의존하지 않음"] },
  ], px, 1.4, 12.75 - px, 5.5, 14.5);
}

// ═════════════════════════════════════════════════════════════
const SEC2 = "판정 로직 · 보안";
pres.addSection({ title: SEC2 });
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC2 });
  s.addText("신뢰도 판정 파이프라인", { placeholder: "title" });
  const steps = [
    ["수집", "TourAPI 장소 + 네이버 블로그 검색 요약"],
    ["개인정보 가리기", "전화, 이메일, 주민번호, 카드, 계좌, 메신저 ID"],
    ["숨은 명령 차단", "규칙 탐지 시 AI에 전달 X"],
    ["협찬 고지 확인", "공정위 표기 → 숨기지 않고 표시"],
    ["문맥 읽기", "Qwen2.5-7B 보안 분류 · 숨은 광고 판단 · 번역"],
    ["AI 작성 판별", "Fast-DetectGPT + Qwen 문체 평균"],
    ["판정 도장", "신뢰, 참고, 협찬 고지, 의심, 차단"],
  ];
  const w = 1.6, g = 0.15;
  steps.forEach(([t, d], i) => {
    const x = 0.6 + i * (w + g), y = 1.35;
    const last = i === steps.length - 1;
    s.addShape(S.roundRect, { x, y, w, h: 2.25, rectRadius: 0.1, fill: { color: last ? C.accent4 : C.background2 }, line: { color: last ? C.accent4 : C.background2 }, objectName: `step ${i + 1}` });
    s.addText(String(i + 1), { shape: S.ellipse, x: x + 0.15, y: y + 0.15, w: 0.42, h: 0.42, fill: { color: last ? C.accent1 : C.text1 }, line: { color: last ? C.accent1 : C.text1 }, color: C.background1, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText([{ text: t, options: { bold: true, fontSize: 14, color: C.text1, breakLine: true, paraSpaceAfter: 3 } }, { text: d, options: { fontSize: 13.5, color: C.text2 } }],
      { x: x + 0.13, y: y + 0.66, w: w - 0.24, h: 1.55, margin: 0, valign: "top", isTextBox: true });
  });
  // 배지 규칙 표
  const head = ["배지", "조건", "화면 표시"].map((t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text1 } } }));
  const rows = [
    [{ text: "신뢰", options: { bold: true, color: C.accent2 } }, "점수 ≥ 0.70", "기본 노출"],
    [{ text: "참고", options: { bold: true, color: C.accent3 } }, "0.40 ≤ 점수 < 0.70, 또는 AI 분석 실패", "기본 노출"],
    [{ text: "협찬 고지", options: { bold: true, color: "2D5F8F" } }, "협찬을 밝힌 글 (공정위 표기)", "기본 노출 · 협찬 표시"],
    [{ text: "숨은 광고·AI 의심", options: { bold: true, color: C.accent1 } }, "표기 없는 홍보, 또는 점수 < 0.40", "기본 숨김 · 펼치기"],
    [{ text: "차단", options: { bold: true, color: C.text1 } }, "프롬프트 인젝션 탐지", "분석 안 함 · 사유 표시"],
  ];
  s.addTable([head, ...rows], { x: 0.6, y: 3.85, w: 7.4, colW: [1.95, 3.45, 2.0], fontSize: 13.5, color: C.text1, rowH: 0.47, margin: 0.06, valign: "middle", border: { type: "solid", pt: 0.5, color: BORDER }, objectName: "badge rules" });
  panel(s, [
    { h: "신뢰도 점수 (1.0에서 감점)", items: ["협찬 고지(공정위 표기·협찬 명시): −0.30, 숨기지 않음", "표기 없는 홍보 등급: possible −0.15 · likely −0.35 (숨은 광고 → 의심)", "AI 작성 확률 p: −0.5 × p (판별기·문체 신호 평균)", "AI 조작 의심 문구: −0.20"] },
    { h: "7B 모델 안정화", text: "숫자 점수 대신 등급(none/possible/likely/explicit, low/medium/high)으로 받아 코드에서 점수화" },
  ], 8.3, 3.9, 4.45, 3.0, 13.5);
}
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC2 });
  s.addText("보안 설계", { placeholder: "title" });
  const cards = [
    ["개인정보 비식별화", ["분석 전에 정규식으로 전화·이메일·주민번호·카드·계좌·메신저ID 마스킹", "AI 모델·화면에는 가려진 텍스트만 전달", "가린 건수를 후기마다 표시"]],
    ["프롬프트 인젝션 3중 방어", ["① 규칙 탐지: 명백한 조작 문구는 AI에 전달하지 않고 차단", "② Qwen 보안 분류: 문맥상 조작 의도를 정상·의심·차단으로 분류", "③ 외부 글은 <review> 데이터로만 전달, 특수 토큰 제거, JSON 스키마 강제"]],
    ["키 · 접근 관리", ["API 키는 .env와 Vercel 환경변수(민감 값 암호화)에만 보관, 저장소 커밋 기록 검사", "Modal GPU·판별기는 API 키 인증 → 키 없이 호출하면 401", "블로그 원문은 textContent로만 출력 (XSS 차단)"]],
    ["수집 범위 최소화", ["네이버 공식 검색 API 요약만 사용, 본문 크롤링 안 함", "네이버 블로그 robots.txt의 AI·RAG 봇 금지 정책 준수", "사용자 계정·개인정보를 수집하지 않음"]],
  ];
  cards.forEach(([t, items], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.35 + Math.floor(i / 2) * 2.8, w = 5.95, h = 2.62;
    s.addShape(S.roundRect, { x, y, w, h, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: `security ${i + 1}` });
    seal(s, ["개인", "인젝", "키", "최소"][i], x + 0.25, y + 0.25);
    s.addText(t, { x: x + 1.6, y: y + 0.28, w: w - 1.85, h: 0.55, fontSize: 19, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
    s.addText(items.map((it, j) => ({ text: it, options: { bullet: { indent: 15 }, breakLine: j < items.length - 1, paraSpaceAfter: 6 } })),
      { x: x + 0.3, y: y + 1.0, w: w - 0.5, h: h - 1.1, fontSize: 15.5, lineSpacingMultiple: 0.95, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
}

// ═════════════════════════════════════════════════════════════
const SEC3 = "검증 · 운영";
pres.addSection({ title: SEC3 });
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC3 });
  s.addText("검증 결과와 한계", { placeholder: "title" });
  const stats = [
    ["0.92", "AUROC · 에세이 1000자", "KatFish 한국어 벤치마크(ACL 2025), 보정에 쓰지 않은 절반으로 평가"],
    ["0.66", "AUROC · 요약 길이 200자", "블로그 요약처럼 짧은 글에서는 판별력이 낮아짐"],
    ["58개", "단위 테스트 통과", "개인정보·인젝션·협찬 규칙, 점수·배지, 매칭, 주소 영문 변환, 콜드 스타트"],
    ["2.214", "원격 = 로컬 판별 점수", "Modal 판별기와 로컬 계산 결과 일치 확인"],
  ];
  stats.forEach(([n, l, d], i) => {
    const x = 0.6 + i * 3.08, y = 1.4, w = 2.85;
    s.addShape(S.roundRect, { x, y, w, h: 2.45, rectRadius: 0.1, fill: { color: i < 2 ? C.accent4 : C.background2 }, line: { color: i < 2 ? C.accent4 : C.background2 }, objectName: `stat ${i + 1}` });
    s.addText(n, { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: 0.9, fontSize: 40, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText([{ text: l, options: { bold: true, fontSize: 15, color: C.text1, breakLine: true, paraSpaceAfter: 4 } }, { text: d, options: { fontSize: 13, color: C.text2 } }],
      { x: x + 0.22, y: y + 1.1, w: w - 0.42, h: 1.3, margin: 0, valign: "top", isTextBox: true });
  });
  panel(s, [
    { h: "실제 데이터 시연 결과", items: ["누메로뜨레쓰(성수): 후기 6건 중 신뢰 3 · 참고 1 · 의심 2 (표기 없는 해시태그 홍보, 할인·예약 유도)", "직접 검사: 협찬 글 '협찬 고지'(57), 진짜 후기 '신뢰'(89), 인젝션 '차단' + 개인정보 1건 가림"] },
  ], 0.6, 4.1, 5.9, 2.85, 15.5);
  panel(s, [
    { h: "한계 (참고 지표로 제공)", items: ["짧은 글은 정확도 하락 → AI 판별은 참고 지표로만", "보정 데이터는 에세이·논문 → 블로그 후기와 분야 차이", "7B 모델의 고유명사 번역 오류 가능 → 한글 원래 이름 병기, 공식 번역 우선", "숨은 광고는 완벽히 잡지 못함 → 근거를 공개하고 숨기되 지우지 않음"] },
  ], 6.8, 4.1, 5.95, 2.85, 15);
}
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC3 });
  s.addText("기술 스택 · 운영 비용", { placeholder: "title" });
  const head = ["구성", "기술", "역할", "비용"].map((t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text1 } } }));
  const rows = [
    ["웹 서버", "Vercel · FastAPI (Python)", "화면·API, 보안 필터, 판정 로직 (서울 리전)", "Hobby 무료"],
    ["관광 데이터", "한국관광공사 TourAPI 4.0 (국·영·일·중)", "장소·축제·운영시간·공식 번역", "무료 (개발계정 일 1,000회)"],
    ["후기 수집", "NAVER API HUB 블로그 검색", "후기 원문 후보 (공식 API 요약)", "현재 임시 무료"],
    ["언어 모델", "Qwen2.5-7B-Instruct · vLLM · Modal L4 GPU", "보안 분류, 숨은 광고 판단, 번역·요약", "쓸 때만 약 $0.8/시간"],
    ["AI 작성 판별", "Fast-DetectGPT · Qwen2.5-1.5B · Modal CPU", "AI 작성 확률 (무료 오픈 모델)", "쓸 때만, 소액"],
    ["화면", "HTML · CSS · JavaScript (프레임워크 없음)", "4개 언어, 반응형, 실시간 스트리밍", "—"],
    ["소스 관리", "GitHub 비공개 저장소", "버전 관리, 키는 저장소에 없음", "무료"],
  ];
  s.addTable([head, ...rows], { x: 0.6, y: 1.35, w: 12.1, colW: [1.55, 4.15, 3.7, 2.7], fontSize: 14, color: C.text1, rowH: 0.58, margin: 0.07, valign: "middle", border: { type: "solid", pt: 0.5, color: BORDER }, objectName: "stack table" });
  s.addText("Modal은 월 $30 무료 크레딧을 제공하고, 두 서비스 모두 사용하지 않으면 5분 뒤 꺼지므로 시연 1시간에 $1~2 수준입니다. GPT 계열 유료 API를 쓰지 않아 데이터가 외부 AI 회사로 나가지 않습니다.",
    { x: 0.6, y: 6.15, w: 12.1, h: 0.75, fontSize: 14.5, color: C.text2, margin: 0, isTextBox: true });
}

// 마무리
pres.addSection({ title: "마무리" });
{
  const s = pres.addSlide({ masterName: "CLOSING", sectionTitle: "마무리" });
  s.addText("번역은 이미 다들 합니다.\n우리는 그 정보가 진짜인지 가려냅니다.", { placeholder: "title" });
  s.addText([
    { text: `서비스  ${URL}`, options: { breakLine: true, hyperlink: { url: URL }, color: C.background1 } },
    { text: "소스  제출 ZIP의 03_소스코드 (GitHub 비공개 저장소)", options: { breakLine: true } },
    { text: "팀  류황규 · 박건우 · 홍승우 · 황지룡", options: { breakLine: true } },
    { text: "2026 지역혁신 인재양성 연합 페스티벌 · AI·DX 산출물" },
  ], { placeholder: "body" });
  seal(s, "찐", 11.6, 0.6);
}

// PowerPoint는 기본으로 한글 단어를 중간에서 끊는다 → 모든 문단을 단어 단위 줄바꿈으로
async function keepKoreanWords(file) {
  const fs = require("fs");
  const JSZip = require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const parts = Object.keys(zip.files).filter((n) => /^ppt\/(slides|slideLayouts|slideMasters)\/[^/]+\.xml$/.test(n));
  for (const name of parts) {
    let xml = await zip.file(name).async("string");
    xml = xml.replace(/<a:pPr(?![^>]*eaLnBrk)/g, '<a:pPr eaLnBrk="0"');
    xml = xml.replace(/<a:p>(?!<a:pPr)/g, '<a:p><a:pPr eaLnBrk="0"/>');
    // 글자 언어를 한국어로 — en-US로 두면 PowerPoint가 한글을 글자 단위로 끊는다
    xml = xml.replace(/lang="en-US"/g, 'lang="ko-KR" altLang="en-US"');
    zip.file(name, xml);
  }
  // 테마의 한글(Hang)·동아시아(ea) 글꼴도 Noto Sans KR로 — 기본값(맑은 고딕)이 한국어 글자에 쓰이지 않도록
  const themeName = "ppt/theme/theme1.xml";
  let theme = await zip.file(themeName).async("string");
  theme = theme.replace(/<a:ea typeface="[^"]*"/g, '<a:ea typeface="Noto Sans KR"')
               .replace(/(<a:font script="Hang" typeface=")[^"]*"/g, '$1Noto Sans KR"');
  zip.file(themeName, theme);
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  await keepKoreanWords(OUT);
  console.log("wrote", OUT);
})();
