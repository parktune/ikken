"""ikken 결과물 브라우저 점검 — chrome-devtools MCP 가 없을 때 쓰는 대체 수단.

playwright(python) 가 설치된 인터프리터로 실행한다:
    python check.py page.html [--out DIR] [--steps] [--size 1360x900]

하는 일 (결과는 JSON 한 덩어리로 stdout):
  - file:// 로 열고 console error / warning / pageerror 수집
  - 라이트·다크·좁은 폭(390px) 스크린샷
  - 좁은 폭에서 가로 스크롤 여부 (scrollWidth > innerWidth)
  - #next 가 있으면 끝까지 실제 마우스로 클릭하며 #prev/#next · #steps 위치가 변하는지, 버튼 중심이 덮여 있지 않은지
    — 기본 폭과 한 열로 접히는 760 폭 둘 다 (접힌 레이아웃에서 그림 높이가 버튼을 밀던 사고, 2026-10-21)
  - csp-host(iframe) 이면 auto-height host 흉내(iframe 높이를 안쪽 body.scrollHeight 에 맞추기)에서 높이가 한 값에 머무는지,
    그리고 iframe 폭 680 · 760 · 1000 · 1400 마다 같은 단계 점검 + 그림(.stage) 이 잘리지 않는지
    (보이는 .stage 의 scrollHeight ≤ clientHeight)
웹 서버를 띄우지 않는다.
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({"ok": False, "error": "playwright 가 없는 인터프리터입니다. playwright 가 설치된 python 으로 실행하세요."}))
    sys.exit(2)

RECT_JS = """sel => { const e = document.querySelector(sel); if (!e) return null;
  const r = e.getBoundingClientRect(); return [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)]; }"""
STAGE_JS = """() => [...document.querySelectorAll('.stage')].filter(e => e.offsetParent !== null)
  .map(e => ({h: e.clientHeight, sh: e.scrollHeight, fits: e.scrollHeight <= e.clientHeight + 1}))"""
COVER_JS = """sel => { const e = document.querySelector(sel); if (!e) return null;
  const r = e.getBoundingClientRect(); const t = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
  return !!t && (t === e || e.contains(t)); }"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--out", help="스크린샷 폴더 (기본: 임시 폴더)")
    ap.add_argument("--steps", action="store_true", help="단계마다 스크린샷")
    ap.add_argument("--size", default="1360x900")
    ap.add_argument("--wait", type=int, default=800, help="로드 후 대기 ms (CDN·애니메이션)")
    a = ap.parse_args()

    page_path = Path(a.html).resolve()
    out = Path(a.out or Path(tempfile.gettempdir()) / "ikken-check" / page_path.stem)
    out.mkdir(parents=True, exist_ok=True)
    w, h = (int(v) for v in a.size.split("x"))
    url = page_path.as_uri()
    rep = {"page": str(page_path), "out": str(out), "console": [], "shots": []}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        def open_page(scheme, width, height):
            ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme, device_scale_factor=1)
            pg = ctx.new_page()
            pg.on("console", lambda m: m.type in ("error", "warning") and rep["console"].append(
                {"scheme": scheme, "width": width, "type": m.type, "text": m.text[:300]}))
            pg.on("pageerror", lambda e: rep["console"].append({"scheme": scheme, "width": width, "type": "pageerror", "text": str(e)[:300]}))
            pg.goto(url, wait_until="networkidle")
            pg.wait_for_timeout(a.wait)
            return ctx, pg

        def shot(pg, name):
            f = out / f"{name}.png"
            pg.screenshot(path=str(f))
            rep["shots"].append(str(f))

        # 라이트 + 단계 점검
        ctx, pg = open_page("light", w, h)
        shot(pg, "light")
        # iframe 이 있으면(embed.py 의 csp-host) — 높이 판정, embed 모드, 빈 화면 여부
        if pg.query_selector("iframe"):
            fr = pg.frames[1] if len(pg.frames) > 1 else None
            rep["frame"] = {
                "iframe_height": pg.evaluate(RECT_JS, "iframe")[3],
                "embed_class": fr.evaluate("() => document.documentElement.classList.contains('embed')") if fr else None,
                "visible_elements": fr.evaluate("() => [...document.body.querySelectorAll('*')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 20 && r.height > 20; }).length") if fr else 0,
                "page_scrolls": fr.evaluate("() => document.scrollingElement.scrollHeight > innerHeight + 1") if fr else None,
            }
            # host 가 iframe 높이를 내용에 맞추는 경우(auto-height) — 높이가 한 값에 머무는지.
            # 문서 높이를 내용 · vh 가 정하면 높이 ↔ 내용이 물려 줄어들거나 떤다 (2026-10-26, confluence.md)
            if fr:
                ah = {}
                for start in (1000, 700):   # 시작 높이 둘 — 한 값에서만 우연히 맞는 경우를 거른다
                    hs = pg.evaluate("""start => new Promise(res => { const f = document.querySelector('iframe'), d = f.contentDocument, hs = [];
                        f.style.height = start + 'px';
                        setTimeout(() => { const t = setInterval(() => { const h = Math.max(d.body.scrollHeight, d.body.offsetHeight);
                          if (Math.abs(h - f.clientHeight) > 1) f.style.height = h + 'px'; hs.push(f.clientHeight);
                          if (hs.length >= 25) { clearInterval(t); res(hs); } }, 100); }, 300); })""", start)
                    ah[start] = {"last": hs[-3:], "stable": all(abs(x - start) <= 1 for x in hs)}
                rep["frame"]["autoheight"] = {"runs": ah, "stable": all(r["stable"] for r in ah.values())}
        def nav_pass(t, shots=False):
            """t = page 또는 frame. 처음 단계로 가서 끝까지 실제 클릭하며 조작부 위치·덮임을 잰다."""
            t.evaluate("() => document.body.dispatchEvent(new KeyboardEvent('keydown', {key: 'Home', bubbles: true}))")
            t.wait_for_timeout(150)
            rects, covered, n = [], [], 0
            while True:
                rects.append((t.evaluate(RECT_JS, "#prev"), t.evaluate(RECT_JS, "#next"), t.evaluate(RECT_JS, "#steps")))
                covered.append(t.evaluate(COVER_JS, "#next"))
                if shots:
                    shot(pg, f"step{n + 1:02d}")
                if t.eval_on_selector("#next", "e => e.disabled") or n > 60:
                    break
                t.click("#next")  # 실제 마우스 이벤트
                t.wait_for_timeout(150)
                n += 1
            fixed = all(r == rects[0] for r in rects)
            return {"count": n + 1, "nav_fixed": fixed, "nav_rects": rects[:1] if fixed else rects,
                    "next_uncovered": all(c is not False for c in covered[:-1]) if len(covered) > 1 else covered[0]}

        if pg.query_selector("#next"):
            rep["steps"] = nav_pass(pg, a.steps)
            shot(pg, "light_last")
            pg.set_viewport_size({"width": 760, "height": h}); pg.wait_for_timeout(300)
            rep["steps_760"] = nav_pass(pg)
            pg.set_viewport_size({"width": w, "height": h})
        if "frame" in rep and len(pg.frames) > 1:
            fr = pg.frames[1]
            if fr.query_selector("#next"):
                rep["embed"] = {}
                for fw in (680, 760, 1000, 1400):
                    pg.set_viewport_size({"width": fw + 60, "height": max(h, 1100)})
                    pg.eval_on_selector("iframe", f"f => {{ f.style.width = '{fw}px' }}"); pg.wait_for_timeout(400)
                    r = nav_pass(fr)
                    st = fr.evaluate(STAGE_JS)
                    rep["embed"][fw] = {"nav_fixed": r["nav_fixed"], "next_uncovered": r["next_uncovered"],
                                        "stage_fits": all(x["fits"] for x in st), "stages": st}
                    shot(pg, f"embed{fw}")
        ctx.close()

        # 다크
        ctx, pg = open_page("dark", w, h)
        shot(pg, "dark")
        ctx.close()

        # 좁은 폭
        ctx, pg = open_page("light", 390, 844)
        sw = pg.evaluate("() => [document.documentElement.scrollWidth, innerWidth]")
        rep["narrow"] = {"scrollWidth": sw[0], "innerWidth": sw[1], "no_hscroll": sw[0] <= sw[1]}
        shot(pg, "narrow")
        ctx.close()
        browser.close()

    errs = [c for c in rep["console"] if c["type"] in ("error", "pageerror")]
    rep["errors"] = len(errs)
    rep["ok"] = (not errs and rep["narrow"]["no_hscroll"] and rep.get("steps", {}).get("nav_fixed", True)
                 and rep.get("steps_760", {}).get("nav_fixed", True)
                 and all(e["nav_fixed"] and e["stage_fits"] for e in rep.get("embed", {}).values()))
    if "frame" in rep:
        rep["ok"] = rep["ok"] and rep["frame"]["visible_elements"] > 3 and rep["frame"].get("autoheight", {}).get("stable", True)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
