---
name: feedback
description: ikken 결과물에 대한 사용자 피드백을 활성 프로필의 규칙(guide·templates · 사용자 프로필이면 profile.md·tokens.css)에 반영해 다음 생성부터 적용되게 하고, 필요하면 방금 만든 HTML 도 고친다. "/ikken:feedback <의견> [html 경로]", 또는 ikken 결과물을 보고 "앞으로는 이렇게", "이건 항상", "다음부터는" 같은 지적을 할 때 쓴다.
argument-hint: "<피드백 내용> [대상 html 경로]"
---

# ikken:feedback

피드백 하나가 다음 생성부터 지켜지는 규칙이 되게 한다. 이 플러그인이 다른 시각화 도구와 다른 점은 이 누적된 규칙이다. 그러니 문장 하나하나를 신중히 쓴다.

플러그인 루트는 `${CLAUDE_PLUGIN_ROOT}` 이고, 이 스킬 파일의 두 단계 위 디렉터리다.

## 1. 대상과 피드백 파악

- 대상 HTML: 인자에 경로가 있으면 그 파일을 쓴다. 없으면 이 대화에서 ikken 이 마지막으로 만든 HTML 을 쓴다. 둘 다 없으면 규칙만 반영한다.
- 피드백 원문을 그대로 보관한다. 요약하지 않고 인용할 수 있어야 한다.
- 피드백이 가리키는 화면 요소를 대상 HTML 에서 찾아 무엇이 문제인지 직접 확인한다.

## 2. 이번만인가, 앞으로의 규칙인가

| 종류 | 예 | 반영 |
|---|---|---|
| 이번 결과물의 내용 오류·주제 특유 | "이 수치 틀렸어", "3단계 설명이 코드와 달라" | HTML 만 고친다 |
| 앞으로도 적용될 규칙 | "버튼 위치가 변하면 안 돼", "색 견본 빼", "항상 출처를 달아" | 규칙 + HTML |

구분이 애매하면 `AskUserQuestion` 으로 한 번 묻는다: `앞으로 규칙으로 (Recommended)` / `이번 결과물만`.

## 3. 규칙을 어디에 쓰나 — 활성 프로필이 정한다

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/profile.py" feedback-target      # REPO <경로> | PROFILE <경로> | READONLY <이유>
```

- **REPO** — 활성 프로필이 `default` 이고 원본 저장소에서 쓰는 중(배포자). 저장소의 `profiles/default/` 를 고친다(아래 표의 파일). 진행 절차는 루트 `SKILL.md`. 7 에서 commit · push 한다.
  - 원저작자가 아닌 사람이 자기 clone 에서 default 를 고치면, 최신 저장소를 pull 할 때 충돌은 그 사람이 직접 관리한다. 이 경우 보고에 한 줄 알린다.
- **PROFILE** — 활성 프로필이 사용자 프로필(`~/.claude/ikken/profiles/<이름>/`). **그 폴더만** 고치고 저장소는 건드리지 않는다.
  - 규칙 → `profile.md` 의 해당 절. 절 이름 = 아래 표의 guide 파일 이름(`explanation` · `interaction` · `style` · `patterns` · `verify` · `confluence`), 진행 절차는 `진행 (SKILL)` 절. 기본 규칙을 뒤집는 것이면 "기본과 달리 …" 로 쓴다.
  - 색·글꼴 토큰 → `tokens.css` (라이트 · 시스템 다크 · 선택 다크 세 블록, `skills/config/SKILL.md` 프리셋과 같은 모양).
  - 골격 코드로 강제할 것(조작 방향 · 단축키 등) → `profile.md` 에 적는다. 자주 쓰는 골격이면 `templates/<유형>.html` 로 복사해 고친다:
    `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/profile.py" template <유형> <프로필 경로>/templates/<유형>.html` 로 시작.
- **READONLY** — 설치본에서 `default` 가 활성. 저장할 곳이 없으니 `/ikken:config new <이름>` 으로 내 프로필을 만들자고 묻고, 만들면 PROFILE 로 이어 간다.

