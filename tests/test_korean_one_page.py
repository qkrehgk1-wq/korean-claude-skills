"""korean-one-page(한 장 안내문) 테스트 — 표준 라이브러리 unittest.  실행: python -m unittest discover -s tests -v
실제 인쇄 쪽수 시험은 Edge/Chrome이 있을 때만 돈다. 끄려면 HANJANG_BROWSER=none."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "korean-one-page"
SCRIPT = SKILL / "scripts" / "hanjang.py"
sys.path.insert(0, str(SCRIPT.parent))
import hanjang  # noqa: E402

EXAMPLES = sorted((SKILL / "examples").glob("*.json"))


def draft(**kw):
    d = {"title": "제목", "blocks": [{"type": "text", "text": "본문"}]}
    d.update(kw)
    return d


class Validate(unittest.TestCase):
    def test_examples_are_valid_and_clean(self):
        self.assertTrue(EXAMPLES)
        for p in EXAMPLES:
            d = hanjang.validate(json.loads(p.read_text(encoding="utf-8")))
            self.assertEqual(hanjang.lint(d, today=date(2026, 10, 18)), [], p.name)

    def test_errors_point_to_location(self):
        cases = [
            (draft(title=""), "title"),
            (draft(blocks=[]), "blocks"),
            (draft(blocks=[{"type": "text", "text": "a"}, {"type": "chart"}]), "blocks[1].type"),
            (draft(blocks=[{"type": "table", "columns": ["a", "b"], "rows": [["1"]]}]), "blocks[0].rows[0]"),
            (draft(blocks=[{"type": "kv", "rows": [["a"]]}]), "blocks[0].rows[0]"),
            (draft(preset="공지"), "preset"),
            (draft(as_of="2026/10/18"), "as_of"),
            (draft(blocks=[{"type": "note", "text": "a", "tone": "red"}]), "tone"),
        ]
        for d, where in cases:
            with self.assertRaises(hanjang.DraftError) as cm:
                hanjang.validate(d)
            self.assertIn(where, str(cm.exception))

    def test_unsafe_links_rejected(self):
        for bad in ("javascript:alert(1)", "data:text/html,x", "file:///C:/x", "//evil.example"):
            with self.assertRaises(hanjang.DraftError):
                hanjang.validate(draft(source=[{"name": "x", "url": bad}]))
            with self.assertRaises(hanjang.DraftError):
                hanjang.validate(draft(blocks=[{"type": "contact", "items": [{"name": "a", "url": bad}]}]))

    def test_steps_accept_plain_strings(self):
        d = hanjang.validate(draft(blocks=[{"type": "steps", "steps": ["하나", {"title": "둘", "who": "담당"}]}]))
        self.assertEqual([s["title"] for s in d["blocks"][0]["steps"]], ["하나", "둘"])


class Render(unittest.TestCase):
    def render(self, **kw):
        return hanjang.render(hanjang.validate(draft(**kw)))

    def test_escapes_user_text(self):
        out = self.render(title="<script>alert(1)</script>",
                          blocks=[{"type": "faq", "items": [{"q": '"><img src=x onerror=1>', "a": "a&b"}]}])
        self.assertNotIn("<script>alert", out)
        self.assertNotIn("<img src=x", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertIn("a&amp;b", out)

    def test_offline_no_external_resources(self):
        for p in EXAMPLES:
            out = hanjang.render(hanjang.validate(json.loads(p.read_text(encoding="utf-8"))))
            self.assertIsNone(re.search(r"<(script|img|link|iframe)\b", out), p.name)
            self.assertIsNone(re.search(r"@import|url\(", out), p.name)

    def test_block_class_does_not_collide_with_inner_list(self):
        # 회귀(2026-10-18): 블록 클래스 'steps'가 안쪽 목록 CSS(.steps)와 겹쳐 제목과 카드가 옆으로 갈라졌다
        out = self.render(blocks=[{"type": "steps", "steps": ["a"]}, {"type": "contact", "items": [{"name": "b"}]}])
        self.assertNotRegex(out, r'<section class="block (steps|contact)\b')
        self.assertIn('class="block b-steps', out)

    def test_long_blocks_may_break_across_pages(self):
        long_faq = {"type": "faq", "items": [{"q": "질문?", "a": "가" * 40} for _ in range(10)]}
        out = self.render(blocks=[long_faq, {"type": "text", "text": "짧음"}])
        self.assertIn("b-faq tone-info long", out)
        self.assertNotIn("b-text tone-info long", out)

    def test_phone_link_digits_only(self):
        out = self.render(blocks=[{"type": "contact", "items": [{"name": "a", "phone": "02-000-0000 (내선 1)"}]}])
        self.assertIn('href="tel:0200000001"', out)


class Lint(unittest.TestCase):
    def lint(self, today=date(2026, 10, 18), **kw):
        return hanjang.lint(hanjang.validate(draft(**kw)), today=today)

    def test_notice_preset_requires_date_source_contact(self):
        w = " ".join(self.lint(preset="안내"))
        for k in ("기준일", "출처", "문의"):
            self.assertIn(k, w)

    def test_procedure_preset_requires_steps(self):
        self.assertTrue(any("절차" in x for x in self.lint(preset="절차")))

    def test_easy_words_and_long_sentence(self):
        w = self.lint(blocks=[{"type": "text", "text": "익일까지 구비서류를 내세요. " + "가" * 70 + "."}])
        joined = " ".join(w)
        self.assertIn("'익일' → '다음 날'", joined)
        self.assertIn("'구비서류' → '갖출 서류'", joined)
        self.assertIn("문장이", joined)

    def test_stale_and_future_dates(self):
        self.assertTrue(any("일 전" in x for x in self.lint(as_of="2025-01-01")))
        self.assertTrue(any("미래" in x for x in self.lint(as_of="2027-01-01")))
        self.assertFalse(any("일 전" in x for x in self.lint(as_of="2026-06-01")))

    def test_one_page_estimate(self):
        many = {"type": "faq", "items": [{"q": "질문?", "a": "가나다라마 바사아자. " * 6} for _ in range(30)]}
        self.assertTrue(any("A4 한 장" in x for x in self.lint(blocks=[many])))
        self.assertFalse(any("A4 한 장" in x for x in self.lint()))


class Cli(unittest.TestCase):
    def run_cli(self, *args, stdin=None):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin, capture_output=True,
                              text=True, encoding="utf-8", env=env)

    def test_render_from_stdin(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "깊은" / "폴더" / "결과.html"
            r = self.run_cli("render", "-", "-o", str(out), stdin=json.dumps(draft(), ensure_ascii=False))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(out.exists())
            self.assertIn('<html lang="ko">', out.read_text(encoding="utf-8"))

    def test_stdin_utf8_korean_without_pythonioencoding(self):
        # 회귀(2026-10-18): 윈도에서 PYTHONIOENCODING 없이 heredoc으로 넣으면 sys.stdin이 cp949로 풀어 '안내'가 깨졌다
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
        data = json.dumps(draft(preset="안내", title="한글 제목"), ensure_ascii=False).encode("utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "check", "-"], input=data, capture_output=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace") + r.stderr.decode("cp949", "replace"))
        # 회귀(2026-10-18): 파이프로 받는 출력이 cp949라 에이전트가 경고를 못 읽었다 → UTF-8로 나와야 한다
        out = r.stdout.decode("utf-8")
        self.assertIn("[점검]", out)
        # cp949로 저장된 초안 파일도 읽힌다
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "초안.json"
            p.write_bytes(json.dumps(draft(title="한글"), ensure_ascii=False).encode("cp949"))
            r = subprocess.run([sys.executable, str(SCRIPT), "check", str(p)], capture_output=True, env=env)
            self.assertEqual(r.returncode, 0)

    def test_bad_json_exit_1(self):
        r = self.run_cli("check", "-", stdin="{ title: 1 ")
        self.assertEqual(r.returncode, 1)
        self.assertIn("JSON 문법 오류", r.stderr)

    def test_strict_exit_2_on_warnings(self):
        r = self.run_cli("check", "-", "--strict", stdin=json.dumps(draft(preset="안내"), ensure_ascii=False))
        self.assertEqual(r.returncode, 2)
        r = self.run_cli("check", "-", stdin=json.dumps(draft(preset="안내"), ensure_ascii=False))
        self.assertEqual(r.returncode, 0)

    def test_missing_file_message(self):
        r = self.run_cli("check", "없는파일.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("없습니다", r.stderr)


class Measure(unittest.TestCase):
    def test_no_browser_returns_none(self):
        self.assertIsNone(hanjang.measure_pages("<p>x</p>", browser=str(ROOT / "없는브라우저.exe")))

    @unittest.skipUnless(hanjang.find_browser(), "Edge/Chrome 없음")
    def test_examples_print_on_one_a4_page(self):
        for p in EXAMPLES:
            page = hanjang.render(hanjang.validate(json.loads(p.read_text(encoding="utf-8"))))
            self.assertEqual(hanjang.measure_pages(page), 1, p.name)

    @unittest.skipUnless(hanjang.find_browser(), "Edge/Chrome 없음")
    def test_long_draft_measures_more_than_one_page(self):
        many = {"type": "faq", "items": [{"q": f"질문 {i}?", "a": "이 문장은 길이 시험용입니다. " * 4} for i in range(40)]}
        page = hanjang.render(hanjang.validate(draft(blocks=[many])))
        self.assertGreaterEqual(hanjang.measure_pages(page), 2)


if __name__ == "__main__":
    unittest.main()
