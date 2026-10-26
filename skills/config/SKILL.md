---
name: config
description: ikken 프로필 관리 — 활성 프로필 보기·바꾸기, 새 프로필 만들기(취향 질문 또는 복제), 취향 다시 묻기, 지우기. "/ikken:config", "/ikken:config use <이름>", "/ikken:config new <이름> [--from <원본>]", "ikken 프로필 바꿔줘", "ikken 스타일 프로필 새로 만들어" 같은 요청에 쓴다. /ikken 을 처음 실행할 때(설정 없음)도 이 절차의 「처음 설정」을 따른다.
argument-hint: "[use <이름> | new <이름> [--from <원본>] | edit | delete <이름>]"
---

# ikken:config

ikken 의 규칙·골격은 **프로필** 단위로 쌓인다.

- `default` — 저장소의 `profiles/default/` (배포자가 다듬어 배포하는 기본 스타일). 규칙 6개(`guide/*.md`) · 골격 5개(`templates/*.html`) · 이력(`FEEDBACK.md`) 전부가 여기 있다.
- 사용자 프로필 — `~/.claude/ikken/profiles/<이름>/`. **기본과 다른 부분만** 둔다.
  - `profile.md` — 기본 위에 덮어쓰는 규칙. 절 이름은 guide 파일 이름(`explanation` · `interaction` · `style` · `patterns` · `verify` · `confluence`) + `진행 (SKILL)`.
  - `tokens.css` (선택) — 색·글꼴 토큰 덮어쓰기. 골격을 복사할 때 기본 토큰 뒤에 `<style id="ikken-profile-tokens">` 로 붙는다.
  - `templates/<유형>.html` (선택) — 그 유형의 골격을 통째로 바꾼다.
  - `FEEDBACK.md` — 이 프로필의 피드백 이력.
- 활성 프로필은 `~/.claude/ikken/config.json` 의 `active` 하나다. 한 사람이 여러 프로필을 두고 바꿔 쓸 수 있다.

모든 파일 조작은 스크립트로 한다(손으로 config.json 을 쓰지 않는다).

```bash
P="${CLAUDE_PLUGIN_ROOT}/scripts/profile.py"     # 플러그인 루트 = 이 파일의 두 단계 위
python3 "$P" status            # 활성 · 읽을 규칙 · 골격 · 피드백 대상
python3 "$P" list
python3 "$P" use <이름>
python3 "$P" new <이름> [--from <원본>] [--use]
python3 "$P" delete <이름>
```

## 인자별 동작

| 인자 | 동작 |
|---|---|
| (없음) | `status` · `list` 를 보여 주고, 피드백이 어디에 쌓이는지 한 줄로 말한다 |
| `use <이름>` | `use`. 없는 이름이면 목록을 보여 주고 `new` 할지 묻는다 |
| `new <이름>` | `new <이름> --use` 뒤 「취향 질문」으로 차이를 채운다 |
| `new <이름> --from <원본>` | 원본(`default` 또는 다른 로컬 프로필)을 복제한다. `default` 에서 복제하면 차이 없음에서 시작한다. 취향 질문은 묻지 않는다 |
| `edit` | 활성 프로필(default 가 아닐 때)에 「취향 질문」을 다시 하고, 답이 바뀐 항목만 고친다 |
| `delete <이름>` | 지우기 전에 `AskUserQuestion` 으로 확인한다. 활성 프로필은 지울 수 없다 |

## 처음 설정 — config.json 이 없을 때

`/ikken` 이나 `/ikken:config` 를 처음 실행하면(`status` 의 `configured` 가 false) 먼저 이것을 한다. 질문은 두 번 이하다.

1. `AskUserQuestion` — "어떤 스타일로 쓸까요?"
   - `기본(default) 그대로` — `use default`. 피드백은 저장소 기본에 쌓인다(원본 저장소를 쓰는 배포자에게 맞다. 설치본이면 피드백을 저장할 곳이 없으니 「내 프로필」을 권한다).
   - `내 프로필 만들기 (Recommended)` — 이름은 Other 로 받는다(소문자 · 숫자 · `-` · `_`). 비우면 `me`. `new <이름> --use` 후 2 로.
