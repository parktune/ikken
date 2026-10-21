# ikken 一見

> 百聞不如一見 — 백 번 듣는 것보다 한 번 보는 것이 낫다.

이론·알고리즘·코드·논문·데이터를 **몇 분 동안 보고 만져서** 이해할 수 있게 해 주는 Claude Code 플러그인이다.
`/ikken` 에 주제나 경로를 주면 interactive HTML 한 장이 만들어진다.

```
/ikken Kalman filter 가 예측과 측정을 섞는 방식
/ikken ./src/pipeline/crop.py 의 crop 단계
/ikken https://arxiv.org/abs/1706.03762
/ikken ~/data/route.json 이 무엇을 담고 있는지
/ikken <...> confluence          # Confluence 임베드 버전도 함께
```

결과물을 보고 앞으로도 지켜졌으면 하는 점이 있으면 `/ikken:feedback` 으로 알려 준다. 그 의견은 플러그인 규칙(`guide/`)에 남아 다음 생성부터 적용된다.

```
/ikken:feedback 단계 설명 카드에 이 단계에서 쓰는 파라미터 값을 항상 보여줘
```

## 진행 순서

1. **규칙 읽기**: `guide/*.md` 와, 있으면 개인 규칙 `~/.claude/ikken/preferences.md` 를 읽는다.
2. **재료 읽기**: 코드는 실행 경로를 따라가며 읽고, 논문은 전문을 읽고, 데이터는 직접 계산한다.
3. **구성안**: 핵심 한 문장, 화면, 단계, 만져 볼 것, 저장 경로를 다섯 줄 남짓으로 보여 주고 확인을 받는다.
4. **만들기**: `templates/` 의 골격에서 시작해 단일 HTML 을 만든다(CDN 은 버전 고정 classic 빌드).
5. **점검**: 라이트·다크, 콘솔 에러, 단계 버튼 위치 고정, 좁은 폭을 확인한다.
6. **보고**: 경로와 보는 순서를 알려 준다.

## 페이지 유형

| 유형 | 언제 | 골격 |
|---|---|---|
| walkthrough | 알고리즘·규칙이 단계적으로 판정·변형 | `templates/walkthrough.html` |
| explorer | 실데이터를 프레임·레코드 단위로 탐색 | `templates/explorer.html` |
| overview | 저장소·시스템 구조와 흐름 | `templates/overview.html` |
| view3d | 높이·3D 기하가 본질 | `templates/view3d.html` |

## 구성

```
.claude-plugin/       plugin.json, marketplace.json
SKILL.md              /ikken
skills/feedback/      /ikken:feedback
guide/                설명·상호작용·스타일·유형·점검·Confluence 규칙
templates/            페이지 유형별 골격 (그대로 열리는 데모 포함)
scripts/embed.py      Confluence 임베드 버전 변환 (표준 라이브러리만)
scripts/check.py      브라우저 점검 (playwright 필요, chrome-devtools MCP 대체)
FEEDBACK.md           피드백 이력
requirements/         요구사항
```

## 설치

### 개발용 (원본 저장소에서 바로 반영)

```bash
git clone https://github.com/taeyoonB/ikken.git <경로>
ln -s <경로>/ikken ~/.claude/skills/ikken      # 다음 세션부터 ikken@skills-dir 로 로드
```

이 방식에서는 `/ikken:feedback` 이 저장소의 `guide/` 를 직접 고치고 commit 한다. 고친 내용은 다음 `/ikken` 호출부터 바로 적용된다.

### 공유용 (GitHub 에 올린 뒤)

```
/plugin marketplace add taeyoonB/ikken
/plugin install ikken@ikken
```

설치본에서 `/ikken:feedback` 을 쓰면 개인 규칙 `~/.claude/ikken/preferences.md` 에 쌓인다.

## Confluence 임베드

요청할 때만 만든다. 자세한 규칙은 `guide/confluence.md` 에 있다.

```bash
python3 scripts/embed.py page.html     # → page.confluence.html (붙여 넣을 것) + page.csp-host.html (로컬 점검용)
```

"Advanced HTML & Iframe Embed" 매크로에 `page.confluence.html` 원문을 붙이고 Height 를 1000 으로 둔다. 파일은 2 MB 미만이어야 한다.

## 브라우저 점검

```bash
python scripts/check.py page.html --steps     # playwright 가 있는 python 으로
```

## 라이선스

MIT
