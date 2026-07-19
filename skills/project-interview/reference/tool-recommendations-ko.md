# 산출물별 추천 도구 (무료 우선 · Confluence 중심)

> 원칙: **문서 허브 = Confluence**, **다이어그램 = draw.io**. 그 외 산출물도 "강력하면서 무료/오픈"인 도구를 우선. 가능한 것은 MCP로 연동, 아니면 코드/파일로 생성해 Confluence에 임베드.

## 단계별 매핑

| 단계 | 산출물 | 추천 도구 (무료 우선) | 연동 방식 |
|---|---|---|---|
| 1 인터뷰 | 요구사항정의서 | **Confluence** | Atlassian MCP로 페이지 생성 |
| 2 설계 | 시스템 아키텍처 | **draw.io (diagrams.net)** — 무료 | `.drawio` XML 생성 → Confluence draw.io 앱 임베드 |
| 2 설계 | ERD (DB 모델) | **Mermaid ERD** (무료, 어디서나 렌더) + **dbml/dbdiagram.io** | 마크다운/Confluence 코드매크로 |
| 2 설계 | UML(시퀀스/클래스) | **PlantUML** 또는 **Mermaid** — 무료 | 코드 as diagram |
| 2 설계 | API 명세 | **OpenAPI(Swagger)** — 무료 표준 | `openapi.yaml` → Swagger UI |
| 2 설계 | 화면 디자인/와이어 | **Figma**(무료 티어) 또는 **Excalidraw**(무료) | Figma MCP 연동 |
| 2 설계 | 보안 설계 | **OWASP ASVS/Top10** 체크리스트(무료) | Confluence 문서 |
| 3 구현 | 태스크/이슈 | **Jira** | Atlassian MCP |
| 3 구현 | 코드리뷰 로그 | (내장) **code-reviewer** 서브에이전트 | docs/03-build |
| 4 테스트 | 단위 테스트 | **Pytest**(Python) / **Jest**(JS) — 무료 | 리포지토리 |
| 4 테스트 | e2e 테스트 | **Playwright** — 무료·강력 (Cypress 대안) | 리포지토리 + 리포트 |
| 5 모니터링 | 지표/대시보드 | **Prometheus + Grafana**(오픈소스) 또는 AWS CloudWatch | 인프라 |
| 5 모니터링 | 제품 분석 | **Mixpanel** | Mixpanel MCP |
| 6 인수인계 | 최종 문서 | **Confluence** 공간 정리 | Atlassian MCP |

## 이 세션에 이미 붙어 있는 MCP (바로 활용 가능)
- **Atlassian (Confluence·Jira)** — 문서 허브 + 태스크. 정식 저장소.
- **Figma** — 디자인/와이어프레임.
- **Notion** — 대안 문서.
- **Mixpanel** — 제품/데이터 분석.
- **Microsoft 365** — 사내 문서/메일 연동 필요 시.
- **Slack** — 알림/공유.

## 무료 "다이어그램 as code" 우선 이유
- draw.io/Mermaid/PlantUML은 **텍스트로 버전관리** 가능 → git diff·월간 갱신·리뷰에 유리.
- Confluence가 세 형식 모두 렌더/임베드 지원 → 문서 허브 일원화가 쉬움.
- 라이선스 비용 0 → 팀 확산에 부담 없음.
