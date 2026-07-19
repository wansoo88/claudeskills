# 프로젝트 README 템플릿 & 작성 원칙 (참조)

## 좋은 README의 기준
- **처음 보는 사람이 30분 내 실행** 가능. 복붙 가능한 명령.
- 최신 상태와 일치. 실제로 있는 것만 적는다(없으면 "미정/TBD" 표시).
- 위에서 아래로 갈수록 상세(빠른 시작 → 심화).

## 권장 구조

```markdown
# <프로젝트 이름>
<한 줄 설명: 무엇을 하는 서비스인가>

## 개요
- 무엇을 / 누가 씀 / 왜(해결 문제) / 성공기준
- 아키텍처: docs/02-design/architecture.drawio (링크/썸네일)

## 주요 기능
- 기능 1, 2, 3 (사용자 관점)

## 기술 스택
| 계층 | 기술 |
|---|---|
| 프론트 | React ... |
| 백엔드 | FastAPI (Docker) ... |
| DB | PostgreSQL ... |
| 인프라 | AWS ... |

## 빠른 시작
### 사전 요구
- Docker / Docker Compose, (Node, Python 등)
### 설치 & 실행
​```bash
git clone <repo> && cd <repo>
cp .env.example .env   # 값 채우기
docker compose up -d
​```
→ http://localhost:<port> 접속

## 환경 변수
| 이름 | 설명 | 예 |
|---|---|---|
| DATABASE_URL | DB 접속 | postgresql://... |
| ... | ... | ... |

## 프로젝트 구조
​```
frontend/   React 앱
backend/    API (레이어: router/service/repository)
docs/       설계·테스트·운영 산출물
​```

## 사용법 / API
- 핵심 엔드포인트(요약) 또는 docs/02-design/api-spec.md 링크

## 테스트
​```bash
pytest            # 백엔드 단위
npm test          # 프론트
npx playwright test  # e2e
​```

## 배포 / 운영
- 배포 방법, 모니터링 대시보드·알람(docs/05-monitoring)

## 문의 / 인수인계
- 담당·연락, 상세 인수인계: docs/06-handover/handover.md
```

## 작성 팁
- 명령은 **실제 파일 기준**(package.json scripts, compose 서비스명 확인).
- 스크린샷/다이어그램은 상대경로로. 배지는 과하지 않게.
- 데이터 프로덕트는 **데이터 소스·갱신주기·지표 정의**를 개요에 넣으면 좋다.
- 민감정보(실제 키·비밀)는 절대 README에 넣지 않는다.
