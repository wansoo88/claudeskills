---
name: implementation-plan
description: 3단계 구현 시작 시 사용한다. 설계 산출물(아키텍처·ERD·API·보안)을 읽어 레이어를 나누고 모듈·작업 분할·순서·위험과 각 작업의 code-review/security-review 게이트를 담은 구현계획서를 docs/03-build/implementation-plan.md에 작성한다.
---

# 구현 계획 (3단계 진입)

당신은 지금 **시니어 소프트웨어 아키텍트**다. 목표는 설계를 **실행 가능한 계획**으로 바꾸고, 리뷰 게이트를 계획에 못 박는 것이다.

## 진행 순서

### 1. 설계 읽기
`docs/02-design/`의 `architecture.drawio`·`erd.md`·`api-spec.md`·`security.md`와 `requirements.md`를 읽는다.

### 2. 레이어 분리
`reference/layering-guide-ko.md`를 참고해 표현/애플리케이션/도메인/데이터 레이어로 나눈다. 프론트=React, 백엔드=Docker 기준.

### 3. 구현계획서 작성 (`docs/03-build/implementation-plan.md`)
- **모듈 목록**: 레이어별 책임·의존 방향.
- **작업 분할(WBS)**: 작업 단위, 담당(frontend-react/backend-docker), 선후 순서, 예상 위험.
- **인터페이스 우선순위**: API 계약 확정 → 프론트/백엔드 병렬.
- **게이트 명시**: 각 작업 완료 시 `code-review` → `security-review` 통과 후에만 커밋(hook이 강제함).
- **초기 원장 생성**: `docs/03-build/.review-state.json`을 아래로 초기화(리뷰 미완료 상태).
  ```json
  {"code_review": {"status": "pending"}, "security_review": {"status": "pending"}}
  ```

### 4. 구현 착수 안내
계획 확정 후 backend-docker/frontend-react를 **이름으로 명시 호출**해 구현을 시작한다고 알린다. 커밋 시점마다 리뷰 게이트가 걸린다는 점을 사용자에게 안내.

## 하지 말 것
- 계획 없이 코드부터. 게이트를 계획에서 누락. 규모에 안 맞는 과도한 레이어링.
