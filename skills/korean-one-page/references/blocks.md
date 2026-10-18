# 한 장 안내문 초안 형식

초안은 JSON 객체 하나다. `title`과 `blocks`만 꼭 필요하다.

```json
{
  "title": "제목 (필수)",
  "subtitle": "부제 (선택)",
  "preset": "안내 | 절차 | 자유 (기본 자유)",
  "summary": "한 줄 요약 (선택)",
  "as_of": "YYYY-MM-DD (선택, 안내는 권장)",
  "source": [{"name": "출처 이름", "url": "https://... (선택)"}],
  "blocks": [ ... 아래 블록 ... ]
}
```

모든 블록은 `type`이 있고, `title`(선택)과 `tone`(선택: `info` 기본 · `warn` · `ok`)을 쓸 수 있다.
링크(`url`)는 `http(s)://`, `tel:`, `mailto:`만 된다.

## callout · checklist: 글 목록
```json
{"type": "callout", "title": "한눈에 보기", "items": ["누가: ...", "무엇을: ...", "비용: 무료"]}
{"type": "checklist", "title": "갖출 서류", "items": ["신분증", "통장 사본"]}
```

## kv: 항목과 내용 (두 칸)
```json
{"type": "kv", "title": "받을 수 있는 분", "rows": [["나이", "65세 이상"], ["주소", "○○구 주민"]]}
```

## steps: 순서 (글만 써도 됨)
```json
{"type": "steps", "title": "신청 방법", "steps": [
  {"title": "전화 신청", "detail": "본인이나 가족이 신청", "who": "신청인", "when": "평일 9시~18시"},
  "상담 전화"
]}
```

## table: 표 (모든 행의 칸 수 = columns 칸 수)
```json
{"type": "table", "title": "주제별 담당", "columns": ["주제", "담당"], "rows": [["주거", "복지팀"], ["일자리", "상담창구"]]}
```

## faq: 묻고 답하기
```json
{"type": "faq", "title": "자주 묻는 질문", "items": [{"q": "가족이 신청해도 되나요?", "a": "네, 본인 동의가 있으면 됩니다."}]}
```

## contact: 문의처
```json
{"type": "contact", "title": "문의", "items": [{"name": "복지정책과", "phone": "02-000-0000", "hours": "평일 9시~18시", "url": "https://..."}]}
```

## note · text: 한 덩어리 글
```json
{"type": "note", "title": "꼭 알아 두세요", "text": "...", "tone": "warn"}
{"type": "text", "title": "배경", "text": "..."}
```
`note`의 기본 `tone`은 `warn`이다.
