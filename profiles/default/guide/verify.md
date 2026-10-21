# 만든 뒤 점검

보고하기 전에 확인한다. 못 한 항목은 보고에 그렇다고 적는다. 웹 서버는 띄우지 않고 `file://` 로 연다.

## 브라우저 점검

두 방법 중 하나를 쓴다. 둘 다 안 되면 보고에 "브라우저 점검 못 함"이라고 적는다.

- **`scripts/check.py`** (playwright 가 있는 python): 아래 2–7번을 한 번에 하고 JSON 과 스크린샷 경로를 낸다. 스크린샷은 `Read` 로 직접 본다.
  ```bash
  python "${CLAUDE_PLUGIN_ROOT}/scripts/check.py" page.html --steps --out <scratchpad>/check
  ```
  playwright 가 있는 인터프리터는 `python -c "import playwright"` 로 찾는다(conda env 포함).
- **chrome-devtools MCP**: Chrome 이 있으면 쓴다. 순서는 다음과 같다.


1. `new_page` → `file:///절대/경로.html` 로 연다.
2. `list_console_messages` 를 확인한다. error 가 0 이어야 한다. three.js classic deprecation 경고 한 줄은 정상이다.
3. 라이트·다크에서 각각 `take_screenshot`(`emulate` 로 `prefers-color-scheme`, 또는 theme 버튼 클릭)을 찍는다. 두 테마 모두에서 글자와 선이 보여야 한다.
4. 단계형이면 처음부터 끝까지 **실제 클릭**(`click`)으로 넘긴다. 매 단계 이전/다음·단계 번호 버튼의 `getBoundingClientRect()` 가 같은지 `evaluate_script` 로 확인한다. 위치가 변하면 실패다.
   - 기본 폭과 **한 열로 접히는 폭(760)** 둘 다 본다.
   - Confluence 버전이 있으면 `csp-host` 의 iframe 폭 680 · 760 · 1000 · 1400 에서도 본다.
   - 같은 폭들에서 그림(`.stage`)이 잘리지 않는지(`scrollHeight ≤ clientHeight`)도 본다.
   - `check.py` 는 이 모두를 한다 (`steps` · `steps_760` · `embed`). 넓은 폭에서만 통과하고 접힌 폭에서 버튼이 밀린 사고가 있었다 (2026-10-21).
5. 키보드 단축키를 `press_key` 로 확인한다.
6. 폭 390px(`resize_page` 또는 `emulate` viewport)에서 `document.documentElement.scrollWidth <= innerWidth` 인지, 레이아웃이 한 열로 접히는지 본다.
7. 주요 버튼이 덮여 있지 않은지 `document.elementFromPoint(버튼 중심)` 이 그 버튼인지 확인한다.
8. 확인이 끝나면 `close_page` 로 닫는다.

## 내용 점검

- 화면의 숫자를 데이터 스크립트 출력과 대조한다(무작위 2–3개).
- 단계별 범례 개수의 합이 전체와 맞는지 확인한다.
- `TODO(ikken)` 이 남아 있지 않은지 확인한다: `grep -n "TODO(ikken)" <file>` 결과가 없어야 한다.
- 이전 버전 비교 문구, 정답 미확정 판정 문구가 없는지 확인한다(`explanation.md`).
- 라이브러리가 표의 classic 빌드인지, `type="module"`·importmap 이 없는지 확인한다.
- 데이터 블록을 `loadData()` 로만 읽는지 확인한다: `grep -n 'JSON.parse(document.getElementById' <file>` 결과가 없어야 한다 (`confluence.md`).
- 새로 만든 class·id 가 골격의 것과 겹치지 않는지 확인한다. 특히 `.wrap`·`.card`·`.stage`·`.side` 같은 골격 클래스와, 같은 id 를 두 요소에 쓰는 경우(예: select 와 table 이 둘 다 `#route`) — `document.querySelectorAll('[id]')` 로 중복 id 를 센다 (2026-10-14 `.seg.wrap` 이 페이지 `.wrap` 의 여백을 받아 버튼이 밀렸고, `#route` 중복으로 선택 상자가 비었다).

## 크기

- 일반 버전은 제한이 없지만 5 MB 를 넘으면 샘플을 줄인다.
- Confluence 버전은 2 MB 미만이어야 한다(`confluence.md`).