규칙이 들어갈 곳 (REPO 는 `profiles/default/` 아래 파일, PROFILE 은 `profile.md` 의 같은 이름 절):

| 피드백 주제 | 파일 / 절 |
|---|---|
| 설명 순서, 문장, 용어, 숫자 표기, 무엇을 넣고 빼나 | `guide/explanation.md` / `explanation` |
| 버튼·키보드·마우스·단계·범례·토글·선택 | `guide/interaction.md` / `interaction` |
| 색, 글꼴, 간격, 컴포넌트 모양, 라이브러리 | `guide/style.md` / `style` (+ `tokens.css`) |
| 페이지 유형, 레이아웃 선택, 데이터 싣기 | `guide/patterns.md` / `patterns` |
| 점검 절차 | `guide/verify.md` / `verify` |
| Confluence 임베드 | `guide/confluence.md` / `confluence` |
| `/ikken` 진행 절차(구성안, 질문, 보고) | 루트 `SKILL.md` / `진행 (SKILL)` |
| 모든 결과물에 들어가는 코드(테마·로더·조작) | `templates/*.html` — 다섯 골격 모두 일관되게 / 프로필 `templates/` |
| 스크립트 동작(`check.py` · `embed.py` · `profile.py`) | 루트 `scripts/` — REPO 일 때만 |

## 4. 규칙 쓰는 법

- 해당 절에 **명령형 한 줄**로 쓴다. 필요하면 바로 아래에 이유 한 줄을 붙인다.
- 이유에는 사용자 원문을 짧게 인용하고 날짜를 적는다: `(2026-10-14 "이전/다음 위치가 변하면 연속 클릭을 못하잖아")`.
- **일반화하되 범위를 적는다.** 특정 사례에 대한 지적이라도 같은 상황 전체에 적용되게 쓴다. 다만 적용 범위가 좁으면 그 범위("3D 페이지에서", "단계형에서")를 명시한다.
- 기존 규칙과 겹치거나 충돌하면 덧붙이지 말고 **기존 문장을 고쳐 합친다**. 충돌하면 새 피드백이 이긴다.
- 템플릿 코드로 강제할 수 있는 규칙(위치 고정, 단축키, 조작 방향)은 템플릿도 함께 고친다. 문서에만 적힌 규칙은 지켜지지 않는다.
- 규칙 수를 늘리는 것보다 기존 규칙을 선명하게 다듬는 것을 먼저 고려한다.

## 5. 이력

`feedback-target` 이 알려 준 프로필의 `FEEDBACK.md` 맨 위 표에 한 줄을 추가한다 — REPO 면 `profiles/default/FEEDBACK.md`, PROFILE 이면 `<프로필>/FEEDBACK.md`.

```
| 2026-10-14 | <원문 요약 한 줄> | <반영 파일> | <대상 html 이름 또는 —> |
```

## 6. 대상 HTML 고치기

- 규칙대로 대상 HTML 을 고친다. 그 HTML 에 Confluence 버전이 있으면 `scripts/embed.py` 로 다시 만든다.
- `guide/verify.md` 대로 점검한다(웹 서버는 띄우지 않는다).
- 골격을 고쳤으면 그 골격도 `scripts/check.py` 로 점검한다(REPO: `profiles/default/templates/`, PROFILE: `<프로필>/templates/`).

## 7. 커밋 (REPO 일 때만)

```bash
ROOT="$(realpath "${CLAUDE_PLUGIN_ROOT}")"
git -C "$ROOT" add -A && git -C "$ROOT" commit -m "feedback: <요약>"
```

PROFILE 은 커밋하지 않는다(로컬 폴더). 사용자가 그 폴더를 따로 git 으로 관리하면 그쪽은 사용자가 한다.

- 원격(`origin`)이 있으면 push 한다. 없으면 커밋만 한다.
- `plugin.json` 의 version 은 사용자가 배포를 말할 때만 올린다.

## 8. 보고

- 반영한 프로필(`default` 저장소 / 사용자 프로필 이름)
- 바뀐 규칙: 파일별 한두 줄 (전/후)
- 대상 HTML 수정 여부와 점검 결과
- 커밋 해시 (REPO 일 때)
