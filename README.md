<!-- 검색 키워드: Claude 한국어, 클로드 프롬프트, 한국어 AI 문서 자동화, 보고서 요약 AI, 회의록 자동화, 이메일 자동 작성, 카드뉴스 생성, 코드리뷰 한글화, Claude Skill 한국어 -->

<div align="center">

# 🇰🇷 Korean Claude Skills

### 매일 쓰는 한국어 문서, Claude가 5분 만에 끝내는 법
**보고서·회의록·이메일 하루 3건 → 15분으로 줄인 Claude 스킬 6종 (무료·오픈소스)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Quality Score](https://img.shields.io/badge/AI%20품질검토-8.3%2F10-brightgreen)](https://github.com/qkrehgk1-wq/korean-cloude-skills)
[![Skills](https://img.shields.io/badge/스킬-6종-blue)](https://github.com/qkrehgk1-wq/korean-cloude-skills)
[![Free](https://img.shields.io/badge/무료-오픈소스-orange)](https://github.com/qkrehgk1-wq/korean-cloude-skills)

</div>

---

## ⚡ 이 레포가 필요한 사람

> "보고서 한 장 쓰는 데 1시간 넘게 걸린다."
> "회의 끝나고 회의록 정리하다 퇴근이 늦어진다."
> "Claude 써보고 싶은데, 한국어로 제대로 쓰는 법을 모르겠다."

**Korean Claude Skills**는 한국어 직장 문서 작업에 최적화된 Claude Skill 6종을 **무료**로 제공합니다.

- 🎯 **타깃**: 매일 한국어 문서 작업을 하는 직장인·마케터·1인 사업가
- 🔓 **라이선스**: MIT (무료 오픈소스, 상업적 사용 가능)
- 🏆 **품질**: AI 7차원 품질검토 평균 **8.3/10** 통과 (정확성·유용성·가독성·일관성·안전성·효율성·한국어 자연스러움)

---

## 🗂️ 스킬 6종 한눈에 보기

| # | 스킬 | 한 줄 설명 | 예상 절감 |
|---|------|------------|-----------|
| 1 | 📄 [**보고서 요약기**](skills/korean-report-summarizer/) | 긴 보고서·기사 → 3줄 요약 + 액션 5개 + 소셜카드 문장 | ~40분 → 3분 |
| 2 | 🃏 [**카드뉴스 생성기**](skills/korean-cardnews-generator/) | 주제·키워드·긴 글 → 인스타 카드뉴스 7~9장 구성안 | ~60분 → 5분 |
| 3 | 📝 [**회의록 정리기**](skills/korean-meeting-notes/) | 날것의 메모·녹취 → 결정사항·액션(담당·기한)·미결 | ~30분 → 3분 |
| 4 | ✉️ [**이메일 작성기**](skills/korean-email-writer/) | 상황·톤 지정 → 격식별 비즈니스 한국어 이메일 | ~20분 → 2분 |
| 5 | 💻 [**코드리뷰 한글화**](skills/korean-code-review/) | 코드·diff → 버그·보안·개선 한국어 리뷰 | ~30분 → 2분 |
| 6 | ✍️ [**글 윤문기**](skills/korean-writing-refiner/) | 거친 한국어 글 → 자연스럽고 명확하게 + 무엇을 왜 고쳤는지 코칭 | ~15분 → 1분 |

---

## 🚀 빠른 시작 — 3가지 방법

### 방법 1. Claude Code (가장 쉬움) ⭐
스킬 폴더를 Claude Code의 skills 디렉터리에 복사하면 **자동 인식**됩니다.

```bash
# 저장소 클론
git clone https://github.com/qkrehgk1-wq/korean-cloude-skills.git

# 원하는 스킬을 Claude Code skills 폴더로 복사
# (Windows PowerShell)
Copy-Item -Recurse korean-cloude-skills\skills\korean-report-summarizer "$env:USERPROFILE\.claude\skills\"
# (macOS / Linux)
cp -r korean-cloude-skills/skills/korean-report-summarizer ~/.claude/skills/
```

이제 Claude Code에서 **"이 보고서 요약해줘"** 라고 하면 스킬이 자동 발동합니다.

### 방법 2. Claude.ai / Claude 앱 (복붙)
파일 설치 없이 사용합니다.
1. `skills/korean-report-summarizer/SKILL.md` 를 엽니다
2. `---` 아래 본문 전체를 복사합니다
3. Claude 대화창 맨 앞에 붙여넣고, 그 뒤에 처리할 문서를 붙입니다

### 방법 3. API / 코드 통합
`SKILL.md` 본문을 `system` 프롬프트로 넣어 자동화 파이프라인에 연결합니다. 자세한 예제는 [docs/INSTALL.md](docs/INSTALL.md).

> 💡 **참고:** 이 스킬은 Claude를 더 잘 쓰게 해주는 "지침"입니다. Claude(무료/Pro/API) 자체는 별도로 필요합니다.

---

## 🔍 왜 일반 ChatGPT 프롬프트와 다른가요?

일반적인 영문 프롬프트를 한국어에 그냥 쓰면 이런 문제가 생깁니다:

| 문제 | 일반 영문 프롬프트 | Korean Claude Skills |
|------|-------------------|----------------------|
| 존댓말 레벨 | 제멋대로 섞임 | 상황별 명시적 지정 |
| 문서 구조 | 영미식 포맷 | 한국 직장 관행 반영 |
| 전문 용어 | 영어 혼용 출력 | 한국어 용어 우선 |
| 출력 길이 | 너무 길거나 짧음 | 실무 적정 분량 |
| 재현성 | 매번 달라짐 | 파라미터 고정으로 일관성 |

> 이 스킬 팩은 한국어 문서의 **형식 관행·존댓말 체계·실무 맥락**을 프롬프트 레벨에서 설계했습니다.

---

## 💡 실제 사용 예시 — 보고서 요약기

**입력 (업무 보고서 일부)**
> "이번 주 신규 가입자가 전주 대비 12% 증가한 3,400명을 기록했으나, 결제 전환율은 2.1%로 목표(3%)에 미달했습니다. 원인은 결제 페이지 로딩 속도(평균 4.2초)로 파악되었으며…"

**출력 (스킬 적용)**
```
📌 3줄 요약
- 신규 가입 3,400명 (전주 +12%) 달성
- 결제 전환율 2.1%로 목표 3% 미달 — 로딩 4.2초가 주요 이탈 요인
- 다음 주 결제 페이지 최적화를 최우선 과제로 추진

✅ 액션 아이템
1. [개발팀] 결제 페이지 로딩 4.2초 → 2초 이내 최적화
2. [데이터팀] 전환율 이탈 지점 퍼널 분석
   ...
```

---

## 📊 품질 검증 (AI 7차원 채점)

```
① 정확성 8.5  ② 유용성 8.7  ③ 가독성 8.2  ④ 일관성 8.1
⑤ 안전성 8.6  ⑥ 효율성 8.0  ⑦ 한국어 자연스러움 8.1
──────────────────────────────  평균 8.3 / 10
```
> ※ 자체 평가 기준이며 지속 업데이트됩니다. 이슈·PR로 개선에 참여해 주세요.

---

## 🗺️ 로드맵

- [x] 스킬 5종 v1.0 배포
- [ ] 각 스킬 `examples/` 실제 입출력 샘플 추가
- [ ] 영문 README (글로벌 확장)
- [ ] 직무별 확장팩 (인사·법무·회계) — 프리미엄 예정 🔜

---

## 🤝 기여 & 응원

가장 쉬운 기여는 **⭐ Star** 입니다. Star가 쌓일수록 더 많은 직장인에게 노출됩니다. 🙏
- 🐛 프롬프트 오류·어색한 출력 [이슈 제보](https://github.com/qkrehgk1-wq/korean-cloude-skills/issues)
- 💬 실제 사용 후기·개선 아이디어
- 📝 새로운 직무별 스킬 PR

> 🔔 **Watch → Releases only** 설정 시 새 스킬 출시 알림을 받을 수 있습니다.

---

## 📄 라이선스

MIT License — 개인·상업적 사용 모두 무료. 단, 이 레포를 그대로 재판매하는 행위는 삼가 주세요.

---

<div align="center">

**🇰🇷 한국어 AI 문서 자동화, 같이 만들어 갑시다.**

[⭐ Star](https://github.com/qkrehgk1-wq/korean-cloude-skills) · [🐛 Issue](https://github.com/qkrehgk1-wq/korean-cloude-skills/issues) · [🔀 PR](https://github.com/qkrehgk1-wq/korean-cloude-skills/pulls)

</div>
