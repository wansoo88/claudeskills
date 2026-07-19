---
description: 가이드 모드로 다음 단계를 진행한다. 단계 완료 → 요약 → 확인 → 다음 단계로 이어감.
---

프로젝트 루트의 `skill.md`·`CLAUDE.md`를 읽어 현재 단계를 파악한 뒤, **가이드 모드**로 진행하라.

## 가이드 루프 (CLAUDE.md의 "진행 방식"을 따름)
1. **다음 미완료 단계 실행** — 아래 매핑의 스킬/역할을 **이름으로 명시 호출**.
2. **산출물 3~5줄 한국어 요약**.
3. **AskUserQuestion**: "다음 단계(N: 이름)로 갈까요?" → [예 / 이번 단계 수정 / 여기서 멈춤].
4. **예** → 1로 돌아가 다음 단계 진행. **수정** → 이번 단계 보완 후 다시 확인. **멈춤** → `skill.md`·`CLAUDE.md` 상태 갱신 후 종료.
5. 각 단계 완료 시 `skill.md`의 상태를 갱신.

## 단계 → 스킬/역할
- **2 설계** → `architecture-design`(infra-architect) → `db-modeling`(db-architect) → `security-design`. 산출물 `docs/02-design/`.
- **3 구현** → `implementation-plan`(software-architect) → frontend-react/backend-docker → **`code-review`·`security-review` 필수**.
  - ⚠️ **하드 스톱**: 두 리뷰가 passed 되기 전엔 다음 단계로 못 간다(훅이 커밋 차단).
- **4 테스트** → `testing-unit-e2e`(qa-engineer).
- **5 모니터링** → `monitoring-setup`(infra-architect).
- **6 인수인계** → `handover-check`. 이후 `/write-readme` 제안.

## 규칙
- 외부(Confluence 등) 업로드·비가역 작업 전 사용자 확인.
- 사용자가 "쭉 진행"을 명시하면 소프트 확인은 줄이되 3단계 리뷰 게이트는 항상 지킨다.

특정 단계 지정 또는 "쭉 진행" 등: $ARGUMENTS
