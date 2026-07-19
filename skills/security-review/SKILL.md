---
name: security-review
description: 3단계 구현에서 커밋 전 '무조건' 실행하는 필수 보안리뷰. 변경 코드를 OWASP/보안 베이스라인과 2단계 보안설계 기준으로 점검하고 security-review-log.md와 .review-state.json에 pass/fail을 기록한다. security-reviewer 서브에이전트를 이름으로 호출해 수행.
---

# 보안리뷰 (3단계 필수 게이트)

목표: 커밋 전에 보안 취약점을 **공격자 관점**으로 점검하고 원장에 판정을 남긴다. code-review와 함께 둘 다 passed여야 hook이 커밋을 허용한다.

## 진행 순서

### 1. 기준 로드
`../security-design/reference/security-baseline-ko.md`(OWASP+AWS)와 `docs/02-design/security.md`의 security-review 체크리스트를 기준으로 삼는다.

### 2. security-reviewer 호출
`security-reviewer` 서브에이전트를 **이름으로 명시 호출**한다. 변경 코드에서 인증/인가·인젝션·비밀노출·암호화·입력검증·취약의존성을 점검하도록 지시.

### 3. 판정 기록 (게이트 핵심)
- `docs/03-build/security-review-log.md` — 취약점(위치·심각도·CWE/OWASP·수정안).
- `docs/03-build/.review-state.json` — `security_review.status`를 `passed`/`failed`로. 예:
  ```json
  {"security_review": {"status": "passed", "at": "2026-07-19T18:05:00", "notes": "인젝션·비밀노출 없음"}}
  ```
  (code_review 항목은 유지·병합.)

### 4. 결과 안내
- **passed** & code-review도 passed → 커밋 가능(hook 통과).
- **failed** → 취약점과 수정안을 요약, 수정 후 재리뷰. 커밋은 계속 차단됨.

## 하지 말 것
- 형식적 통과. 민감정보 다룸에도 기본 항목(인증·암호화·비밀관리) 생략.
