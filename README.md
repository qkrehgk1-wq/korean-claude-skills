<!-- 검색 키워드: Claude 한국어, 클로드 스킬, Claude Skill 한국어, Claude Code 플러그인, 한국어 AI 문서 자동화, 보고서 요약 AI, 회의록 자동화, 이메일 자동 작성, 카드뉴스 생성, 코드리뷰 한글화, 글 윤문, 안내문 한 장, A4 한 장 HTML -->

<div align="center">

# 🇰🇷 Korean Claude Skills

### 매일 쓰는 한국어 문서, Claude에게 형식까지 맞춰 맡기는 법
**보고서·회의록·이메일·카드뉴스·코드리뷰·글 윤문·한 장 안내문 — 한국 직장인용 Claude 스킬 7종 (무료·오픈소스)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/스킬-7종-blue)](https://github.com/qkrehgk1-wq/korean-claude-skills)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-플러그인%20설치-8A63D2)](#방법-1-claude-code-플러그인-추천-)
[![Version](https://img.shields.io/badge/버전-1.3.0-lightgrey)](CHANGELOG.md)

</div>

---

## ⚡ 이 저장소가 필요한 사람

> "보고서 한 장 쓰는 데 1시간 넘게 걸린다."
> "회의 끝나고 회의록 정리하다 퇴근이 늦어진다."
> "Claude 써보고 싶은데, 한국어로 제대로 쓰는 법을 모르겠다."

**Korean Claude Skills**는 한국어 직장 문서 작업에 맞춘 Claude 스킬 7종을 **무료**로 제공합니다.

- 🎯 **대상**: 매일 한국어 문서 작업을 하는 직장인·마케터·1인 사업가
- 🔓 **라이선스**: MIT (무료 오픈소스, 상업적 사용 가능)

---

## 🗂️ 스킬 7종 한눈에 보기

| # | 스킬 | 한 줄 설명 |
|---|------|------------|
| 1 | 📄 [**보고서 요약기**](skills/korean-report-summarizer/) | 긴 보고서·기사 → 3줄 요약 + 액션 아이템 5개 + 소셜카드 한 줄 |
| 2 | 🃏 [**카드뉴스 생성기**](skills/korean-cardnews-generator/) | 주제·키워드·긴 글 → 인스타 카드뉴스 7~9장 구성안 |
| 3 | 📝 [**회의록 정리기**](skills/korean-meeting-notes/) | 날것의 메모·녹취 → 결정사항·액션(담당·기한)·미결 |
| 4 | ✉️ [**이메일 작성기**](skills/korean-email-writer/) | 상황·톤 지정 → 격식별 비즈니스 한국어 이메일 + 보내기 전 체크 |
| 5 | 💻 [**코드리뷰 한글화**](skills/korean-code-review/) | 코드·diff → 버그·보안·개선 한국어 리뷰 |
| 6 | ✍️ [**글 윤문기**](skills/korean-writing-refiner/) | 거친 한국어 글 → 자연스럽게 + 무엇을 왜 고쳤는지 코칭 |
| 7 | 🗒️ [**한 장 안내문**](skills/korean-one-page/) | 안내문·절차 → 인쇄용 A4 한 장 HTML + 쉬운 말·기준일·실제 인쇄 쪽수 점검 (파이썬 필요) |

---

## 🚀 설치 — 4가지 방법

### 방법 1. Claude Code 플러그인 (추천) ⭐

Claude Code 대화창에 두 줄을 입력하면 7종이 한 번에 설치됩니다.

```
/plugin marketplace add qkrehgk1-wq/korean-claude-skills
/plugin install korean-claude-skills@korean-claude-skills
```

설치 후에는 **"이 보고서 요약해줘"**처럼 평소대로 말하면 알맞은 스킬이 자동으로 쓰입니다. 직접 부르려면 `/korean-claude-skills:korean-report-summarizer`처럼 입력합니다. 새 버전이 나오면 `/plugin` 메뉴에서 업데이트할 수 있습니다.

> 설치해 두는 것만으로 대화마다 약 480토큰(스킬 목록 설명)이 쓰이고, 스킬이 실제로 실행될 때 370~600토큰이 더 쓰입니다. (`claude plugin details` 기준 추정치, v1.3.0 7종)

### 방법 2. 스킬 폴더 복사 (원하는 것만)

```bash
git clone https://github.com/qkrehgk1-wq/korean-claude-skills.git
# (Windows PowerShell)
Copy-Item -Recurse korean-claude-skills\skills\korean-report-summarizer "$env:USERPROFILE\.claude\skills\"
# (macOS / Linux)
cp -r korean-claude-skills/skills/korean-report-summarizer ~/.claude/skills/
```

### 방법 3. Claude.ai / Claude 앱 (복붙)
1. `skills/korean-report-summarizer/SKILL.md`를 엽니다
2. 두 번째 `---` 아래 본문 전체를 복사합니다
3. Claude 대화창 맨 앞에 붙여넣고, 그 뒤에 처리할 문서를 붙입니다

### 방법 4. API / 코드 통합
`SKILL.md` 본문을 `system` 프롬프트로 넣어 자동화에 연결합니다. 예제는 [docs/INSTALL.md](docs/INSTALL.md).

> 💡 이 스킬은 Claude를 더 잘 쓰게 해 주는 "지침"입니다. Claude(무료/Pro/API) 자체는 별도로 필요합니다.
>
> 🗒️ **한 장 안내문**만은 HTML을 만드는 파이썬 스크립트(3.10 이상, 추가 설치 없음)를 함께 씁니다. 그래서 **방법 1·2(Claude Code)**에서만 동작하고, 방법 3·4처럼 본문만 복사해서는 쓸 수 없습니다.

---

## 🔍 일반 프롬프트와 무엇이 다른가요?

같은 문장을 넣어도 스킬이 있으면 **정해진 형식**으로 답합니다. 아래는 v1.2.0 검증 때 글 윤문기에 같은 입력을 넣은 실제 결과입니다.

**입력**
> 저희 회사는 고객님들의 만족을 위해서 최선의 노력을 다하고 있는 중에 있으며 앞으로도 더욱더 노력을 하도록 하겠습니다.

<table>
<tr><th>스킬 없이</th><th>글 윤문기 스킬 사용</th></tr>
<tr valign="top"><td>

"저희 회사는 고객 만족을 위해 최선을 다하고 있으며, 앞으로도 더 나은 서비스를 위해 노력하겠습니다."

간결하게 다듬었고, 중복 표현을 정리했습니다.

</td><td>

✍️ **다듬은 글**
저희 회사는 고객님의 만족을 위해 최선을 다하고 있으며, 앞으로도 더욱 노력하겠습니다.

🔍 **주요 수정**
- `최선의 노력을 다하고 있는 중에 있으며 → 최선을 다하고 있으며` **[군더더기]** 진행형을 이중으로 겹쳐 쓴 표현
- `더욱더 노력을 하도록 하겠습니다 → 더욱 노력하겠습니다` **[번역투]** 돌려 말하는 번역투

💡 **한 줄 코칭**
한 번이면 될 말을 두 번 겹쳐 쓰는 버릇이 보여요.

</td></tr>
</table>

<sub>※ 출력은 실행마다 조금씩 달라질 수 있습니다. 위 결과는 일부를 줄여 실었습니다.</sub>

---

## 💡 실제 사용 예시 — 보고서 요약기

**입력**
> 이번 주 신규 가입자는 전주 대비 12% 증가한 3,400명이었으나 결제 전환율은 2.1%로 목표 3%에 미달했다. 결제 페이지 평균 로딩이 4.2초로 이탈의 주원인으로 보인다. 마케팅팀은 다음 달 프로모션 예산 1,200만 원을 요청했고, 개발팀은 결제 모듈 교체에 3주가 필요하다고 보고했다.

**출력** (v1.2.0 검증 실행 결과)
```
📌 3줄 요약
- 신규 가입자 3,400명 달성 (전주 대비 +12%)
- 결제 전환율 2.1%로 목표 3% 미달, 로딩 4.2초가 주요 이탈 원인
- 마케팅 예산 1,200만 원 요청, 개발팀은 결제 모듈 교체에 3주 소요 보고

✅ 액션 아이템 5개
1. [개발팀] 결제 모듈 교체 착수 — 완료까지 3주 소요 (보고 기준)
2. [개발팀] 결제 페이지 로딩 속도 4.2초 → 목표치로 단축 (제안: 2초대)
3. [마케팅팀] 다음 달 프로모션 예산 1,200만 원 집행 승인 요청
4. [PM] 결제 모듈 교체(3주) 일정과 프로모션 집행 시점 조율 (제안)
5. [데이터팀] 전환율 2.1% 이탈 구간 상세 분석 후 모듈 교체 우선순위에 반영 (제안)

🔗 소셜카드 한 줄
신규 가입 +12%, 이제 결제 전환율 3% 돌파가 다음 미션 🚀
```

---

## ✅ 어떻게 검증했나요?

릴리스마다 아래를 실제로 실행합니다. 점수를 매기는 대신 **통과/실패**로만 적습니다.

- `claude plugin validate .` — 마켓플레이스·플러그인 설정 파일 검사
- 별도 설정 폴더에 플러그인을 실제 설치해 스킬이 모두 인식되는지 확인
- 스킬을 실제 업무 문장으로 한 번씩 실행해, 각 스킬만 내는 출력 형식(예: 회의록의 "미결", 이메일의 "보내기 전 체크")이 나오는지 확인
- 같은 입력을 스킬 없이 넣었을 때는 그 형식이 나오지 않는지 대조 확인

각 버전 결과는 [CHANGELOG.md](CHANGELOG.md)에 있습니다.

---

## 🗺️ 로드맵

- [x] v1.0 스킬 5종 배포
- [x] v1.1 글 윤문기 추가 (6종)
- [x] v1.2 Claude Code 플러그인 설치 지원, 실행 검증 공개
- [x] v1.3 한 장 안내문 추가 (7종) — 첫 스크립트 포함 스킬, 자동 시험 22개
- [ ] 각 스킬 `examples/` 실제 입출력 샘플 추가
- [ ] 영문 README

---

## 🤝 기여

- 🐛 어색한 출력·오류는 [이슈](https://github.com/qkrehgk1-wq/korean-claude-skills/issues)로 알려 주세요. 입력 문장과 기대한 결과를 함께 적어 주시면 가장 빨리 고칠 수 있습니다.
- 💬 실제 사용 후기와 새 직무 스킬 아이디어도 환영합니다.
- ⭐ 도움이 됐다면 Star로 알려 주세요.

---

## 📄 라이선스

MIT License — 개인·상업적 사용, 수정, 재배포 모두 자유롭습니다. 자세한 조건은 [LICENSE](LICENSE)를 참고하세요.
