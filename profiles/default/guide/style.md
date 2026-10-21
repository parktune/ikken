# 디자인 스타일

먼저 만든 HTML(교차로 블록 묶기, 경로 JSON 탐색기, 저장소 개관, 3D 맵 crop, 고도 보기)에서 추출했다.
분위기는 **조용한 엔지니어링 노트**다. 종이에 가까운 옅은 배경, 얇은 선, 색은 의미가 있는 곳에만 쓴다.

## 색 — 토큰으로만

- 모든 색은 `:root` CSS 변수로 정의한다. 요소에 hex 를 직접 쓰지 않는다(SVG 는 `var(--x)` 나 JS 에서 `getComputedStyle` 로 읽기).
- 다크 모드는 반드시 세 군데에 정의한다.

```css
:root{ /* light */ }
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]){ /* dark */ color-scheme:dark } }
:root[data-theme="dark"]{ /* dark, 같은 값 */ color-scheme:dark }
```

- 기본 중립 토큰 (slate 계열, junction 페이지 기준):

| 토큰 | light | dark | 용도 |
|---|---|---|---|
| `--bg` | `#E6ECEF` | `#0E151B` | 페이지 배경 (약간 푸른 회색) |
| `--panel` | `#F7F9FA` | `#151F28` | 카드·패널 |
| `--ink` | `#15212B` | `#DCE5EB` | 본문 |
| `--muted` | `#56676F` | `#8B9AA5` | 보조 글, 축 |
| `--line` | `#C3CFD6` | `#293744` | 테두리·구분선 |
| `--grid` | `#E3EAEE` | `#1A2530` | 격자 |
| `--code` | `#EEF2F4` | `#101921` | inline code 배경 |
| `--hit` | `#D23D26` | `#FF6B50` | 선택·강조 (빨강 계열) |

- **의미 색**은 이름을 뜻으로 짓는다(`--share`, `--route`, `--ego`, `--jlane`). `--blue` 처럼 색 이름으로 짓지 않는다.
  한 페이지에 6–8개 이하로 쓴다. 채움은 같은 색의 투명 버전(`--share-f: rgba(…,.22)`)을 쓴다.
- 참고 의미 색 (light / dark): teal `#17808A`/`#4CC0C8`, blue `#3D6FB6`/`#7FA8E8`, magenta `#A52F68`/`#E36AA6`,
  amber `#B57611`/`#E2A843`, violet `#7b4ff0`/`#a88bff`, green `#0a7d55`/`#37c98f`, orange `#e2760f`/`#ff9a3d`.
- 배경 요소(일반 차로, 비활성 노드)는 `--lane` 처럼 낮은 대비의 회색으로 그리고, 주제만 색으로 칠한다.
- 차트 색 설계가 복잡하면 `dataviz` skill 의 방법을 참고한다(단, 토큰 이름과 이 표가 우선).

