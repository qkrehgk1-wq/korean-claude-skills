# 변경 이력

## 1.3.0 — 2026-10-18

### 추가
- **🗒️ 한 장 안내문 (`korean-one-page`) — 7번째 스킬.** 한국어 안내문·제도 설명·업무 절차를 인쇄용 **A4 한 장 HTML**로 만듭니다.
  - 모델은 JSON 초안만 쓰고, 번들된 `scripts/hanjang.py`(파이썬 3.10+, 표준 라이브러리만)가 배치·인쇄 서식을 맡습니다.
  - 결과 HTML은 외부 글꼴·스크립트·이미지를 부르지 않아 인터넷 없이 열립니다.
  - 점검: 안내문 양식은 기준일·출처·문의처가 없으면 경고하고, 쉬운 말(예: 익일→다음 날)을 제안하며, 60자 넘는 문장과 1년 지난 기준일도 알려 줍니다.
  - `--measure`: 설치된 Edge/Chrome으로 실제 A4 인쇄 쪽수를 셉니다. 없으면 글자 수 추정(약 1,300자)만 합니다.
  - 이 저장소의 첫 **스크립트 포함 스킬**이라 Claude Code(플러그인·폴더 복사)에서만 동작합니다.
- `tests/` 자동 시험 22개와 CI 실행 단계.

### 검증 결과 (Windows 11, Claude Code 2.1.227, Python 3.11)
| 항목 | 결과 |
|---|---|
| `claude plugin validate .` | 통과 |
| 격리된 설정 폴더에 플러그인 설치 → 스킬 인식 | 7/7 |
| 설치된 플러그인 위치에서 스크립트 실행 | 예시 안내문 A4 1쪽, 점검 경고 0 |
| 자동 시험 | 22개 통과 (인쇄 시험 끈 모드: 20개 통과·2개 건너뜀) |
| 실제 인쇄 쪽수 (Edge headless) | 예시 2종 모두 1쪽. 약 1,250자 1쪽 / 약 1,620자 2쪽 |
| Claude Code 대화에서 스킬 실행 | 가상 안내문 → A4 1쪽 HTML |
| 새 대화에서 평범한 요청만으로 자동 발동되는지 | **미확인** (다음 릴리스에서 확인) |

인쇄 쪽수는 Windows Edge에서만 확인했습니다. macOS·Linux Chrome에서는 글꼴에 따라 달라질 수 있습니다.

## 1.2.0 — 2026-09-17

### 추가
- **Claude Code 플러그인 설치 지원.** `.claude-plugin/marketplace.json`·`plugin.json` 추가. 두 줄로 6종 설치:
  `/plugin marketplace add qkrehgk1-wq/korean-claude-skills` → `/plugin install korean-claude-skills@korean-claude-skills`
  스킬 파일 위치(`skills/`)는 그대로라 기존 폴더 복사 설치도 계속 됩니다.
- README에 실제 실행 결과와 검증 방법 공개.

### 수정 (버그)
- `docs/INSTALL.md` API 예제가 Windows에서 `UnicodeDecodeError`로 멈추던 문제 — `open()`에 `encoding="utf-8"` 추가. (기본 인코딩 cp949 환경에서 재현 확인)
- 같은 예제가 생각 기능이 켜진 최신 모델 응답에서 `AttributeError`가 나던 문제 — `response.content[0].text` 대신 text 블록을 찾아 읽도록 변경, `max_tokens` 1500 → 16000. (SDK 0.97.0 응답 타입으로 재현 확인)

### 변경
- 저장소 이름 오타 수정: `korean-cloude-skills` → `korean-claude-skills` (옛 주소는 새 주소로 자동 연결)
- 설명의 스킬 개수를 6종으로 통일
- 근거를 공개할 수 없는 자체 품질 점수 배지·채점표 제거, 통과/실패 방식의 검증 기록으로 대체
- 출시되지 않은 유료 요금표 제거
- 라이선스 안내를 MIT 조건과 일치하게 수정

### 제거
- 운영용 내부 문서(`COMMANDER-ACTIONS.md`, `landing/`, `docs/30-DAY-PLAN.md`) — 사용자에게 필요 없는 파일

### 검증 결과 (Claude Code 2.1.227)
| 항목 | 결과 |
|---|---|
| `claude plugin validate .` | 통과 |
| 격리된 설정 폴더에 플러그인 설치 → 스킬 인식 | 6/6 |
| 스킬별 실제 실행 → 고유 출력 형식 확인 | 6/6 (13~26초) |
| 대조: 스킬 없이 같은 입력(글 윤문기) → 고유 형식 미출현 | 확인 |
| 스킬 설치 비용(`claude plugin details`) | 상시 약 390토큰, 실행 시 350~600토큰 |

## 1.1.0
- 글 윤문기(`korean-writing-refiner`) 추가 — 6종

## 1.0.0
- 보고서 요약기·카드뉴스 생성기·회의록 정리기·이메일 작성기·코드리뷰 한글화 5종 공개
