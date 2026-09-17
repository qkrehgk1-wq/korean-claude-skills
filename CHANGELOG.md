# 변경 이력

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
