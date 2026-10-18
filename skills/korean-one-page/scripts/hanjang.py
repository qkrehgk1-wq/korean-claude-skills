#!/usr/bin/env python3
"""korean-one-page(한 장 안내문): 한국어 안내문·절차 매뉴얼을 '오프라인 한 장 HTML'로 만든다.

모델은 JSON 초안만 쓰고, 이 스크립트가 배치·색·인쇄(A4) 서식을 맡는다.
파이썬 표준 라이브러리만 쓴다. 결과 HTML은 외부 글꼴·스크립트·이미지를 부르지 않는다.

  python hanjang.py render 초안.json -o 결과.html     # 만들기 (+ 점검 경고 출력)
  python hanjang.py render - -o 결과.html < 초안.json  # 표준입력
  python hanjang.py check 초안.json                     # 점검만
종료 코드: 0 정상(경고는 있을 수 있음) · 1 초안 형식 오류 · 2 --strict에서 경고 발생
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

VERSION = "0.1.0"
BLOCK_TYPES = ("callout", "kv", "steps", "table", "checklist", "faq", "contact", "note", "text")
PRESETS = ("안내", "절차", "자유")
TONES = ("info", "warn", "ok")
LINK_SCHEMES = ("http://", "https://", "tel:", "mailto:")

# 한 장(A4)에 들어가는 대략의 글자 수 (추정). 2026-10-18 Edge 인쇄 실측: 약 1,250자 1쪽 · 약 1,620자 2쪽.
# 표·단계 카드가 많으면 더 일찍 넘친다 → 보수적으로 잡고, 정확한 값은 --measure(실제 인쇄)로 본다.
ONE_PAGE_CHARS = 1300
LONG_SENTENCE = 60  # 한 문장 글자 수 경고 기준 (휴리스틱, 공공언어 '짧게 쓰기' 취지)
LONG_BLOCK_CHARS = 250  # 이보다 긴 블록은 인쇄 때 쪽을 넘어 이어지게 허용

# 공공언어에서 흔히 쉬운 말로 바꾸라고 권하는 낱말 (제안일 뿐 자동으로 바꾸지 않는다)
EASY_WORDS = {
    "익일": "다음 날", "금일": "오늘", "명일": "내일", "상기": "위", "별첨": "붙임",
    "내방": "방문", "요망": "바람", "제반": "여러", "당해": "해당", "구비서류": "갖출 서류",
    "징구": "받음", "불입": "납부", "시건장치": "잠금장치", "개소": "곳", "유선": "전화",
}


class DraftError(ValueError):
    """초안 형식 오류 — 어디가 잘못됐는지(경로)를 함께 알려 준다."""


# ------------------------------------------------------------------ 검증
def _str(v, where: str, required: bool = True) -> str:
    if v is None or v == "":
        if required:
            raise DraftError(f"{where}: 값이 비어 있습니다")
        return ""
    if not isinstance(v, (str, int, float)):
        raise DraftError(f"{where}: 글자여야 합니다 (현재 {type(v).__name__})")
    return str(v).strip()


def _list(v, where: str) -> list:
    if not isinstance(v, list) or not v:
        raise DraftError(f"{where}: 항목이 1개 이상인 목록이어야 합니다")
    return v


def _url(v, where: str) -> str:
    u = _str(v, where)
    if not u.lower().startswith(LINK_SCHEMES):
        raise DraftError(f"{where}: 링크는 http(s)·tel·mailto만 쓸 수 있습니다 → {u!r}")
    return u


def validate(d) -> dict:
    """초안을 검사하고 정리된 사본을 돌려준다. 형식이 틀리면 DraftError."""
    if not isinstance(d, dict):
        raise DraftError("초안 전체가 JSON 객체({ ... })여야 합니다")
    out = {
        "title": _str(d.get("title"), "title"),
        "subtitle": _str(d.get("subtitle"), "subtitle", required=False),
        "summary": _str(d.get("summary"), "summary", required=False),
        "preset": _str(d.get("preset") or "자유", "preset"),
        "as_of": _str(d.get("as_of"), "as_of", required=False),
        "source": [],
        "blocks": [],
    }
    if out["preset"] not in PRESETS:
        raise DraftError(f"preset: {', '.join(PRESETS)} 중 하나여야 합니다 → {out['preset']!r}")
    if out["as_of"] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", out["as_of"]):
        raise DraftError(f"as_of: 날짜는 YYYY-MM-DD 형식이어야 합니다 → {out['as_of']!r}")
    for i, s in enumerate(d.get("source") or []):
        w = f"source[{i}]"
        if not isinstance(s, dict):
            raise DraftError(f"{w}: {{\"name\": ..., \"url\": ...}} 형태여야 합니다")
        out["source"].append({"name": _str(s.get("name"), f"{w}.name"),
                              "url": _url(s["url"], f"{w}.url") if s.get("url") else ""})
    for i, b in enumerate(_list(d.get("blocks"), "blocks")):
        out["blocks"].append(_validate_block(b, f"blocks[{i}]"))
    return out


def _validate_block(b, w: str) -> dict:
    if not isinstance(b, dict):
        raise DraftError(f"{w}: 블록은 JSON 객체여야 합니다")
    t = b.get("type")
    if t not in BLOCK_TYPES:
        raise DraftError(f"{w}.type: {', '.join(BLOCK_TYPES)} 중 하나여야 합니다 → {t!r}")
    o = {"type": t, "title": _str(b.get("title"), f"{w}.title", required=False)}
    tone = b.get("tone") or ("warn" if t == "note" else "info")
    if tone not in TONES:
        raise DraftError(f"{w}.tone: {', '.join(TONES)} 중 하나여야 합니다 → {tone!r}")
    o["tone"] = tone
    if t in ("callout", "checklist"):
        o["items"] = [_str(x, f"{w}.items[{j}]") for j, x in enumerate(_list(b.get("items"), f"{w}.items"))]
    elif t == "kv":
        rows = []
        for j, r in enumerate(_list(b.get("rows"), f"{w}.rows")):
            if not (isinstance(r, list) and len(r) == 2):
                raise DraftError(f"{w}.rows[{j}]: [\"항목\", \"내용\"] 두 칸이어야 합니다")
            rows.append([_str(r[0], f"{w}.rows[{j}][0]"), _str(r[1], f"{w}.rows[{j}][1]")])
        o["rows"] = rows
    elif t == "steps":
        steps = []
        for j, s in enumerate(_list(b.get("steps"), f"{w}.steps")):
            if isinstance(s, str):
                s = {"title": s}
            if not isinstance(s, dict):
                raise DraftError(f"{w}.steps[{j}]: 글자 또는 {{\"title\": ...}} 이어야 합니다")
            steps.append({k: _str(s.get(k), f"{w}.steps[{j}].{k}", required=(k == "title"))
                          for k in ("title", "detail", "who", "when")})
        o["steps"] = steps
    elif t == "table":
        cols = [_str(c, f"{w}.columns[{j}]") for j, c in enumerate(_list(b.get("columns"), f"{w}.columns"))]
        rows = []
        for j, r in enumerate(_list(b.get("rows"), f"{w}.rows")):
            if not (isinstance(r, list) and len(r) == len(cols)):
                raise DraftError(f"{w}.rows[{j}]: 칸 수가 columns({len(cols)}칸)와 같아야 합니다")
            rows.append([_str(c, f"{w}.rows[{j}][{k}]", required=False) for k, c in enumerate(r)])
        o["columns"], o["rows"] = cols, rows
    elif t == "faq":
        items = []
        for j, q in enumerate(_list(b.get("items"), f"{w}.items")):
            if not isinstance(q, dict):
                raise DraftError(f"{w}.items[{j}]: {{\"q\": ..., \"a\": ...}} 이어야 합니다")
            items.append({"q": _str(q.get("q"), f"{w}.items[{j}].q"), "a": _str(q.get("a"), f"{w}.items[{j}].a")})
        o["items"] = items
    elif t == "contact":
        items = []
        for j, c in enumerate(_list(b.get("items"), f"{w}.items")):
            if not isinstance(c, dict):
                raise DraftError(f"{w}.items[{j}]: {{\"name\": ..., \"phone\": ...}} 이어야 합니다")
            items.append({"name": _str(c.get("name"), f"{w}.items[{j}].name"),
                          "phone": _str(c.get("phone"), f"{w}.items[{j}].phone", required=False),
                          "hours": _str(c.get("hours"), f"{w}.items[{j}].hours", required=False),
                          "url": _url(c["url"], f"{w}.items[{j}].url") if c.get("url") else ""})
        o["items"] = items
    elif t in ("note", "text"):
        o["text"] = _str(b.get("text"), f"{w}.text")
    return o


# ------------------------------------------------------------------ 점검 (경고)
def _texts(d: dict):
    """점검용으로 초안의 모든 문장을 (위치, 글) 로 꺼낸다."""
    yield "summary", d["summary"]
    for i, b in enumerate(d["blocks"]):
        w = f"blocks[{i}]"
        for j, x in enumerate(b.get("items", [])):
            if isinstance(x, str):
                yield f"{w}.items[{j}]", x
            elif isinstance(x, dict):
                for k in ("q", "a"):
                    if k in x:
                        yield f"{w}.items[{j}].{k}", x[k]
        for j, r in enumerate(b.get("rows", [])):
            yield f"{w}.rows[{j}]", " ".join(r)
        for j, s in enumerate(b.get("steps", [])):
            yield f"{w}.steps[{j}]", s["title"] + " " + s["detail"]
        if b.get("text"):
            yield f"{w}.text", b["text"]


def lint(d: dict, today: date | None = None) -> list[str]:
    today = today or date.today()
    warns = []
    types = [b["type"] for b in d["blocks"]]
    if d["preset"] == "안내":
        if not d["as_of"]:
            warns.append("기준일(as_of)이 없습니다 — 금액·자격 같은 내용은 바뀌므로 언제 기준인지 꼭 적으세요")
        if not d["source"]:
            warns.append("출처(source)가 없습니다 — 원문 공지·법령 링크를 적어 사실 확인이 가능하게 하세요")
        if "contact" not in types:
            warns.append("문의(contact) 블록이 없습니다 — 안내문에는 물어볼 곳이 있어야 합니다")
    if d["preset"] == "절차" and "steps" not in types:
        warns.append("절차(steps) 블록이 없습니다")
    if d["as_of"]:
        age = (today - date.fromisoformat(d["as_of"])).days
        if age > 365:
            warns.append(f"기준일이 {age}일 전입니다 — 내용이 바뀌었는지 원문을 다시 확인하세요")
        elif age < 0:
            warns.append("기준일이 미래 날짜입니다")
    total = len(d["title"]) + len(d["summary"])
    for where, t in _texts(d):
        total += len(t)
        for word, easy in EASY_WORDS.items():
            if word in t:
                warns.append(f"{where}: '{word}' → '{easy}' (쉬운 말 제안)")
        for s in re.split(r"(?<=[.!?。])\s+|\n", t):
            if len(s.strip()) > LONG_SENTENCE:
                warns.append(f"{where}: 문장이 {len(s.strip())}자입니다 — {LONG_SENTENCE}자 안쪽으로 나누면 읽기 쉽습니다")
    if total > ONE_PAGE_CHARS:
        warns.append(f"글자가 약 {total}자입니다 — A4 한 장(약 {ONE_PAGE_CHARS}자, 추정)을 넘을 수 있습니다. "
                     "정확한 쪽수는 --measure로 확인하세요")
    return warns


# ------------------------------------------------------------------ 실제 인쇄 쪽수 (선택)
_BROWSER_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
_PAGE_RE = re.compile(rb"/Type\s*/Page(?![a-zA-Z])")  # Chromium(Skia) PDF의 쪽 객체 (pypdf 결과와 대조 확인)


def find_browser() -> str | None:
    env = os.environ.get("HANJANG_BROWSER")
    if env:
        return env if Path(env).exists() else None
    for p in _BROWSER_PATHS:
        if Path(p).exists():
            return p
    for name in ("msedge", "google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        w = shutil.which(name)
        if w:
            return w
    return None


def measure_pages(html_text: str, browser: str | None = None, wait_s: float = 30) -> int | None:
    """설치된 Edge/Chrome으로 A4 PDF를 실제로 인쇄해 쪽수를 센다. 브라우저가 없거나 실패하면 None.
    인쇄는 이 PC 안에서만 일어나고, 결과 HTML에는 외부 자원이 없어 네트워크를 쓰지 않는다."""
    browser = browser or find_browser()
    if not browser:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        src, pdf = Path(tmp) / "page.html", Path(tmp) / "page.pdf"
        src.write_text(html_text, encoding="utf-8")
        try:
            subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", src.as_uri()], capture_output=True, timeout=wait_s + 30)
        except (OSError, subprocess.TimeoutExpired):
            return None
        deadline = time.time() + wait_s  # Windows Edge 실행기는 PDF를 다 쓰기 전에 끝나므로 파일을 기다린다
        last = -1
        while time.time() < deadline:
            if pdf.exists():
                size = pdf.stat().st_size
                if size > 0 and size == last:  # 크기가 두 번 연속 같으면 다 쓴 것으로 본다
                    break
                last = size
            time.sleep(0.5)
        if not pdf.exists() or pdf.stat().st_size == 0:
            return None
        n = len(_PAGE_RE.findall(pdf.read_bytes()))
        return n or None


# ------------------------------------------------------------------ 그리기
def e(s: str) -> str:
    return html.escape(s, quote=True).replace("\n", "<br>")


def _block_html(b: dict) -> str:
    t = b["type"]
    head = f"<h2>{e(b['title'])}</h2>" if b["title"] else ""
    if t == "callout":
        body = "<ul>" + "".join(f"<li>{e(x)}</li>" for x in b["items"]) + "</ul>"
    elif t == "checklist":
        body = '<ul class="check">' + "".join(f"<li>{e(x)}</li>" for x in b["items"]) + "</ul>"
    elif t == "kv":
        body = "<dl>" + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in b["rows"]) + "</dl>"
    elif t == "steps":
        lis = []
        for s in b["steps"]:
            meta = " · ".join(x for x in (s["who"], s["when"]) if x)
            lis.append(f"<li><b>{e(s['title'])}</b>"
                       + (f'<span class="meta">{e(meta)}</span>' if meta else "")
                       + (f"<p>{e(s['detail'])}</p>" if s["detail"] else "") + "</li>")
        body = '<ol class="steps">' + "".join(lis) + "</ol>"
    elif t == "table":
        body = ("<table><thead><tr>" + "".join(f'<th scope="col">{e(c)}</th>' for c in b["columns"])
                + "</tr></thead><tbody>"
                + "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in b["rows"])
                + "</tbody></table>")
    elif t == "faq":
        body = "".join(f'<p class="q">Q. {e(x["q"])}</p><p class="a">{e(x["a"])}</p>' for x in b["items"])
    elif t == "contact":
        rows = []
        for c in b["items"]:
            phone = f'<a href="tel:{e(re.sub(r"[^0-9+]", "", c["phone"]))}">{e(c["phone"])}</a>' if c["phone"] else ""
            link = f' · <a href="{e(c["url"])}">바로가기</a>' if c["url"] else ""
            hours = f' <span class="meta">{e(c["hours"])}</span>' if c["hours"] else ""
            rows.append(f"<li><b>{e(c['name'])}</b> {phone}{hours}{link}</li>")
        body = '<ul class="contact">' + "".join(rows) + "</ul>"
    else:  # note, text
        body = f"<p>{e(b['text'])}</p>"
    wide = " wide" if t in ("steps", "table") else ""
    # 긴 블록은 인쇄 때 쪽·단을 넘어 이어지게 한다 (안 그러면 통째로 다음 쪽으로 밀려 빈 공간이 생김)
    long = " long" if _block_chars(b) > LONG_BLOCK_CHARS else ""
    # 블록 종류 클래스는 b- 접두사: 안쪽 목록 클래스(.steps·.contact)와 이름이 겹치면 블록 전체에 목록 CSS가 먹는다
    return f'<section class="block b-{t} tone-{b["tone"]}{wide}{long}">{head}{body}</section>'


def _block_chars(b: dict) -> int:
    n = len(b["title"]) + len(b.get("text", ""))
    for x in b.get("items", []):
        n += len(x) if isinstance(x, str) else sum(len(v) for v in x.values())
    n += sum(len(c) for r in b.get("rows", []) for c in r) + sum(len(c) for c in b.get("columns", []))
    n += sum(len(v) for s in b.get("steps", []) for v in s.values())
    return n


CSS = """
:root{--ink:#1c2230;--muted:#5b6475;--line:#dde2ea;--bg:#fff;--card:#f7f9fc;--navy:#1f3a8a;
--info:#1f3a8a;--warn:#b54708;--ok:#067647;--warnbg:#fffaeb;--okbg:#ecfdf3;--infobg:#eef3ff}
@media (prefers-color-scheme:dark){:root{--ink:#e6e9ef;--muted:#a3abba;--line:#343b48;--bg:#14171d;
--card:#1c2029;--navy:#8fb0ff;--info:#8fb0ff;--warn:#f5b45f;--ok:#6ad49b;--warnbg:#2b2213;--okbg:#14261c;--infobg:#18213a}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 "Pretendard","Noto Sans KR","Malgun Gothic","Apple SD Gothic Neo",sans-serif;word-break:keep-all;overflow-wrap:anywhere}
main{max-width:980px;margin:0 auto;padding:28px 20px 40px}
header{border-bottom:3px solid var(--navy);padding-bottom:12px;margin-bottom:16px}
h1{margin:0;font-size:26px;line-height:1.3}.sub{color:var(--muted);margin-top:4px}
.summary{margin:12px 0 0;padding:10px 14px;border-left:4px solid var(--navy);background:var(--infobg);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.block{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;break-inside:avoid}
.block.wide{grid-column:1/-1}
h2{margin:0 0 6px;font-size:16px;color:var(--navy)}
ul,ol{margin:0;padding-left:20px}li{margin:2px 0}p{margin:4px 0}
.tone-warn{background:var(--warnbg);border-color:var(--warn)}.tone-warn h2{color:var(--warn)}
.tone-ok{background:var(--okbg);border-color:var(--ok)}.tone-ok h2{color:var(--ok)}
dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 12px;margin:0}dt{font-weight:700;color:var(--muted)}dd{margin:0}
.check{list-style:none;padding-left:0}.check li::before{content:"\\2610  ";color:var(--muted)}
.steps{counter-reset:s;list-style:none;padding-left:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:8px}
.steps li{counter-increment:s;position:relative;padding:8px 10px 8px 40px;background:var(--bg);border:1px solid var(--line);border-radius:8px}
.steps li::before{content:counter(s);position:absolute;left:10px;top:8px;width:22px;height:22px;border-radius:50%;background:var(--navy);color:var(--bg);font-weight:700;text-align:center;line-height:22px;font-size:13px}
.meta{display:block;color:var(--muted);font-size:13px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}th{background:var(--infobg)}
.q{font-weight:700;margin-top:6px}.a{margin-top:0;color:var(--ink)}
.contact{list-style:none;padding-left:0}a{color:var(--navy)}
footer{margin-top:16px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:8px}
@page{size:A4;margin:12mm}
@media print{:root{--bg:#fff;--card:#fff;--ink:#000;--muted:#444;--line:#999;--infobg:#f0f0f0;--warnbg:#fff;--okbg:#fff}
body{font-size:10pt;line-height:1.45}main{max-width:none;padding:0}h1{font-size:17pt}header{margin-bottom:3mm;padding-bottom:2mm}
.summary{margin-top:2mm;padding:2mm 3mm}
/* 인쇄는 신문식 2단 흐름: 격자(행 높이가 맞물림)와 달리 빈칸 없이 채워진다 */
.grid{display:block;column-count:2;column-gap:5mm}
.block{padding:2mm 3mm;border-radius:2mm;margin:0 0 3mm}.block.wide{column-span:all}
.block.long{break-inside:auto}h2{font-size:11pt;margin-bottom:1mm;break-after:avoid}
.steps{grid-template-columns:repeat(auto-fit,minmax(38mm,1fr));gap:2mm}.steps li{padding:1.5mm 2mm 1.5mm 9mm}
.steps li::before{left:2mm;top:1.5mm;width:5mm;height:5mm;line-height:5mm;font-size:8pt}
table{font-size:9pt}th,td{padding:1mm 2mm}footer{margin-top:2mm;padding-top:1mm;font-size:8pt}
a{color:#000;text-decoration:none}}
"""


def render(d: dict) -> str:
    """검증된 초안 → 한 장짜리 HTML 문자열 (외부 자원 없음)."""
    src = " · ".join((f'<a href="{e(s["url"])}">{e(s["name"])}</a>' if s["url"] else e(s["name"])) for s in d["source"])
    foot = []
    if d["as_of"]:
        foot.append(f"기준일 {e(d['as_of'])}")
    if src:
        foot.append(f"출처 {src}")
    foot.append("최신 기준은 출처 원문을 확인하세요")  # 만든 도구 표시는 <meta name="generator">에만 (인쇄물에 군더더기 없게)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="hanjang {VERSION}">
<title>{e(d['title'])}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<header>
<h1>{e(d['title'])}</h1>
{f'<div class="sub">{e(d["subtitle"])}</div>' if d['subtitle'] else ''}
{f'<p class="summary">{e(d["summary"])}</p>' if d['summary'] else ''}
</header>
<div class="grid">
{"".join(_block_html(b) for b in d['blocks'])}
</div>
<footer>{" · ".join(foot)}</footer>
</main>
</body>
</html>
"""


# ------------------------------------------------------------------ CLI
def _load(path: str) -> dict:
    try:
        data = sys.stdin.buffer.read() if path == "-" else Path(path).read_bytes()
    except FileNotFoundError:
        raise DraftError(f"초안 파일이 없습니다: {path}") from None
    # 바이트로 읽어 직접 푼다: 윈도에서 sys.stdin은 cp949로 풀어서 UTF-8 한글이 깨진다 (2026-10-18 실사용에서 발견)
    for enc in ("utf-8-sig", "cp949"):
        try:
            raw = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise DraftError("초안 글자 인코딩을 알 수 없습니다 — UTF-8로 저장하거나 보내세요")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as ex:
        raise DraftError(f"JSON 문법 오류 ({ex.lineno}행 {ex.colno}칸): {ex.msg}") from None


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")  # 콘솔 창: 윈도가 유니코드로 그려 주므로 인코딩은 그대로
            else:
                # 파이프(Claude Code의 Bash 등): 윈도 기본 cp949로 나가면 에이전트가 경고를 못 읽는다 → UTF-8
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(prog="hanjang", description="한국어 안내문·절차를 오프라인 한 장 HTML로")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="초안 JSON → HTML")
    r.add_argument("draft", help="초안 JSON 경로 (- 이면 표준입력)")
    r.add_argument("-o", "--out", help="결과 HTML 경로 (기본: 초안과 같은 이름.html, 표준입력이면 hanjang.html)")
    r.add_argument("--strict", action="store_true", help="경고가 있으면 종료 코드 2")
    r.add_argument("--measure", action="store_true",
                   help="설치된 Edge/Chrome으로 실제 A4 인쇄 쪽수를 센다 (HANJANG_BROWSER로 경로 지정 가능)")
    c = sub.add_parser("check", help="초안 점검만")
    c.add_argument("draft")
    c.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    try:
        d = validate(_load(a.draft))
    except DraftError as ex:
        print(f"[초안 오류] {ex}", file=sys.stderr)
        return 1
    warns = lint(d)
    if a.cmd == "render":
        out = Path(a.out) if a.out else (Path(a.draft).with_suffix(".html") if a.draft != "-" else Path("hanjang.html"))
        out.parent.mkdir(parents=True, exist_ok=True)
        page = render(d)
        out.write_text(page, encoding="utf-8")
        print(f"만듦: {out.resolve()}")
        if a.measure:
            n = measure_pages(page)
            if n is None:
                print("[쪽수] 브라우저(Edge/Chrome)를 찾지 못했거나 인쇄에 실패해 실측하지 못했습니다 — 글자 수 추정만 봅니다")
            else:
                print(f"[쪽수] 실제 A4 인쇄 {n}쪽")
                warns = [w for w in warns if "A4 한 장" not in w]  # 실측이 있으면 추정 경고는 뺀다
                if n > 1:
                    warns.append(f"A4 {n}쪽입니다 — 한 장으로 줄이려면 FAQ·설명 문장을 줄이거나 블록을 나누세요")
    for w in warns:
        print(f"[점검] {w}")
    if not warns:
        print("[점검] 문제 없음")
    return 2 if (a.strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
