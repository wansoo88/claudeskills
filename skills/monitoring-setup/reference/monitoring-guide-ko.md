# 모니터링 가이드 (참조) — 무료 우선

## 4대 골든 시그널 (Google SRE)
| 신호 | 의미 | 예시 지표 |
|---|---|---|
| Latency | 응답 지연 | API p50/p95/p99 |
| Traffic | 부하 | RPS, 동시접속 |
| Errors | 실패율 | 5xx 비율, 예외 수 |
| Saturation | 포화도 | CPU/메모리/커넥션풀 |

## 데이터 프로덕트 특화 지표
- **데이터 신선도**: 마지막 갱신 시각 vs 기대 주기.
- **파이프라인**: 처리 건수·실패율·지연, 배치 완료 시각(SLO).
- **품질**: 스키마 위반·null 급증·중복률.

## 스택 (무료/오픈 우선)
| 목적 | 오픈소스 | AWS 관리형 |
|---|---|---|
| 지표 수집 | Prometheus | CloudWatch Metrics |
| 대시보드 | Grafana | CloudWatch Dashboards |
| 알람 | Alertmanager | CloudWatch Alarms |
| 로그 | Loki / ELK | CloudWatch Logs |
| 분산추적 | Tempo/Jaeger | X-Ray |
| 제품분석 | — | Mixpanel(연동됨) |

## SLI/SLO 원칙
- SLI는 **사용자 체감**에 가깝게. SLO는 현실적 목표 + 에러버짓.
- 예: "가용성 99.5%/월", "배치 09:00 전 완료 99%".

## 알람 설계 (피로 방지)
- **조치 가능**한 것만 알람. 나머지는 대시보드/리포트.
- 심각도 분리(P1 즉시/P2 근무시간). 통지 경로(Slack/메일).
- 알람에는 런북 링크(무엇을 어떻게).

## 로깅
- 구조적(JSON), 상관ID(traceId), 레벨 일관.
- **민감정보 로그 금지**(보안설계와 일치). 보존기간·마스킹 정책.
