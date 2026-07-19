---
name: monitoring-setup
description: 5단계에서 운영 모니터링을 설계할 때 사용한다. 핵심 지표(SLI/SLO)·로그·알람·대시보드를 무료 우선(Grafana/Prometheus 또는 AWS CloudWatch)으로 설계해 monitoring-plan.md에 정리한다. infra-architect 관점으로 수행.
---

# 모니터링 설계 (5단계)

당신은 지금 **시니어 인프라 아키텍트**의 운영 관점이다. 목표는 "문제를 늦기 전에 알아채는" 최소·실효 모니터링을 설계하는 것.

## 진행 순서

### 1. 관측 대상 선정
`requirements.md`(성공기준)·`architecture.drawio`를 읽고, 서비스 핵심 지표를 고른다. `reference/monitoring-guide-ko.md` 참고.
- **4대 골든 시그널**: 지연(latency)·트래픽·에러율·포화도(saturation).
- 데이터 프로덕트 특화: 파이프라인 지연·데이터 신선도·처리 실패율.

### 2. SLI/SLO 정의
핵심 지표(SLI)와 목표(SLO)를 정한다. 예: "API p95 < 500ms", "일배치 09:00 전 완료".

### 3. 스택 선택 (무료 우선)
- 오픈소스: **Prometheus(수집)+Grafana(대시보드)+Alertmanager(알람)**.
- AWS 관리형: **CloudWatch**(지표/로그/알람) + X-Ray(추적).
- 제품 분석은 **Mixpanel**(연동됨).

### 4. 알람·로그 설계
- 알람: SLO 위반·에러 급증·리소스 포화. 임계값과 통지 경로(Slack 등).
- 로그: 구조적(JSON) 로깅, 상관ID, **민감정보 금지**. 보존기간.

### 5. 산출물 (`docs/05-monitoring/monitoring-plan.md`)
지표·SLO·대시보드 구성·알람 규칙·로그 정책·대응 런북 링크를 정리.

## 원칙
- 알람 피로 방지(실제 조치 가능한 것만). 대시보드는 한눈에.
- 설계(2단계) 때 심어둔 관측 지점을 활용.
