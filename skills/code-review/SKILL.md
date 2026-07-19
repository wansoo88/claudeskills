---
name: code-review
description: 3단계 구현에서 커밋 전 '무조건' 실행하는 필수 코드리뷰. 변경 코드를 정확성·가독성·설계·테스트·성능으로 점검하고, code-review-log.md와 .review-state.json에 pass/fail을 기록한다. code-reviewer 서브에이전트를 이름으로 호출해 수행.
---

# 코드리뷰 (3단계 필수 게이트)

목표: 커밋 전에 코드 품질을 **객관적 기준**으로 판정하고 원장에 남긴다. 이 게이트를 통과해야 hook이 커밋을 허용한다.

## 진행 순서

### 1. 변경 범위 파악
`git diff`(또는 변경 파일)로 리뷰 대상을 정한다. 관련 설계(`docs/02-design/`)도 참조.

### 2. code-reviewer 호출
`code-reviewer` 서브에이전트를 **이름으로 명시 호출**한다(자동위임 의존 금지). 리뷰어에게 `reference/code-review-checklist-ko.md` 기준으로 검토를 지시.

### 3. 판정 기록 (게이트 핵심)
리뷰 결과를 반영해 다음을 보장:
- `docs/03-build/code-review-log.md` — 발견사항·심각도·수정제안.
- `docs/03-build/.review-state.json` — `code_review.status`를 `passed`/`failed`로. 예:
  ```json
  {"code_review": {"status": "passed", "at": "2026-07-19T18:00:00", "notes": "핵심 로직 테스트 확인"}}
  ```
  (security_review 항목은 유지·병합.)

### 4. 결과 안내
- **passed**: 다음으로 security-review 필요함을 알림(둘 다 passed여야 커밋 가능).
- **failed**: 무엇을 고쳐야 하는지 요약하고, 수정 후 재리뷰.

## 하지 말 것
- 형식적 통과. fail 근거 없이 pass 기록. 소스 임의 수정(리뷰어는 판정만).
