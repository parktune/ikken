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

결과물을 보고 앞으로도 지켜졌으면 하는 점이 있으면 `/ikken:feedback` 으로 알려 준다. 그 의견은 **활성 프로필**의 규칙에 남아 다음 생성부터 적용된다. 스타일은 사람마다(또는 한 사람이 여러 벌) 프로필로 나뉜다 — 아래 「프로필」.

```
/ikken:feedback 단계 설명 카드에 이 단계에서 쓰는 파라미터 값을 항상 보여줘
```

## 진행 순서

1. **프로필 → 규칙 읽기**: 기본 규칙(`profiles/default/guide/*.md`)을 읽고, 활성 프로필의 차이(`profile.md`)를 덮어쓴다. 처음 실행이면 프로필부터 정한다.
2. **재료 읽기**: 코드는 실행 경로를 따라가며 읽고, 논문은 전문을 읽고, 데이터는 직접 계산한다.
3. **구성안**: 핵심 한 문장, 화면, 단계, 만져 볼 것, 저장 경로를 다섯 줄 남짓으로 보여 주고 확인을 받는다.
4. **만들기**: 프로필로 해석한 골격(`scripts/profile.py template`)에서 시작해 단일 HTML 을 만든다(CDN 은 버전 고정 classic 빌드).
5. **점검**: 라이트·다크, 콘솔 에러, 단계 버튼 위치 고정, 좁은 폭을 확인한다.
6. **보고**: 경로와 보는 순서를 알려 준다.

## 페이지 유형

| 유형 | 언제 | 골격 |
|---|---|---|
| walkthrough | 알고리즘·규칙이 단계적으로 판정·변형 | `profiles/default/templates/walkthrough.html` |
| explorer | 실데이터를 프레임·레코드 단위로 탐색 | `profiles/default/templates/explorer.html` |
| overview | 저장소·시스템 구조와 흐름 | `profiles/default/templates/overview.html` |
| view3d | 높이·3D 기하가 본질 | `profiles/default/templates/view3d.html` |

## 프로필

규칙·골격·피드백은 프로필 단위로 쌓인다.

| 프로필 | 위치 | 담는 것 |
|---|---|---|
| `default` | 저장소 `profiles/default/` | 규칙 6개(`guide/`) · 골격 4개(`templates/`) · 이력(`FEEDBACK.md`) — 배포자가 다듬어 배포하는 기본 스타일 |
| 사용자 프로필 | `~/.claude/ikken/profiles/<이름>/` | 기본과 **다른 점만**: `profile.md`(규칙 덮어쓰기) · `tokens.css`(색·글꼴, 선택) · `templates/`(골격 교체, 선택) · `FEEDBACK.md` |

- 활성 프로필은 `~/.claude/ikken/config.json` 하나다. `/ikken` 을 처음 실행하면 이름과 취향 질문 네 개(화면 언어 · 색 분위기 · 설명 밀도 · 3D 회전 방향)로 프로필을 만든다. 모두 "기본 그대로" 를 고를 수 있다.
- 관리: `/ikken:config` (현재·목록) · `use <이름>` · `new <이름> [--from <원본>]` · `edit` · `delete <이름>`.
- 피드백: 활성 프로필이 `default` 이고 원본 저장소를 쓰는 중이면 저장소 기본에 반영하고 commit · push 한다. 사용자 프로필이 활성이면 그 프로필 폴더에만 쓴다.
- 원저작자가 아닌 사람이 자기 clone 에서 `default` 를 고치면, 최신 저장소를 pull 할 때 충돌은 직접 관리해야 한다. 자기 스타일을 지키며 업데이트를 받으려면 사용자 프로필을 쓴다 — 프로필은 저장소 밖에 있어 pull 과 부딪히지 않는다.

## 구성

```
.claude-plugin/          plugin.json, marketplace.json
SKILL.md                 /ikken
skills/feedback/         /ikken:feedback
skills/config/           /ikken:config (프로필 · 처음 설정 · 취향 질문)
profiles/default/        기본 프로필 — guide/ (설명·상호작용·스타일·유형·점검·Confluence) · templates/ · FEEDBACK.md
scripts/profile.py       프로필 해석 · 골격 복사(+토큰) · 피드백 대상 (표준 라이브러리만)
scripts/embed.py         Confluence 임베드 버전 변환 (표준 라이브러리만)
scripts/check.py         브라우저 점검 (playwright 필요, chrome-devtools MCP 대체)
requirements/            요구사항
```

## 설치

### 개발용 (원본 저장소에서 바로 반영)

```bash
git clone https://github.com/taeyoonB/ikken.git <경로>
ln -s <경로> ~/.claude/skills/ikken      # 다음 세션부터 ikken@skills-dir 로 로드
```

이 방식에서 활성 프로필이 `default` 면 `/ikken:feedback` 이 저장소의 `profiles/default/` 를 직접 고치고 commit 한다.

### 공유용

```
/plugin marketplace add taeyoonB/ikken
/plugin install ikken@ikken
```

설치본에서는 저장소를 고칠 수 없으니 처음 실행 때 사용자 프로필을 만든다. 피드백은 그 프로필에 쌓인다.

## Confluence 임베드

요청할 때만 만든다. 자세한 규칙은 `profiles/default/guide/confluence.md` 에 있다.

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
