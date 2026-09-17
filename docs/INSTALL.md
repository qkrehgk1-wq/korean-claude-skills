# 📥 설치 & 사용 가이드

> 한국어 Claude 스킬을 Claude Code / Claude.ai / API에서 사용하는 방법.

---

## 방법 1 — Claude Code 플러그인 (추천)

Claude Code 대화창에 입력합니다.

```
/plugin marketplace add qkrehgk1-wq/korean-claude-skills
/plugin install korean-claude-skills@korean-claude-skills
```

- 6종이 한 번에 설치되고, 평소처럼 "이 보고서 요약해줘"라고 말하면 알맞은 스킬이 자동으로 쓰입니다.
- 직접 부를 때: `/korean-claude-skills:korean-report-summarizer`
- 업데이트: `/plugin` 메뉴에서 이 플러그인을 선택해 업데이트합니다.
- 삭제: `/plugin uninstall korean-claude-skills@korean-claude-skills`

터미널에서 설치해도 됩니다.

```bash
claude plugin marketplace add qkrehgk1-wq/korean-claude-skills
claude plugin install korean-claude-skills@korean-claude-skills
```

---

## 방법 2 — 스킬 폴더 복사 (원하는 것만)

```bash
git clone https://github.com/qkrehgk1-wq/korean-claude-skills.git

# (macOS / Linux)
cp -r korean-claude-skills/skills/korean-report-summarizer ~/.claude/skills/
# (Windows PowerShell)
Copy-Item -Recurse korean-claude-skills\skills\korean-report-summarizer "$env:USERPROFILE\.claude\skills\"
```

> 방법 1과 방법 2로 같은 스킬을 둘 다 설치하면 목록에 두 번 보입니다. 한 가지만 쓰세요.

---

## 방법 3 — Claude.ai / Claude 앱 (복붙)

1. `skills/korean-report-summarizer/SKILL.md` 열기
2. 두 번째 `---` 아래 본문 전체 복사
3. Claude 대화창 맨 앞에 붙여넣고, 그 뒤에 처리할 문서를 붙임

```
[SKILL.md 본문 붙여넣기]

=== 처리할 문서 ===
(여기에 보고서/회의록 등 붙여넣기)
```

---

## 방법 4 — API / 코드 통합 (Python)

```bash
pip install anthropic
```

```python
import anthropic

client = anthropic.Anthropic()  # 환경변수 ANTHROPIC_API_KEY 사용

# SKILL.md 본문을 system 프롬프트로 사용.
# encoding="utf-8" 필수 — 빼면 Windows에서 한글 파일을 cp949로 읽다가 UnicodeDecodeError가 납니다.
with open("skills/korean-report-summarizer/SKILL.md", encoding="utf-8") as f:
    skill = f.read().split("---", 2)[2]  # 맨 앞 설정(frontmatter) 제거

response = client.messages.create(
    model="claude-opus-5",   # 필요하면 다른 모델로 바꾸세요
    max_tokens=16000,        # 최신 모델은 답하기 전에 생각에도 토큰을 씁니다 — 너무 작으면 답이 잘립니다
    system="다음 스킬 지침을 따르는 한국어 전문가입니다.\n" + skill,
    messages=[{"role": "user", "content": "여기에 보고서 내용"}],
)

# 첫 번째 조각이 '생각' 블록일 수 있으므로 글(text) 조각을 찾아 읽습니다.
# response.content[0].text 로 바로 읽으면 AttributeError가 날 수 있습니다.
print(next(block.text for block in response.content if block.type == "text"))
```

---

## ❓ 자주 묻는 질문

**Q. Claude 구독이 따로 필요한가요?**
네. 이 스킬은 Claude를 더 잘 쓰게 해 주는 "지침"입니다. Claude(무료/Pro/API) 자체는 별도입니다.

**Q. 한국어만 되나요?**
한국 비즈니스 맥락에 맞춰져 있습니다. 영어 입력도 처리하지만 출력은 한국어가 기본입니다.

**Q. 회사 기밀 문서를 넣어도 되나요?**
Claude의 데이터 정책을 따릅니다. 일부 스킬은 민감해 보이는 수치에 `[민감]` 처리를 제안하지만, 최종 판단은 사용자 책임입니다. 회사 보안 규정을 먼저 확인하세요.
