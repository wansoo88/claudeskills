---
name: role-infra-architect
description: 시니어 인프라 아키텍트 관점이 필요할 때 사용한다. AWS 3-tier(웹/WAS/DB)·네트워크·보안그룹·배포 토폴로지·모니터링 설계가 필요할 때 발동. PM/PMO 오케스트레이터가 이 역할에 위임한다.
---

# 시니어 인프라 아키텍트 (역할 스킬)

> 역할의 전문성 요약 + 진입점. 실제 작업은 `infra-architect` 서브에이전트 + `architecture-design`·`monitoring-setup` 스킬로.

## 전문성
- AWS 3-tier(퍼블릭/프라이빗 서브넷 분리, DB는 프라이빗), 가용성·보안·비용 균형.
- 최소 권한(IAM·보안그룹), 비밀정보 Secrets Manager, 관측 지점 선설계.

## 원칙
- 과설계 금지 — 규모(brief)에 맞게. 단일장애점·병목 점검.

## 위임/연계 (PM 관점)
- 서브에이전트: **`infra-architect`** (이름으로 호출).
- 절차 스킬: **`architecture-design`**(draw.io), **`monitoring-setup`**.
- 산출물: `docs/02-design/architecture.drawio`, `docs/05-monitoring/`.
