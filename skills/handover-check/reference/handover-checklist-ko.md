# 인수인계 완결성 체크리스트 (참조)

## 1단계 — 요구사항
- [ ] requirements.md 존재, 서비스정의·사용자·성공기준(KPI) 명확
- [ ] project-brief.json의 "_assumed" 값들이 확정되었나

## 2단계 — 설계
- [ ] architecture.drawio (열람 가능, 최신)
- [ ] erd.md + schema.dbml (실제 스키마와 일치)
- [ ] api-spec.md (구현과 일치)
- [ ] security.md (security-review 기준 포함)

## 3단계 — 구현/리뷰
- [ ] implementation-plan.md
- [ ] code-review-log.md + security-review-log.md
- [ ] .review-state.json 두 항목 passed
- [ ] Dockerfile/compose로 로컬 실행 가능

## 4단계 — 테스트
- [ ] test-plan.md + test-report.md
- [ ] 단위/e2e 통과, 성공기준 검증됨

## 5단계 — 모니터링
- [ ] monitoring-plan.md (SLI/SLO·알람·대시보드·로그정책)

## 일관성 교차 점검
- [ ] ERD ↔ 실제 DB 스키마
- [ ] api-spec ↔ 백엔드 구현 ↔ 프론트 호출
- [ ] CLAUDE.md 6단계 체크박스 ↔ 실제 상태
- [ ] 미해결 결함·기술부채가 문서화됨

## 인수인계 문서(handover.md) 필수 항목
- [ ] 서비스 1줄 요약 + 아키텍처 링크
- [ ] 로컬 실행/배포/환경변수·비밀 관리
- [ ] 폴더·모듈 지도, 자주 하는 작업
- [ ] 운영(대시보드/알람/런북/장애 대응)
- [ ] 알려진 이슈·다음 할 일

## 최종 기준
- [ ] "처음 보는 사람이 30분 내에 로컬 실행 + 구조 이해" 가능
