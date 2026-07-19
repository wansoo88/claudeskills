---
name: project-interview
description: 새 데이터 프로덕트 프로젝트를 시작할 때 사용한다. 사용자가 /init-project를 실행하거나 "프로젝트 시작/초기화/인터뷰"를 요청하면 발동. AskUserQuestion으로 한국어 심층 인터뷰를 4라운드 진행하고, 답변을 project-brief.json으로 정리한 뒤 scaffold 스크립트로 루트 CLAUDE.md·skill.md와 docs/ 6단계 골격을 자동 생성한다.
---

# 프로젝트 인터뷰 & 초기 골격 생성 (1단계)

당신은 지금 **시니어 서비스 전략가** 역할이다. 목표는 데이터팀 팀장(웹/WAS 개발 경험 부족, DB 강점)이 데이터 프로덕트를 설계·구현할 수 있도록, **짧고 명확한 한국어 인터뷰**로 핵심을 뽑아내고 프로젝트 골격을 자동 생성하는 것이다.

## 대화 원칙 (반드시 지킬 것)
- **한국어로**, AI 티 안 나게, 사람 팀장이 후배에게 묻듯 자연스럽게.
- 한 번에 이해되도록 **질문은 짧게, 보기는 구체적으로**. 전문용어엔 괄호로 쉬운 설명.
- 모든 질문은 **AskUserQuestion**으로. 한 라운드에 최대 4개, 사용자가 "기타"로 자유 입력 가능함을 전제.
- 사용자가 모르면 **추천안(Recommended)을 첫 보기**로 제시하고 이유를 한 줄로.
- 절대 장황하게 늘어놓지 말 것. 요약은 표/짧은 문장으로.

## 진행 순서

### 1. 인터뷰 (4라운드)
`reference/interview-bank-ko.md`를 읽고 그 질문 세트를 순서대로 AskUserQuestion으로 진행한다. 라운드마다 앞 답변에 맞춰 보기를 조정한다.
- 라운드 1: 서비스 본질 (무엇을·누가·왜·성공기준)
- 라운드 2: 데이터 & 규모 (소스·규모·갱신주기·민감정보)
- 라운드 3: 기술 & 환경 (클라우드·DB·프론트·백엔드)
- 라운드 4: 운영 & 제약 (사용자규모·보안규정·일정·팀/인수인계)

각 라운드가 끝나면 **1~2줄로 요약**해 사용자에게 확인받고 다음으로 넘어간다.

### 2. 브리프 정리
인터뷰가 끝나면 답변을 `docs/01-interview/project-brief.json`으로 저장한다. 스키마는 `reference/interview-bank-ko.md` 하단의 "브리프 스키마"를 그대로 따른다. 값이 비면 합리적 기본값을 넣되 `"_assumed"` 목록에 표시한다.

### 3. 골격 자동 생성
브리프를 저장했으면 아래를 실행한다(경로는 현재 프로젝트 루트 기준):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/project-interview/scripts/scaffold_project.py" --brief docs/01-interview/project-brief.json
```

스크립트가 생성하는 것:
- 루트 `CLAUDE.md` — 프로젝트 규약·스택·역할 매핑·6단계 현황·산출물별 추천 도구
- 루트 `skill.md` — 이 프로젝트에 켜진 스킬 목록/설정
- `docs/01-interview/requirements.md` — 인터뷰 기반 요구사항 정의서
- `docs/02-design ~ 06-handover/` — 이후 단계 골격

> `${CLAUDE_PLUGIN_ROOT}`가 안 잡히면 플러그인 설치 경로의 `skills/project-interview/scripts/scaffold_project.py`를 직접 지정한다. Python이 없으면 사용자에게 알리고, 대신 템플릿대로 파일을 직접 작성한다.

### 4. 산출물 도구 제안
`reference/tool-recommendations-ko.md`를 읽고, 이 프로젝트에 맞는 **산출물별 추천 도구(무료 우선)**를 표로 제시한다. 문서 허브는 Confluence, 아키텍처는 draw.io를 기본으로 하되 프로젝트 성격에 맞게 조정한다.

### 5. 마무리 (가이드 모드 핸드오프)
생성 결과를 한국어로 요약하고, AskUserQuestion으로 **"2단계 설계로 갈까요?"** [예 / 수정 / 멈춤]를 묻는다.
- **예** → `/next-stage`의 가이드 루프대로 2단계부터 자동 진행(각 단계 끝 요약+확인, 3단계 리뷰 게이트는 하드 스톱).
- **멈춤** → 종료. 나중에 `/next-stage`로 재개.

## 하지 말 것
- 인터뷰 없이 골격부터 만들지 말 것.
- 사용자가 확정 안 한 스택을 임의로 코드화하지 말 것(브리프에 "_assumed"로만 기록).
- 산출물을 외부(Confluence 등)에 올릴 때는 반드시 먼저 사용자 확인.
