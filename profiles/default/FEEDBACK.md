# 피드백 이력

`/ikken:feedback` 이 반영한 피드백이다. 최신이 위에 온다. 규칙 본문은 `guide/*.md` 에 있고, 여기에는 경위만 남긴다.

| 날짜 | 피드백 | 반영 | 대상 |
|---|---|---|---|
| 2026-10-30 | codex-bridge 사용 안내 스타일이 가이드로 마음에 듦 — 이런 템플릿도 있으면 | `templates/guide.html`(신규), `patterns.md` 표 · guide, `style.md` 레이아웃 · 예외(hero · radius · 그림자) · 코드 블록, `interaction.md` 공통(복사 버튼 · 목차 표시), `scripts/profile.py` TEMPLATES, `SKILL.md` 5, `README.md`, `skills/config` · `skills/feedback` 골격 수 | codex-bridge-guide.html |
| 2026-10-28 | 확대 화면(lightbox)에서 마우스 휠로 확대 · 축소, 끌어 이동 | guide/interaction.md · style.md · verify.md | tl_box_undist_check.html |
| 2026-10-28 | html 에 이미지를 붙이면 누르면 화면에서 크게 보이게(lightbox) — 오버레이 포함 | `interaction.md` 공통, `style.md` lightbox, `verify.md` 7 | box_undist 정렬 점검 |
| 2026-10-26 | 사례마다 똑같이 적용되는 옵션(지금 규칙 vs Viterbi, 대상 가까이 vs 구간 전체)은 패널마다 따로가 아니라 공유 | `interaction.md` 공통 · 시간축, `templates/compare.html`(`VIEW` · `setView`) | ego_lane Viterbi 사례 블록 · 방향 구간 Viterbi 보고서 |
| 2026-10-26 | Confluence 임베드 블록에 지터링 — 문서 높이를 내용이, 그림 크기를 vh 가 정해 host 높이와 물려 돌았다 | `confluence.md` 스크롤 · 높이 고정, `templates/compare.html`(embed CSS), `scripts/check.py`(`autoheight`) | ego_lane Viterbi 사례 블록 |
| 2026-10-26 | 원본 뷰어 링크는 내부망 · 외부망 둘 다 (compare 골격으로 실제 보고서를 만들며) | `templates/compare.html`(`links` 여럿 · 사례 `note` 한 줄) | 방향 구간 Viterbi 보고서 |
| 2026-10-26 | compare 골격 만들어 둬 | `templates/compare.html`(예시 데이터 · 방식 선택 · BEV · 막대 · player), `patterns.md` 표 · compare, `scripts/profile.py` TEMPLATES, `SKILL.md` 5, `README.md` | — |
| 2026-10-26 | 사례 비교 보고서 스타일이 마음에 듦 + 막대만으로는 상황이 안 보이니 지도 · ego 상자 BEV 를 붙이고, 고른 매칭 로직의 결과를 도로 위에서 보게 · 장면 심층 페이지(조작 / 도식 / 표 / 막대 패널)도 마음에 듦 | `patterns.md` compare 유형, `interaction.md` 시간축(막대 · 방식 선택 · 여러 player) · 지도(가까이/전체), `style.md` 개체 범주 색 · 지도 도식(BEV) · segmented · 결과 표 | ego 차로 매칭 비교(Viterbi smoke) · 박스 매칭 successor 거리 |
| 2026-10-22 | 시간·거리를 따라 쌓인 데이터(프레임별 라벨)는 단계형 대신 시간축(거리축) 바로 넘기며 각 시점이 왜 그 값인지 설명 | `patterns.md` 머리 (이해의 축) | command.driver 프레임별 라벨 |
| 2026-10-21 | 임베드의 테마 · 전체화면 버튼을 따로 두지 말고 한 상자로 붙여서 | `confluence.md` embed 런타임, `scripts/embed.py`(`#ikbar`) | TL 정책 안건 블록 |
| 2026-10-21 | 패널에는 항상 타이틀 (신호등 상태 조합 페이지가 잘 만든 예) — 단계 설명·선택한 점 카드와 3D 장면에도 `.ptitle` | `style.md` 레이아웃(패널 제목 규칙 다듬기), `templates/walkthrough.html`(카드 `.ptitle`), `templates/view3d.html`(3D 장면 `.ptitle`) | 신호등 상태 조합 페이지 |
| 2026-10-21 | 임베드 전체화면 버튼은 테마 버튼 바로 오른쪽에 | `confluence.md` embed 런타임, `scripts/embed.py`(`#ikfs`) | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | 회전 중심 표시를 점 대신 xyz 축 선분으로 | `interaction.md` 3D, `templates/view3d.html`(`placeFocus` · `--ax-*` 토큰) | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | 3D 회전 중심(focus point)을 작은 점으로 표시 | `interaction.md` 3D, `templates/view3d.html`(`placeFocus`) | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | 3D 좌클릭 가로 드래그 회전 방향 반대 → 장면이 마우스를 따라 돌게 (우클릭 pan 은 그대로 — 앞 커밋은 오해라 되돌림) | `interaction.md` 3D, `templates/view3d.html` | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | 레이어 관계 노드 그래프 대신 실제 HD맵 3D 에서 객체를 눌러 가며 구성을 보게 | `patterns.md` catalog(공간 객체는 실제 장면 · id 관계선 · 레이어 띄우기 · 종류 목록) | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | 맵 속성 확장 설명은 단계가 아니라 카테고리(레이어)별로 — 템플릿에 끼워 맞추지 말고 주제의 이해 축에 맞춰 화면을 새로 구성 | `SKILL.md` 3(이해의 축 · 유형) · 5(골격 없으면 새로), `patterns.md` 머리말 · catalog 유형 | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | 이전/다음이 접힌 레이아웃·embed 에서 그림 높이에 밀려 연속 클릭이 끊김 → 조작부를 그림·카드와 분리해 어느 폭에서도 고정 | `interaction.md` 단계형, `patterns.md` walkthrough, `verify.md` 4, `scripts/check.py`(760 폭 · embed 폭 점검), `templates/walkthrough.html`(`.ctrl` 영역 · sticky) | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | 단계 번호 버튼이 5개를 넘으면 5개씩 페이지로 넘김 | `interaction.md` 단계형, `templates/walkthrough.html`(`drawSteps`) | HD맵 레이어 속성 확장 페이지 |
| 2026-10-21 | embed 에서 그림이 잘림 → 그림 패널 여럿은 탭, 좁으면 설명 카드도 탭, 그림 잘림 점검 | `confluence.md`(그림은 잘리지 않게 · 패널), `scripts/check.py`, `templates/walkthrough.html`(좁은 embed 쌓기 · embed 에서 `.sum` 숨김) | HD맵 레이어 속성 확장 페이지 |
| 2026-10-14 | 머리말은 문단 lede 대신 3줄 요약, 한글 단어 단위 줄바꿈 | `explanation.md` 구성 순서, `style.md` 글꼴, 템플릿 4종 body·walkthrough 머리말 | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | 상태 선택 버튼은 큰 아이콘 + 작은 글씨, 선택은 테두리 | `style.md` 컴포넌트 | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | 핵심 값 전용 결과 패널, [그림 | 조작 | 결과] 배치 | `patterns.md` combinator | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | 행 전체 패널은 여러 칸으로, 패널 안 긴 설명·중복 배지 금지 | `style.md` 레이아웃 | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | 조건이 엮이는 주제는 고정 사례 대신 조합 | `interaction.md` 조합, `patterns.md` combinator | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | 데이터 블록은 loadData() 로만 (임베드 빈 화면 재발 방지) | `confluence.md`, `verify.md` | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | 임베드는 핵심 패널만 담은 블록을 원본에서 생성, 680–1400 폭 높이 1000 | `confluence.md` | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | HTML & Iframe Embed 매크로 API 게시 절차와 ADF 확인 | `confluence.md` | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | class·id 충돌 점검 | `verify.md` | 신호등 상태 조합 페이지 · 임베드 블록 |
| 2026-10-14 | 패널에는 항상 지칭할 수 있는 제목(title)을 단다 | `guide/style.md` 「레이아웃」, `templates/walkthrough.html` (stage `.ptitle`) | 신호등 상태 조합 페이지 |
| 2026-10-14 | 외부 라이브러리는 CDN 허용, 요청 시 Confluence 임베드 버전 | `guide/confluence.md`, `guide/style.md` 「라이브러리」, `scripts/embed.py` | — |

