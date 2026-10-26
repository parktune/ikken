"""ikken 프로필 — 어떤 규칙·골격을 읽고, 피드백을 어디에 쓸지 정한다.

기본(default) 프로필은 저장소의 profiles/default/ 에 있고(배포자 스타일), 사용자 프로필은
~/.claude/ikken/profiles/<이름>/ 에 기본과 다른 부분만 둔다. 활성 프로필은 ~/.claude/ikken/config.json.

    python3 profile.py status [--json]          활성 프로필 · 읽을 파일 · 골격 · 피드백 대상
    python3 profile.py list                     프로필 목록
    python3 profile.py use <이름>               활성 프로필 바꾸기 ("default" = 저장소 기본)
    python3 profile.py new <이름> [--from <원본>] [--use]   새 프로필 (기본과 차이 없음에서 시작, 또는 원본 복제)
    python3 profile.py delete <이름>            프로필 지우기 (활성 프로필은 못 지움)
    python3 profile.py template <유형> <출력.html>  골격 복사 — 프로필 골격이 있으면 그것, tokens.css 가 있으면 덧붙임
    python3 profile.py feedback-target          피드백을 쓸 곳: REPO <경로> | PROFILE <경로> | READONLY <이유>

IKKEN_HOME 환경 변수로 ~/.claude/ikken 대신 다른 폴더를 쓸 수 있다(점검용).
표준 라이브러리만 쓴다.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent            # 플러그인 루트
DEFAULT = ROOT / "profiles" / "default"
HOME = Path(os.environ.get("IKKEN_HOME") or Path.home() / ".claude" / "ikken")
CONFIG = HOME / "config.json"
GUIDES = ["explanation", "interaction", "style", "patterns", "verify", "confluence"]
TEMPLATES = ["walkthrough", "explorer", "overview", "view3d", "compare"]
NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")

PROFILE_MD = """# {name} 프로필

기본(default) 프로필 위에 덮어쓰는 규칙이다. 기본과 충돌하면 이 파일이 이긴다.
절 이름은 기본의 guide 파일 이름과 같다. 비어 있는 절은 기본 그대로다.
만든 날: {date}{origin}

## explanation

## interaction

## style

## patterns

## verify

## confluence

## 진행 (SKILL)
"""
FEEDBACK_MD = """# {name} 피드백 이력

`/ikken:feedback` 이 이 프로필에 반영한 피드백이다. 최신이 위에 온다.

