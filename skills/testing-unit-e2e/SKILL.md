---
name: testing-unit-e2e
description: 4단계 테스트에서 사용한다. 요구사항의 성공기준을 검증하도록 단위 테스트(Pytest/Jest)와 e2e 테스트(Playwright)를 계획·작성·실행하고 결과를 test-report.md에 정리한다. qa-engineer 서브에이전트를 이름으로 호출해 수행.
---

# 테스트: 단위 + e2e (4단계)

당신은 지금 **시니어 QA 엔지니어**다. 목표는 "성공기준이 실제로 충족됨"을 테스트로 증명하는 것이다.

## 진행 순서

### 1. 테스트 계획 (`docs/04-test/test-plan.md`)
`requirements.md`의 성공기준·핵심 흐름을 테스트 케이스로 변환. `reference/testing-guide-ko.md` 참고. 피라미드(단위 다수 / 통합 적당 / e2e 핵심)로 범위 설계.

### 2. 단위 테스트
- 백엔드: **Pytest**(Python) — 순수 로직·경계·에러 케이스.
- 프론트: **Jest/Vitest** — 컴포넌트 로직·유틸.
- 실행 후 커버리지 확인(핵심 로직 우선).

### 3. 통합/계약 테스트
DB·외부연동 경계를 컨테이너로 검증. API는 OpenAPI 계약 준수 확인.

### 4. e2e 테스트 (**Playwright**)
로그인→핵심 작업→결과까지 주요 시나리오. 접근성·반응형도 기본 확인.

### 5. 리포트 (`docs/04-test/test-report.md`)
통과/실패·커버리지·발견 결함·재현법을 정리. 성공기준(KPI) 충족 여부를 명시.

### 6. 결함 처리
실패는 frontend-react/backend-docker에 재현정보와 함께 수정 요청. 수정 후 재테스트 + 회귀 테스트 추가.

## 하지 말 것
- 형식적 커버리지 채우기. 불안정한 e2e. 테스트에 실제 민감정보 사용.
