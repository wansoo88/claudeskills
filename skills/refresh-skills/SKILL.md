---
name: refresh-skills
description: 월 1회 스킬셋을 최신 트렌드로 갱신할 때 사용한다(로컬/수동). Claude Skills·AWS·테스트·보안 등 최신 동향을 조사해 각 스킬의 reference 파일을 갱신하고, bump_version.py로 plugin.json 버전을 올려 팀에 배포되게 한다. /refresh-skills로 실행.
---

# 월간 스킬 갱신 (로컬/수동)

목표: 이 스킬셋이 낡지 않도록 **한 달에 한 번** 최신 동향을 반영하고 버전을 올린다. Claude Code는 plugin.json 버전이 바뀔 때만 업데이트를 전달하므로, 버전 bump가 배포 트리거다.

## 진행 순서

### 1. 최신 동향 조사
아래 주제로 조사한다(가능하면 deep-research 워크플로우, 없으면 웹검색 수동):
- **Claude Agent Skills / Claude Code**: SKILL.md 스펙 변화(agentskills.io), 서브에이전트·hook·plugin 변경.
- **스택 트렌드**: AWS 아키텍처, React, Docker/컨테이너, PostgreSQL.
- **품질/보안**: OWASP 업데이트, Playwright/테스트 관행, 모니터링.

### 2. 변경점 요약
"무엇이 새로워졌고 / 무엇이 낡았나(deprecated)"를 항목별로 한국어로 정리. 근거 링크 포함.

### 3. reference 파일 갱신
영향받는 파일만 수정:
- `skills/project-interview/reference/tool-recommendations-ko.md`
- `skills/architecture-design/reference/aws-3tier-patterns.md`
- `skills/db-modeling/reference/erd-guide-ko.md`
- `skills/security-design/reference/security-baseline-ko.md`
- `skills/testing-unit-e2e/reference/testing-guide-ko.md`
- `skills/monitoring-setup/reference/monitoring-guide-ko.md`
- 필요 시 각 SKILL.md 본문(단, 500줄 미만 유지).

### 4. 버전 올리기 + 기록
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/refresh-skills/scripts/bump_version.py" \
  --level minor --note "2026-08 트렌드 반영: <핵심 변경 요약>"
```
→ `plugin.json` 버전 상승 + `CHANGELOG.md` 기록.

### 5. 마무리
변경 요약을 한국어로 보고하고, 팀원은 다음 동기화 때 자동 반영됨을 안내. 큰 변경이면 README/설계도도 갱신.

## 원칙
- **출처 우선**(공식 문서·검증된 자료). 근거 없는 반영 금지.
- 파괴적 변경은 CHANGELOG에 명확히. 스펙 추적은 agentskills.io.
- 세션 예약작업은 7일 만료 → 월간은 로컬/수동 루틴으로(‑ MONTHLY-REFRESH.md 참고).
