"""ikken HTML → Confluence 임베드 버전 변환.

    python3 embed.py page.html [--out page.confluence.html] [--no-host] [--max-mb 2.0]

근거: guide/confluence.md.
- <script src="https://…"> 를 내려받아 inline classic script 로 (캐시 ~/.cache/ikken/cdn)
- type="module" · importmap · 동적 import( 가 있으면 실패 — Confluence CSP 가 막는다
- Google Fonts <link> 제거, 그 밖의 외부 CSS 는 inline <style>
- <script type="application/json" id=…> 데이터 → gzip+base64 (loadData() 가 DecompressionStream 으로 푼다)
- embed 런타임 주입: iframe 자동 감지 · ?embed=0|1 · ?theme= · 150px 높이 판정 · fullscreen · 패널 기본 열림/좁으면 접기
- 2 MB 이상이면 실패(종료 코드 1)
- 점검용 page.csp-host.html: 엄격한 CSP meta + srcdoc iframe(폭 760, 높이 미지정)
표준 라이브러리만 쓴다.
"""
import argparse
import base64
import gzip
import hashlib
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

CACHE = Path.home() / ".cache" / "ikken" / "cdn"

RUNTIME = r"""
(function(){
  /* ikken embed runtime — guide/confluence.md */
  var q = new URLSearchParams(location.search), root = document.documentElement;
  var inFrame = false; try { inFrame = window.self !== window.top; } catch (e) { inFrame = true; }
  var em = q.get('embed'); var on = em === '1' ? true : em === '0' ? false : inFrame;
  if (!on) return;
  root.classList.add('embed');
  var th = q.get('theme'); if (th === 'light' || th === 'dark') root.setAttribute('data-theme', th);
  /* 높이: host 가 높이를 안 준 것이 확실할 때만 (same-origin frameElement, 높이 ≤ 160 — CSS 기본 150 이 신호) */
  var fe = null; try { fe = window.frameElement; } catch (e) {}
  function claim(){
    if (fe && fe.getBoundingClientRect().height <= 160) {
      var want = Math.max(400, Math.min(1200, 1000));
      fe.style.height = want + 'px';
    }
  }
  claim();
  function hint(){
    var low = innerHeight < 300, el = document.getElementById('ikken-hgt');
    if (low && !el) {
      el = document.createElement('div'); el.id = 'ikken-hgt';
      el.textContent = '매크로 높이가 낮습니다 — Height 를 1000 으로 설정하세요';
      el.style.cssText = 'position:fixed;left:0;right:0;top:0;z-index:99;background:#2b2418;color:#ffd08a;font:12px/18px system-ui,sans-serif;padding:2px 8px;text-align:center;border-bottom:1px solid #5a4a22';
      document.body.appendChild(el);
    } else if (!low && el) el.remove();
  }
  /* 패널: 기본 열림. 자리가 모자라면(900×430 미만) 접고, 크기가 바뀌면 다시 판단. 사용자가 직접 여닫으면 손대지 않음 */
  var touched = false;
  function room(){ return innerWidth >= 900 && innerHeight >= 430; }
  function panel(){
    if (touched) return;
    var host = document.querySelector('#layout,#main'); if (!host) return;
    host.classList.toggle('nopanel', !room());
    dispatchEvent(new Event('resize'));
  }
  addEventListener('DOMContentLoaded', function(){
    hint(); panel();
    var b = document.getElementById('panel') || document.getElementById('b-panel');
    if (b) b.addEventListener('click', function(){ touched = true; }, true);
    if (document.fullscreenEnabled) {
      /* 전체화면 버튼은 테마 버튼 바로 오른쪽 — 테마 버튼과 같은 모양(#theme 규칙 복사)으로, 테마 버튼 자리에 두고 테마 버튼을 왼쪽으로 민다 */
      var f = document.createElement('button'); f.title = '전체화면'; f.setAttribute('aria-label', '전체화면');
      f.innerHTML = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4"/></svg>';
      f.onclick = function(){ document.fullscreenElement ? document.exitFullscreen() : root.requestFullscreen(); };
      var th = document.getElementById('theme');
      if (th) {
        f.id = 'ikfs'; f.className = th.className;
        try {
          var css = '';
          for (var i = 0; i < document.styleSheets.length; i++) {
            var rules = document.styleSheets[i].cssRules || [];
            for (var j = 0; j < rules.length; j++) {
              var r = rules[j];
              if (r.selectorText && /#theme\b/.test(r.selectorText)) css += r.cssText.replace(/#theme\b/g, '#ikfs') + '\n';
              else if (r.cssRules && r.media) {   // @media 안의 #theme 규칙도
                var inner = '';
                for (var k = 0; k < r.cssRules.length; k++) if (r.cssRules[k].selectorText && /#theme\b/.test(r.cssRules[k].selectorText)) inner += r.cssRules[k].cssText.replace(/#theme\b/g, '#ikfs');
                if (inner) css += '@media ' + r.media.mediaText + '{' + inner + '}\n';
              }
            }
          }
          var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
        } catch (e) {}
        th.parentNode.insertBefore(f, th.nextSibling);
        var cs = getComputedStyle(th);
        if (cs.position === 'absolute' || cs.position === 'fixed') {
          var w = th.getBoundingClientRect().width || 34, gap = 6;
          f.style.position = cs.position; f.style.top = cs.top; f.style.right = cs.right;
          th.style.right = 'calc(' + cs.right + ' + ' + (w + gap) + 'px)';
          var par = th.parentElement;
          if (par && par.tagName === 'HEADER') par.style.paddingRight = ((parseFloat(getComputedStyle(par).paddingRight) || 0) + w + gap) + 'px';
        } else f.style.marginLeft = '6px';
      } else {
        var hud = document.querySelector('.hud') || document.querySelector('header');
        if (hud) {
          if (hud.classList.contains('hud')) hud.appendChild(f);
          else { f.className = 'icon'; f.style.cssText = 'position:absolute;top:8px;right:16px'; hud.appendChild(f); }
        }
      }
    }
  });
  addEventListener('resize', function(){ hint(); });
  var rt; addEventListener('resize', function(e){ if (!e.isTrusted) return; clearTimeout(rt); rt = setTimeout(panel, 120); });
})();
"""

CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
       "img-src data:; font-src data:; connect-src 'none'")


def fetch(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + "_" + url.rsplit("/", 1)[-1])
    if not f.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "ikken-embed"})
        with urllib.request.urlopen(req, timeout=60) as r:
            f.write_bytes(r.read())
    return f.read_text(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--out")
    ap.add_argument("--no-host", action="store_true", help="CSP 점검용 host 페이지를 만들지 않음")
    ap.add_argument("--max-mb", type=float, default=2.0)
    a = ap.parse_args()

    src = Path(a.html).resolve()
    s = src.read_text(encoding="utf-8")
    log = {"page": str(src), "inlined": [], "removed": [], "warnings": []}

    # 1. 모듈 로더 금지
    bad = []
    if re.search(r'<script[^>]*type=["\']module["\']', s): bad.append('type="module"')
    if re.search(r'<script[^>]*type=["\']importmap["\']', s): bad.append("importmap")
    if re.search(r'\bimport\s*\(', s): bad.append("dynamic import(")
    if bad:
        print(json.dumps({"ok": False, "error": "Confluence CSP 에서 막히는 모듈 로딩: " + ", ".join(bad) +
                          " — guide/style.md 「라이브러리」의 classic(UMD) 빌드로 바꾸세요."}, ensure_ascii=False))
        sys.exit(1)

    # 2. 외부 script → inline
    def rep_script(m):
        url = m.group(2)
        code = fetch(url).replace("</script", "<\\/script")
        log["inlined"].append({"url": url, "kb": round(len(code.encode()) / 1024)})
        return f"<script>/* {url} */\n{code}\n</script>"
    s = re.sub(r'<script([^>]*?)\ssrc=["\'](https?://[^"\']+)["\']([^>]*)>\s*</script>', rep_script, s)

    # 3. stylesheet: Google Fonts 제거, 그 밖은 inline
    def rep_link(m):
        tag = m.group(0)
        href = re.search(r'href=["\']([^"\']+)["\']', tag)
        if "fonts.googleapis.com" in tag or "fonts.gstatic.com" in tag:
            log["removed"].append(href.group(1) if href else tag[:60])
            return ""
        if 'rel="stylesheet"' in tag or "rel='stylesheet'" in tag:
            url = href.group(1)
            if url.startswith("http"):
                code = fetch(url)
                if re.search(r"url\((?!['\"]?data:)", code):
                    log["warnings"].append(f"{url}: CSS 안의 url(…) 리소스(폰트 등)는 CSP 에서 막힙니다 — 시스템 글꼴로 대체됨")
                log["inlined"].append({"url": url, "kb": round(len(code.encode()) / 1024)})
                return f"<style>/* {url} */\n{code}\n</style>"
        return tag
    s = re.sub(r"<link\b[^>]*>", rep_link, s)

    # 4. JSON 데이터 → gzip+base64
    def rep_data(m):
        attrs, body = m.group(1), m.group(2)
        raw = body.strip().encode()
        if len(raw) < 2048:
            return m.group(0)
        b64 = base64.b64encode(gzip.compress(raw, 9)).decode()
        attrs2 = attrs.replace('type="application/json"', 'type="application/octet-stream" data-encoding="gzip-base64"')
        log.setdefault("data", []).append({"kb_before": round(len(raw) / 1024), "kb_after": round(len(b64) / 1024)})
        return f"<script{attrs2}>{b64}</script>"
    s = re.sub(r'<script(\s[^>]*type="application/json"[^>]*)>(.*?)</script>', rep_data, s, flags=re.S)
    if "data-encoding=\"gzip-base64\"" in s and "DecompressionStream" not in s:
        log["warnings"].append("데이터를 압축했지만 페이지에 loadData()(DecompressionStream) 가 없습니다 — 템플릿의 loadData 를 쓰세요")

    # 5. embed 런타임 — <head> 맨 앞(스타일 적용 전에 html.embed 가 붙도록)
    s = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + "\n<script>" + RUNTIME + "</script>", s, count=1)

    out = Path(a.out) if a.out else src.with_name(src.stem + ".confluence.html")
    out.write_text(s, encoding="utf-8")
    mb = out.stat().st_size / 1024 / 1024
    log["out"] = str(out)
    log["mb"] = round(mb, 2)

    # 6. CSP host
    if not a.no_host:
        host = out.with_name(src.stem + ".csp-host.html")
        host.write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>CSP host · {html.escape(src.name)}</title>
<style>body{{margin:0;padding:16px;background:#f4f5f7;font:13px system-ui}} .page{{box-sizing:border-box;width:760px;max-width:100%;background:#fff;border:1px solid #ddd;padding:12px}} iframe{{border:1px solid #bbb;width:100%;display:block}}</style>
</head><body><div class="page"><p>Confluence 재현: CSP <code>{html.escape(CSP)}</code> · iframe 높이 미지정(150)</p>
<iframe srcdoc="{html.escape(s, quote=True)}"></iframe></div></body></html>""", encoding="utf-8")
        log["csp_host"] = str(host)

    log["ok"] = mb < a.max_mb
    if not log["ok"]:
        log["error"] = f"{mb:.2f} MB ≥ {a.max_mb} MB — Confluence 가 저장하지 못합니다. 좌표 반올림 → 샘플 축소 → 라이브러리 제거 순으로 줄이세요."
    print(json.dumps(log, ensure_ascii=False, indent=1))
    sys.exit(0 if log["ok"] else 1)


if __name__ == "__main__":
    main()