2. `AskUserQuestion` 한 번에 「취향 질문」 네 개를 묻는다. 모든 질문의 첫 선택지는 `기본 그대로` 이고, 그것을 고른 항목은 아무것도 쓰지 않는다.
3. 답을 프로필 파일에 쓰고, 무엇이 기본과 달라졌는지 두세 줄로 보고한 뒤 원래 하던 `/ikken` 요청을 이어 간다.

## 취향 질문

| 질문 | 선택지 (첫 번째 = 기본 그대로) | 기본이 아닐 때 쓰는 곳 |
|---|---|---|
| 화면 문구 언어 | 기본 그대로(한국어, 용어는 영어 원문) · 영어 | `profile.md` explanation: "화면 문구는 영어로 쓴다. 데이터 값은 원문 그대로 둔다." |
| 색 분위기 | 기본 그대로(옅은 푸른 회색 종이) · 따뜻한 종이 · 고대비 | `tokens.css` — 아래 프리셋 |
| 설명 밀도 | 기본 그대로(카드 2–4문장) · 더 짧게 · 더 자세히 | `profile.md` explanation: 짧게 = "단계 카드 본문은 1–2문장, 수치는 stats 로만"; 자세히 = "단계 카드 본문은 4–6문장, 왜 그런지 한 문장씩 덧붙인다" |
| 3D 좌클릭 가로 회전 | 기본 그대로(장면이 마우스를 따라 돈다) · 카메라가 마우스를 따라 돈다 | `profile.md` interaction: "3D 좌클릭 가로 드래그는 카메라가 마우스를 따라 돈다(`theta += dx`) — 골격 코드를 이렇게 바꿔 쓴다." |

### 색 프리셋 (`tokens.css`)

골격마다 토큰 이름이 조금 다르다(walkthrough · explorer = `--ink`, view3d · overview = `--fg`). 프리셋은 두 이름을 모두 정의한다.
세 블록(라이트 · 시스템 다크 · 선택 다크)을 모두 쓴다 — 기본 골격과 같은 선택자다.

따뜻한 종이:

```css
:root{--bg:#F1ECE4;--panel:#FBF8F3;--ink:#2A241D;--fg:#2A241D;--muted:#6E6457;--line:#D9CFC1;--grid:#ECE5DA;--code:#F3EDE4}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1A1612;--panel:#231E19;--ink:#ECE4D8;--fg:#ECE4D8;--muted:#A89C8C;--line:#3A322A;--grid:#28221C;--code:#1E1915}}
:root[data-theme="dark"]{--bg:#1A1612;--panel:#231E19;--ink:#ECE4D8;--fg:#ECE4D8;--muted:#A89C8C;--line:#3A322A;--grid:#28221C;--code:#1E1915}
```

고대비:

```css
:root{--bg:#FFFFFF;--panel:#FFFFFF;--ink:#000000;--fg:#000000;--muted:#333333;--line:#8A8A8A;--grid:#E0E0E0;--code:#F0F0F0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#000000;--panel:#0A0A0A;--ink:#FFFFFF;--fg:#FFFFFF;--muted:#CCCCCC;--line:#777777;--grid:#222222;--code:#111111}}
:root[data-theme="dark"]{--bg:#000000;--panel:#0A0A0A;--ink:#FFFFFF;--fg:#FFFFFF;--muted:#CCCCCC;--line:#777777;--grid:#222222;--code:#111111}
```

## 보고

- 활성 프로필과 그 폴더
- 기본과 다른 점 (없으면 "기본과 같음")
- 피드백이 쌓이는 곳: `REPO`(저장소 기본 · commit · push) / `PROFILE`(그 프로필 폴더) / `READONLY`(설치본에서 default — 내 프로필을 만들라고 안내)