## 글꼴

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
```

```css
--font:"IBM Plex Sans KR",system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
--mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,Consolas,"IBM Plex Sans KR",monospace;
```

- 설명형 페이지(walkthrough, overview)의 본문은 `16px/1.65` 다. 탐색기·3D 처럼 밀도가 높은 페이지는 `14px/1.45` 다.
- h1 은 `clamp(1.55rem,3.1vw,2.25rem)`, 700, `letter-spacing:-.01em`, `text-wrap:balance` 다. 탐색기 h1 은 17px 다.
- 본문 폭은 `max-width:70–72ch` 다.
- mono 는 id, 숫자 라벨, eyebrow, 단계 번호, 경로, scalebar 에 쓴다.
- 한글은 단어 중간에서 끊지 않는다: `body{word-break:keep-all; overflow-wrap:break-word}`, 긴 `code` 는 `overflow-wrap:anywhere` (2026-10-14 "첫 문단처럼 중간에 단어가 짤리지 않도록").

## 컴포넌트

| 이름 | 모양 |
|---|---|
| card | `background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:16px 18px` (탐색기는 radius 10, padding 12/14) |
| eyebrow `.k` | mono `.72rem`, `letter-spacing:.08em`, uppercase, `--muted` |
| stats | 3열 grid, 각 칸 `border-top:2px solid var(--line)`, 값 `1.25rem` 700 tabular-nums, 라벨 `.74rem` muted |
| 버튼 | `border:1px solid var(--line)`, radius 4–6, `font:inherit`, 현재/활성은 `background:var(--ink); color:var(--panel)` 반전, disabled 는 `opacity:.35` |
| 이전/다음 | `border:1px solid var(--ink)`, 투명 배경, 2열 grid, `← 이전 단계` / `다음 단계 →` |
| inline code | `--code` 배경, `padding:1px 5px`, radius 3 |
| tooltip | 패널 색, 1px 선, radius 4, `.78rem`. **그림자는 여기에만** `0 2px 10px rgba(0,0,0,.12)` |
| legend | flex wrap, `.8rem` muted, 항목 사이 `gap:6px 16px` |
| callout | `.note`(accent-soft 배경 + 왼쪽 3px accent 선) / `.warn`(warn 계열) — overview 에서만 |
| tag | 작은 pill, 의미 색 글자 + 그 색의 투명 배경 |
| scalebar | 지도 오른쪽 아래, mono `.72rem`, muted 2px 선 |
| theme 버튼 | 오른쪽 위 34×30 아이콘 버튼, 반원 아이콘 |
| 상태 선택 버튼 | 시각적 상태(신호등 점등, 차로 화살표 등)를 고르는 버튼은 **그 상태를 그린 큰 아이콘**이 주인공이고 글씨는 아래에 작게 둔다. 선택 표시는 배경 반전이 아니라 굵은 테두리로 해서 아이콘 색을 지킨다 (2026-10-14 "글씨보다 아이콘을 크게해서 선택할 수 있게") |

## 레이아웃

- walkthrough 는 최대 1240px 이고, `grid-template-columns:minmax(0,1fr) 380px` (그림 | 사이드) 다.
- overview(문서형) 는 최대 980px 단일 열이다.
- explorer 는 최대 1500px 이고 sticky header + `1.55fr / 1fr` 카드 grid 다.
- 3D 는 전체 viewport 이고 `minmax(0,1fr) 380px` 다. 오른쪽 aside 는 세로 전체를 쓰고 내부 스크롤한다.
- 940px 이하에서는 한 열로 접는다. 폰 폭에서도 가로 스크롤이 없어야 하며 좌우 여백은 16px 이상이다.
- 요소 사이 간격: 페이지 섹션 22–28px, 카드 안 14px, 컨트롤 6–8px.
- 행 하나를 혼자 쓰는 패널은 안을 여러 칸(예: 글 | 사진)으로 나눠 넓은 폭을 쓴다. 좁은 화면에서만 위아래로 쌓는다 (2026-10-14 "행을 혼자 쓰게 된 만큼, 설명 패널은 넓은 공간을 활용").
- 패널 안에 긴 보조 설명 문단을 두지 않는다(필요하면 제목 옆 한 줄). 다른 패널이 이미 보여 주는 값을 배지·태그로 다시 그리지 않는다 (2026-10-14 "navi 패널 아래 긴 설명은 필요 없어", "도식에서는 match 태그 없애").
- **모든 패널(그림 stage · 카드 · aside 절 · HUD)에는 짧은 제목을 단다.** 사용자가 "도식 패널", "STATUS 비교 패널"처럼 이름으로 지칭할 수 있어야 한다. 제목은 패널 맨 위 한 줄(`.ptitle` 또는 카드 `h2`), 2–4 단어, 화면에 보이게 둔다 (2026-10-14 "패널에는 항상 내가 지칭할 수 있도록 title을 만드는 것").

## 하지 않는 것

- 그라디언트, 글래스모피즘, 큰 그림자, radius 10px 초과, hero 배너, 일러스트, 이모지 아이콘은 쓰지 않는다.
- 색으로만 구분하지 않는다. 선 모양(점선), 굵기, 라벨을 함께 쓴다.
- 아이콘은 inline SVG(`fill:currentColor`) 로 그린다. 아이콘 폰트는 쓰지 않는다.

## 라이브러리

CDN 은 **버전 고정 + classic(UMD) 빌드만** 쓴다. `type="module"`, importmap, 동적 `import()` 는 쓰지 않는다.
이렇게 해야 `scripts/embed.py` 가 그대로 인라인해서 Confluence 버전을 만들 수 있다.
필요 없으면 라이브러리 없이 SVG·Canvas 로 직접 그린다.

| 용도 | script |
|---|---|
| 차트·스케일·지도 투영 | `https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js` |
| 3D | `https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js` (classic 빌드가 있는 마지막 계열. 콘솔 deprecation 경고 1줄은 정상) |
| 수식 | `https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js` + `…/katex.min.css` |
| 그래프 레이아웃 | `https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js` |

표에 없는 라이브러리가 필요하면 classic 빌드가 있는지 먼저 확인하고, 쓴 뒤 이 표에 추가한다(`/ikken:feedback`).
