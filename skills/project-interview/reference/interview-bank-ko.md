# 인터뷰 질문 은행 (한국어) — 4라운드

> project-interview 스킬이 참조. AskUserQuestion으로 라운드별 진행. 각 질문은 header(≤12자)·보기 2~4개. 첫 보기는 모를 때의 추천안.

---

## 라운드 1 — 서비스 본질

1. **[무엇을]** 이번에 만들 데이터 프로덕트는 어떤 형태에 가깝나요?
   - 대시보드/리포트 (지표를 보는 화면) · 데이터 API (다른 시스템에 데이터 제공) · 분석/예측 모델 · 데이터 파이프라인(수집·가공) · 내부 업무 툴
2. **[누가]** 주 사용자는 누구인가요?
   - 사내 임직원 · 경영진 · 외부 고객 · 다른 개발팀/시스템 · 나(팀) 내부용
3. **[왜]** 지금 이걸 만들어 해결하려는 핵심 문제 한 가지는?
   - (자유 입력 유도: "수작업 리포트 반복", "데이터가 흩어져 있음", "실시간 파악 불가" 등 예시 제시)
4. **[성공기준]** 무엇이 되면 "성공"인가요?
   - 특정 지표 자동화 · 의사결정 속도 향상 · 신규 매출/기능 · 비용/시간 절감 · 정확도 향상

---

## 라운드 2 — 데이터 & 규모

1. **[데이터소스]** 데이터는 주로 어디서 오나요? (복수 가능)
   - 사내 DB · 외부 API · 파일(CSV/엑셀) · 실시간 스트림 · 아직 미정
2. **[규모]** 데이터 규모는 어느 정도인가요?
   - 소규모(~수만 건) · 중규모(수십만~수백만) · 대규모(수천만+) · 잘 모름(추정 도움 필요)
3. **[갱신주기]** 데이터는 얼마나 자주 갱신되나요?
   - 실시간/준실시간 · 시간별 · 일 배치 · 주/월 배치
4. **[민감정보]** 개인정보·결제·기밀 등 민감 데이터가 포함되나요?
   - 포함 안 됨 · 개인정보 포함 · 결제/금융 포함 · 사내 기밀 · 확인 필요

---

## 라운드 3 — 기술 & 환경

1. **[클라우드]** 어디에 배포하나요?
   - AWS (추천: 자료·레퍼런스 가장 풍부) · 기존 사내 인프라/온프레 · 기타 클라우드 · 미정
2. **[DB]** DB는 무엇을 쓰나요? (당신 강점 영역)
   - PostgreSQL (추천: 범용·강력·무료) · MySQL/MariaDB · Aurora · 기존 사내 DB · 미정
3. **[프론트]** 화면(웹)이 필요한가요?
   - React 반응형 웹 (추천) · 관리자 화면만 · 화면 없음(API/배치) · 미정
4. **[백엔드]** 백엔드 언어/방식 선호가 있나요?
   - Python/FastAPI (추천: 데이터팀 친화) · Node.js · Java/Spring · 미정 / 그리고 Docker 컨테이너 기반 확정?

---

## 라운드 4 — 운영 & 제약

1. **[사용자규모]** 예상 사용자/동시접속 규모는?
   - 소수(팀 내) · 수십~수백 명 · 수천 명+ · 잘 모름
2. **[보안규정]** 지켜야 할 보안 정책·규제가 있나요?
   - 사내 보안정책 · 개인정보보호법/GDPR · 금융/결제 규제 · 특별한 것 없음 · 확인 필요
3. **[일정]** 목표 일정은?
   - 1개월 내 MVP · 2~3개월 · 반기 · 정해지지 않음
4. **[팀/인수인계]** 누가 개발·유지하나요?
   - 나 혼자 · 나 + 팀원 소수 · 팀 전체 · 외부 인수인계 예정 (→ 인수인계 문서 중요도 결정)

---

## 브리프 스키마 (project-brief.json)

인터뷰 답변을 아래 키로 정리해 `docs/01-interview/project-brief.json`에 저장한다. 모르는 값은 기본값을 넣고 `_assumed`에 키 이름을 추가.

```json
{
  "project_name": "string (없으면 사용자에게 물어 확정)",
  "product_type": "dashboard|data-api|ml-model|pipeline|internal-tool",
  "primary_users": "string",
  "core_problem": "string",
  "success_metrics": "string",
  "data_sources": ["db", "api", "file", "stream"],
  "data_scale": "small|medium|large|unknown",
  "refresh_cycle": "realtime|hourly|daily|weekly",
  "sensitive_data": "none|pii|payment|confidential|unknown",
  "cloud": "aws|onprem|other|undecided",
  "database": "postgresql|mysql|aurora|existing|undecided",
  "frontend": "react|admin-only|none|undecided",
  "backend": "python-fastapi|nodejs|java-spring|undecided",
  "docker": true,
  "scale_users": "few|hundreds|thousands|unknown",
  "security_requirements": "string",
  "timeline": "1m|2-3m|6m|undecided",
  "team": "solo|small-team|full-team|handover",
  "doc_store": "confluence",
  "mode": "new | adopt",
  "current_stage": 1,
  "created": "YYYY-MM-DD",
  "_assumed": ["키 이름 배열"]
}
```

> `mode`: 신규는 `new`(기본), 기존 프로젝트 도입은 `adopt`(project-adopt 스킬이 설정). `current_stage`(1~6): adopt 시 어느 단계부터 시작할지. 신규는 1.
