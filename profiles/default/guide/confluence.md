# Confluence 임베드 버전

사용자가 Confluence·임베드를 요청할 때만 만든다. 2026-09 에 여러 시각화 도구를 Confluence(제어할 수 없는 host)에 임베드하다 여러 번 실패하면서 얻은 규칙이다.

## 붙이는 곳

- Confluence 의 Forge 앱 매크로 **"Advanced HTML & Iframe Embed"** 에 붙인다. 매크로는 HTML 을 페이지 **안에** 저장하므로 따로 호스팅할 것이 없다.
- 붙여 넣는 것: `<page>.confluence.html` 원문 + 매크로 Height `1000`.
- 높이가 이상하면 페이지를 고치기 전에 **실제 host 부터 본다**. `getConfluencePage` (`contentFormat:"adf"`) 로 extension node 의 `parameters`(`htmlHeight` 등)를 확인한다. host 동작을 그럴듯한 가정으로 메우지 않는다.

## 변환 — `scripts/embed.py`

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/embed.py" page.html            # → page.confluence.html, page.csp-host.html
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/embed.py" page.html --out x.html
```

스크립트가 하는 일은 다음과 같다.

1. `<script src="https://…">` 를 내려받아(`~/.cache/ikken/` 캐시) **inline classic script** 로 바꾼다.
   `type="module"`, importmap, 동적 `import(` 이 있으면 실패한다. Confluence CSP 는 `blob:`·`data:` 모듈과 importmap 을 모두 막고, 빈 화면으로 조용히 실패한다.
2. 외부 stylesheet 를 처리한다. Google Fonts `<link>` 는 지운다(시스템 글꼴로 대체). 그 밖의 CSS(KaTeX 등)는 인라인 `<style>` 로 넣는다. CSS 안의 `url(…)` 폰트는 경고만 낸다.
3. `<script type="application/json" id="…">` 데이터 블록을 gzip+base64 로 압축한다(`data-encoding="gzip-base64"`). 골격의 `loadData()` 가 `DecompressionStream` 으로 푼다(인라인 스크립트라 CSP 를 통과한다).
4. embed 런타임을 주입한다(아래).
5. 크기를 보고한다. **2 MB 이상이면 실패**로 처리한다(2.9 MB 는 "Can't save changes" 로 저장되지 않았고, 2.0 MB 는 저장된 선례가 있다). 줄이는 순서: 좌표 반올림 → 샘플 축소 → 쓰지 않는 라이브러리 제거. three.js 자체(약 650 KB)는 압축할 수 없다(eval/blob 이 막혀 있다).
6. 점검용 `page.csp-host.html` 을 만든다. 엄격한 CSP meta 를 단 host 안의 `srcdoc` iframe(폭 760, 높이 미지정 = 150)으로 실제 매크로 상황을 재현한다.

### 데이터는 `loadData()` 로만 읽는다

- 페이지 코드는 데이터 블록을 **반드시 골격의 `loadData(id)`** 로 읽는다. `JSON.parse(el.textContent)` 로 직접 읽으면 변환본(gzip+base64)에서 예외가 나고 iframe 안이 빈 화면이 된다 (2026-10-14 신호등 상태 임베드 블록 — 일반 버전은 정상이고 Confluence 버전만 비어 있었다). 직접 쓴 코드도 마찬가지이며, 초기 렌더는 `loadData(...).then(...)` 뒤에 한다.

### 임베드 블록은 핵심 패널만

- 사용자가 "패널 몇 개만 임베딩" 을 요청하면, 원본 페이지에서 그 패널만 떼어 낸 **블록 페이지를 스크립트로 생성**한다(원본만 고치고 블록은 다시 생성 — 따로 편집하지 않는다). 블록에 필요 없는 무거운 데이터(사진 등)는 뺀다.
- 블록은 폭 **680 · 760 · 1000 · 1200 · 1400** 에서 높이 1000 안에 스크롤 없이 들어가야 한다. 좁은 세 칸보다 두 줄(그림 한 줄 + 조작·결과 한 줄)이 공간을 잘 쓰는 경우가 많다. 그림 높이는 `max-height` 로 묶는다.

### 그림은 잘리지 않게 — 모자라면 탭으로

- embed 에서 **그림 패널은 iframe 높이 안에 잘리거나 내부 스크롤 없이 다 보여야 한다**. 내부 스크롤은 설명 카드·긴 목록·기록 표에만 허용한다.
- 그림 패널이 둘 이상이면 embed 에서는 쌓지 말고 **탭으로 하나씩** 보여 주고, 고른 패널이 남은 높이 전부를 쓰게 한다. 일반 버전은 그대로 쌓는다.
- 폭이 좁아(900 미만, Confluence 고정 폭 본문 760) 그림과 설명 카드가 함께 들어가지 않으면 **설명 카드도 탭 하나로** 돌린다.
  - 조작부는 항상 맨 위에 보인다.
  - 조작부 아래에 현재 단계 제목 한 줄을 둔다.
- 이유: HD맵 속성 확장 임베드에서 760 폭일 때 그림 두 패널과 카드가 한 열에 쌓여 각 그림이 약 215 px 만 보였다 (2026-10-21 "도식 영역이 부족해서 제대로 보여지지 않고 있어").
- 점검: `check.py <page>.csp-host.html` 이 폭마다 보이는 `.stage` 의 `scrollHeight ≤ clientHeight` 를 본다(`verify.md`). 탭이 있으면 탭마다, 단계마다 확인한다.

## embed 런타임 (주입되는 동작)

- **자동 embed 모드**: iframe 안이면 `<html class="embed">` 가 붙는다. `?embed=0|1` 로 강제할 수 있고, `?theme=light|dark` 를 지원한다.
- **높이**: host 가 높이를 주지 않았다는 것이 **확실할 때만** 높이를 차지한다. 조건은 same-origin `frameElement` 가 있고 높이가 160 이하(CSS 기본값 150 이 그 신호)일 때다. 이때 `frameElement.style.height = 1000px` (400–1200 범위) 로 둔다.
  host 가 일부러 준 높이는 존중한다. 끝내 낮으면 위쪽에 "Height 1000 으로 설정하세요" 안내 줄을 띄운다.
- **스크롤하지 않는다**: embed 모드에서 페이지 전체는 주어진 높이에 맞추고, 길어지는 영역(side 카드, aside)만 내부 스크롤한다. `min-height` 바닥값을 두지 않는다. 바닥값이 있으면 짧은 host 에서 스크롤이 생긴다.
- **패널**: 기본으로 열려 있다. 열리면 오른쪽 세로 전부를 차지하고 그림은 남은 폭으로 줄어든다. 그림 위에 띄워 가리지 않는다. 닫으면 그림이 폭 전부를 쓴다.
  - 높이가 모자라면(430 미만) 기본으로 접고, 크기가 바뀌면 다시 판단한다. 사용자가 직접 여닫은 뒤에는 건드리지 않는다.
  - 폭이 900 미만이면 접어서 감추지 않는다(런타임이 `nopanel` 을 붙여도 템플릿 CSS 가 되살린다). 대신 `[조작부 / 그림 / 카드]` 로 쌓고 행 높이를 비율로 고정하거나, 위 「그림은 잘리지 않게」대로 탭으로 돌린다.
  - 조작부는 패널을 닫아도 남는다.
- **전체화면** 버튼은 `document.fullscreenEnabled` 일 때만 보인다. 테마 버튼과 **한 상자**로 붙인다 — 따로 떨어진 버튼 두 개로 두지 않는다.
  - 런타임이 테마 버튼 자리에 묶음(`#ikbar`)을 두고 `[테마 | 전체화면]` 순서로 넣는다. 가운데 모서리는 각지게, 맞닿는 테두리는 한 줄(구분선)만 남긴다.
  - 모양은 테마 버튼 것을 그대로 쓴다(같은 class, `#theme` CSS 규칙을 `#ikfs` 로 복사). 머리말 오른쪽 여백은 버튼 한 칸만큼 늘린다.
  - 테마 버튼이 없는 페이지에서만 HUD 끝에 둔다.
  - 이유: "theme과 full screen 버튼을 독립 버튼으로 두지 말고 하나의 박스 안에 붙여서 배치해줘" (2026-10-21) — 전에는 테마 버튼 오른쪽에 6px 띄운 별도 버튼이었다.

템플릿은 `html.embed` 클래스에 반응하는 CSS 를 이미 갖고 있다. 새 레이아웃을 만들면 그 규칙을 함께 맞춘다.

## 블로그·페이지에 자동으로 넣기 (API)

- 매크로("HTML & Iframe Embed", extension key `…/static/html-macro`)는 storage 에 `<ac:adf-extension>` 으로 저장된다. **새로 만들지 말고 같은 스페이스의 기존 글에서 이 블록을 복제**해 바꾼다:
  `guest-params` 의 `body` = JSON `{"htmlCode": <변환본 원문>, "htmlHeight": "1000"}`(HTML escape), `search-text`, `local-id`(새 uuid, node·fallback 둘 다), `extension-data.content` 의 글 id · version, `measured-height` 는 지운다.
- 순서: 본문만으로 글 생성 → id 를 받아 매크로를 넣어 version 2 로 갱신 → 첨부(이미지)는 글 id 로 올린다.
- 올린 뒤 `body-format=atlas_doc_format` 으로 다시 읽어 extension 의 `htmlCode` 가 변환본과 **완전히 같은지**, `htmlHeight` 가 1000 인지 확인한다. 로그인 화면 확인은 사용자에게 부탁한다.

## 점검

- `page.csp-host.html` 을 chrome-devtools 로 열고(`file://`), iframe 안이 빈 화면이 아닌지, 콘솔에 CSP 위반이 없는지 확인한다.
  스크린샷을 760 폭과 좁은 폭(600)에서 찍는다.
- embed 를 건드린 변경은 일반 버전과 embed 버전을 **둘 다** 점검한다.
- 보이는 것을 확인한다. 클래스나 플래그를 보지 말고 `getBoundingClientRect()` 로 화면 안에 있는지, 크기가 맞는지 확인한다.
- 일반 버전과 Confluence 버전을 따로 관리하지 않는다. 원본(`page.html`)만 고치고 변환을 다시 돌린다. 옛 `.confluence.html` 이 남아 있으면 지운다(오래된 산출물이 붙여 넣어지는 사고가 있었다).
