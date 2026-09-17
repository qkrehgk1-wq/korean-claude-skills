"""스킬·플러그인 설정 검사 (표준 라이브러리만 사용).

Claude Code 공식 문서(2026-09 확인) 기준으로, 고쳐도 설치·인식이 깨지지 않는지 본다.
  - SKILL.md 첫 줄이 '---' 여야 설정(frontmatter)을 읽는다. 아니면 파일 전체가 본문 취급된다.
  - description 은 목록에서 1,536자(when_to_use 포함)에서 잘린다.
  - name 을 쓰면 폴더 이름과 같아야 설치 방법(폴더 복사/플러그인)에 상관없이 부르는 이름이 같다.
  - 'synced' 폴더명은 예약어다.
  - 본문 500줄 이하 권장.
  - marketplace.json / plugin.json 필수 항목, 플러그인 버전과 CHANGELOG 최신 버전 일치.

사용: python scripts/validate_skills.py   (문제 있으면 종료 코드 1)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(text: str) -> dict:
    """아주 단순한 'key: value' 한 줄짜리만 읽는다 — 이 저장소 스킬은 그 형식만 쓴다."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def check_skills(errors: list) -> int:
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    for d in skills:
        f = d / "SKILL.md"
        where = f"skills/{d.name}"
        if not f.exists():
            errors.append(f"{where}: SKILL.md 없음")
            continue
        raw = f.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{where}: BOM 이 있어 첫 줄이 '---' 로 인식되지 않음")
        text = raw.decode("utf-8")
        if text.splitlines()[0].strip() != "---":
            errors.append(f"{where}: 첫 줄이 '---' 가 아님 — 설정이 무시되고 본문으로 읽힘")
            continue
        fm = frontmatter(text)
        if fm is None:
            errors.append(f"{where}: 닫는 '---' 없음")
            continue
        if not KEBAB.match(d.name):
            errors.append(f"{where}: 폴더명은 소문자-하이픈 형식이어야 함")
        if d.name.lower() == "synced":
            errors.append(f"{where}: 'synced' 는 예약된 폴더명")
        if fm.get("name") and fm["name"] != d.name:
            errors.append(f"{where}: name '{fm['name']}' ≠ 폴더명 — 설치 방법마다 부르는 이름이 달라짐")
        desc = fm.get("description", "")
        if not desc:
            errors.append(f"{where}: description 없음 — 자동 발동 판단 근거가 없음")
        if len(desc) + len(fm.get("when_to_use", "")) > 1536:
            errors.append(f"{where}: description+when_to_use {len(desc)}자 > 1,536자 — 목록에서 잘림")
        if len(text.splitlines()) > 500:
            errors.append(f"{where}: {len(text.splitlines())}줄 > 권장 500줄")
    return len(skills)


def check_manifests(errors: list, n_skills: int) -> None:
    mp = ROOT / ".claude-plugin" / "marketplace.json"
    pj = ROOT / ".claude-plugin" / "plugin.json"
    try:
        market = json.loads(mp.read_text(encoding="utf-8"))
        plugin = json.loads(pj.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"설정 파일 읽기 실패: {e}")
        return
    for key in ("name", "owner", "plugins"):
        if key not in market:
            errors.append(f"marketplace.json: '{key}' 없음")
    if not (market.get("owner") or {}).get("name"):
        errors.append("marketplace.json: owner.name 없음")
    names = [p.get("name") for p in market.get("plugins", [])]
    if plugin.get("name") not in names:
        errors.append(f"plugin.json name '{plugin.get('name')}' 이 marketplace 목록 {names} 에 없음")
    for p in market.get("plugins", []):
        if not KEBAB.match(p.get("name", "")):
            errors.append(f"marketplace.json: 플러그인 이름 '{p.get('name')}' 은 소문자-하이픈 형식이어야 함")
        if not p.get("source"):
            errors.append(f"marketplace.json: '{p.get('name')}' source 없음")
    version = plugin.get("version", "")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        errors.append(f"plugin.json: version '{version}' 이 x.y.z 형식이 아님 — 사용자 업데이트가 안 됨")
    cl = ROOT / "CHANGELOG.md"
    if cl.exists():
        m = re.search(r"^## (\d+\.\d+\.\d+)", cl.read_text(encoding="utf-8"), re.M)
        if m and m.group(1) != version:
            errors.append(f"CHANGELOG 최신 {m.group(1)} ≠ plugin.json {version} — 버전 올리는 걸 잊음")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"스킬-{n_skills}종" not in readme:
        errors.append(f"README 배지의 스킬 개수가 실제 {n_skills}종과 다름")


def main() -> int:
    errors: list = []
    n = check_skills(errors)
    check_manifests(errors, n)
    if errors:
        print("❌ 검사 실패")
        for e in errors:
            print("  -", e)
        return 1
    print(f"✅ 스킬 {n}종·설정 파일 검사 통과")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
