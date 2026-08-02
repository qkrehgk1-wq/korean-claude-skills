# 📥 설치 & 사용 가이드

> 한국어 Claude Skills를 Claude Code / Claude Desktop / Claude.ai 에서 사용하는 방법.

---

## 방법 1 — Claude Code (가장 쉬움)

Claude Code의 Skill 디렉토리에 복사하면 자동 인식됩니다.

```bash
# 저장소 클론
git clone https://github.com/qkrehgk1-wq/korean-cloude-skills.git

# 원하는 Skill을 Claude Code skills 폴더로 복사
# (macOS/Linux)
cp -r korean-cloude-skills/skills/korean-report-summarizer ~/.claude/skills/
# (Windows PowerShell)
Copy-Item -Recurse korean-cloude-skills\skills\korean-report-summarizer "$env:USERPROFILE\.claude\skills\"
```

이제 Claude Code에서 "이 보고서 요약해줘" 라고 하면 Skill이 자동 발동합니다.

---

## 방법 2 — Claude.ai / Claude Desktop (복붙)

Skill 파일이 필요 없습니다. SKILL.md의 본문을 프롬프트로 붙여넣으세요.

1. `skills/korean-report-summarizer/SKILL.md` 열기
2. `---` 아래 본문 전체 복사
3. Claude 대화창 맨 앞에 붙여넣고, 그 뒤에 처리할 문서를 붙임

```
[SKILL.md 본문 붙여넣기]

=== 처리할 문서 ===
(여기에 보고서/회의록/등 붙여넣기)
```

---

## 방법 3 — API / 코드 통합

```python
import anthropic

client = anthropic.Anthropic()

# SKILL.md 본문을 system 으로
with open("skills/korean-report-summarizer/SKILL.md") as f:
    skill = f.read().split("---", 2)[-1]  # frontmatter 제거

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1500,
    system="다음 Skill 지침을 따르는 한국어 전문가입니다.\n" + skill,
    messages=[{"role": "user", "content": "여기에 보고서 내용"}],
)
print(response.content[0].text)
```

---

## 🆓 무료 vs 💎 프리미엄

| | 무료 (이 저장소) | 프리미엄 (월 $9) |
|---|---|---|
| Skill 수 | 5종 | 20종+ |
| 업데이트 | 커뮤니티 | 매주 신규 |
| 산업 특화 템플릿 | ❌ | ✅ (제안서·IR·KPI) |
| 우선 지원 | ❌ | ✅ |

프리미엄: (Gumroad 링크 — 출시 후 추가)

---

## ❓ 자주 묻는 질문

**Q. Claude 구독이 따로 필요한가요?**
네. 이 Skill은 Claude를 더 잘 쓰게 해주는 "지침"입니다. Claude(무료/Pro/API) 자체는 별도입니다.

**Q. 한국어만 되나요?**
한국 비즈니스 맥락에 최적화돼 있습니다. 영어 입력도 처리하지만 출력은 한국어 기본입니다.

**Q. 회사 기밀 문서를 넣어도 되나요?**
Claude의 데이터 정책을 따릅니다. 민감 정보는 각 Skill이 `[민감]` 처리를 제안하지만, 최종 판단은 사용자 책임입니다.