| 날짜 | 피드백 | 반영 | 대상 |
|---|---|---|---|
"""


def load_config():
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, ValueError):
        return None


def save_config(cfg):
    HOME.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n")


def pdir(name):
    return DEFAULT if name == "default" else HOME / "profiles" / name


def local_profiles():
    d = HOME / "profiles"
    return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.is_dir() else []


def repo_writable():
    """원본 저장소에서 쓰는 중인가 — git 작업 트리이고 쓸 수 있으면 True (마켓플레이스 설치본은 False 로 본다)."""
    try:
        top = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    except OSError:
        return False
    return top.returncode == 0 and os.access(ROOT, os.W_OK) and "/plugins/cache/" not in str(ROOT)


def status():
    cfg = load_config()
    active = (cfg or {}).get("active")
    out = {"root": str(ROOT), "home": str(HOME), "configured": cfg is not None, "active": active}
    if active and active != "default" and not pdir(active).is_dir():
        out["error"] = f"활성 프로필 '{active}' 폴더가 없다 — /ikken:config 로 다시 고른다"
    reads = [str(DEFAULT / "guide" / f"{g}.md") for g in GUIDES]
    tmpl, tokens = {}, None
    for t in TEMPLATES:
        tmpl[t] = str(DEFAULT / "templates" / f"{t}.html")
    if active and active != "default" and pdir(active).is_dir():
        p = pdir(active)
        if (p / "profile.md").is_file():
            reads.append(str(p / "profile.md"))
        if (p / "tokens.css").is_file():
            tokens = str(p / "tokens.css")
        for t in TEMPLATES:
            if (p / "templates" / f"{t}.html").is_file():
                tmpl[t] = str(p / "templates" / f"{t}.html")
    out.update({"read": reads, "templates": tmpl, "tokens": tokens, "feedback": feedback_target(active)})
    return out


def feedback_target(active=None):
    if active is None:
        active = ((load_config() or {}).get("active")) or "default"
    if active == "default":
        if repo_writable():
            return {"kind": "REPO", "path": str(DEFAULT), "history": str(DEFAULT / "FEEDBACK.md")}
        return {"kind": "READONLY", "reason": "활성 프로필이 default 인데 저장소를 고칠 수 없다(설치본) — /ikken:config new <이름> 으로 내 프로필을 만든다"}
    p = pdir(active)
    return {"kind": "PROFILE", "path": str(p), "history": str(p / "FEEDBACK.md")}


def cmd_new(name, src=None, use=False):
    if not NAME.match(name) or name == "default":
        sys.exit(f"이름은 소문자 · 숫자 · - · _ 만 (default 제외): {name}")
    dst = pdir(name)
    if dst.exists():
        sys.exit(f"이미 있다: {dst}")
    if src and src != "default":
        if not pdir(src).is_dir():
            sys.exit(f"원본 프로필이 없다: {src}")
        shutil.copytree(pdir(src), dst)
        fb = dst / "FEEDBACK.md"
        fb.write_text(FEEDBACK_MD.format(name=name))
        md = dst / "profile.md"
        if md.is_file():
            md.write_text(re.sub(r"^# .* 프로필", f"# {name} 프로필", md.read_text(), count=1, flags=re.M))
    else:
        dst.mkdir(parents=True)
        (dst / "profile.md").write_text(PROFILE_MD.format(name=name, date=dt.date.today().isoformat(), origin=""))
        (dst / "FEEDBACK.md").write_text(FEEDBACK_MD.format(name=name))
    if use or load_config() is None:
        save_config({"active": name})
    print(json.dumps({"created": str(dst), "active": (load_config() or {}).get("active")}, ensure_ascii=False))


def cmd_use(name):
    if name != "default" and not pdir(name).is_dir():
        sys.exit(f"프로필이 없다: {name} — 목록: default, {', '.join(local_profiles()) or '(없음)'}")
    save_config({"active": name})
    print(json.dumps({"active": name, "feedback": feedback_target(name)}, ensure_ascii=False))


def cmd_delete(name):
    if name == "default":
        sys.exit("default 는 지울 수 없다")
    if (load_config() or {}).get("active") == name:
        sys.exit(f"'{name}' 은 활성 프로필이다 — 먼저 다른 프로필로 바꾼다")
    if not pdir(name).is_dir():
        sys.exit(f"프로필이 없다: {name}")
    shutil.rmtree(pdir(name))
    print(json.dumps({"deleted": name}, ensure_ascii=False))


def cmd_template(kind, out):
    if kind not in TEMPLATES:
        sys.exit(f"골격 유형: {', '.join(TEMPLATES)}")
    st = status()
    html = Path(st["templates"][kind]).read_text()
    if st["tokens"]:
        css = Path(st["tokens"]).read_text()
        tag = f'<style id="ikken-profile-tokens">\n/* 프로필 토큰 — {st["active"]} (기본 토큰 뒤에 와서 덮어쓴다) */\n{css}\n</style>\n'
        i = html.find("</head>")
        html = html[:i] + tag + html[i:] if i >= 0 else tag + html
    Path(out).write_text(html)
    print(json.dumps({"out": out, "from": st["templates"][kind], "tokens": st["tokens"], "profile": st["active"]}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="ikken 프로필")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--json", action="store_true")
    sub.add_parser("list")
    s = sub.add_parser("use"); s.add_argument("name")
    s = sub.add_parser("new"); s.add_argument("name"); s.add_argument("--from", dest="src"); s.add_argument("--use", action="store_true")
    s = sub.add_parser("delete"); s.add_argument("name")
    s = sub.add_parser("template"); s.add_argument("kind"); s.add_argument("out")
    sub.add_parser("feedback-target")
    a = ap.parse_args()
    if a.cmd == "status":
        st = status()
        if a.json:
            print(json.dumps(st, ensure_ascii=False, indent=1))
        else:
            print(f"활성 프로필: {st['active'] or '(설정 없음 — 처음 실행)'}")
            print("읽을 규칙:\n  " + "\n  ".join(st["read"]))
            print("골격:\n  " + "\n  ".join(f"{k}: {v}" for k, v in st["templates"].items()))
            print(f"토큰 덮어쓰기: {st['tokens'] or '없음'}")
            fb = st["feedback"]
            print(f"피드백 대상: {fb['kind']} {fb.get('path') or fb.get('reason')}")
            if st.get("error"):
                print("오류: " + st["error"])
    elif a.cmd == "list":
        act = (load_config() or {}).get("active")
        for n in ["default"] + local_profiles():
            print(("* " if n == act else "  ") + n + ("  (저장소 기본)" if n == "default" else f"  {pdir(n)}"))
    elif a.cmd == "use":
        cmd_use(a.name)
    elif a.cmd == "new":
        cmd_new(a.name, a.src, a.use)
    elif a.cmd == "delete":
        cmd_delete(a.name)
    elif a.cmd == "template":
        cmd_template(a.kind, a.out)
    elif a.cmd == "feedback-target":
        fb = feedback_target()
        print(fb["kind"], fb.get("path") or fb.get("reason"))


if __name__ == "__main__":
    main()