## 초기 규칙의 출처 (2026-10-14)

플러그인을 만들기 전에 받은 피드백(Claude Code 메모리)을 처음 규칙으로 옮겼다.

| 날짜 | 원래 피드백 | 반영 |
|---|---|---|
| 2026-09-30 | "이전 단계 다음 단계는 위치가 변하면 안돼. 마우스로 연속 클릭을 못하잖아" | `interaction.md` 단계형 |
| 2026-10-01 | "이전이랑 비교하는 톤으로 만들지 말고 현재 로직만 설명하도록 해줘" | `explanation.md` 현재 로직만 |
| 2026-10-01 | 블로그·설명은 보고서 형식 — 대화 질문이 아니라 대상 자체를 설명 | `explanation.md` 구성 순서 |
| 2026-10-02 | "step 에서 판정되는게 아니면 토글을 넣지 마", "legend 에서 색 범례는 그냥 없애" | `interaction.md` 판정 범례 |
| 2026-10-02, 10-06 | 3D 조작: WASD xy · Q 아래/E 위 · 회전 방향 · 우클릭 pan · Shift 4배 | `interaction.md` 3D, `templates/view3d.html` |
| 2026-10-06 | Confluence 임베드: 패널 기본 열림·오른쪽 고정, 150px → 1000, 인라인 스크립트, 2 MB 미만 | `confluence.md`, `scripts/embed.py` |
| 2026-10-12 | 영어는 미국식 철자 | `explanation.md` 언어 |
| 2026-10-13 | 정답 미확정이면 정확도·맞다/틀리다 금지, 다른 사례만 나란히 | `explanation.md` |
