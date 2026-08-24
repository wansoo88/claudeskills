# CHANGELOG

## 0.13.0 — 2026-08-24
- **사내 시큐어코딩 가이드 v1.0(E.S11.G07) 준수 반영** — `security-review/reference/secure-coding-guide-ko.md` 신규. 제5~18조 코딩 기준(취약/안전 예시 포함), 언어별 기준(Python 제17조·JS/TS 제18조), 오픈소스·SBOM, 별첨1 점검 체크리스트 20항목, 증적 목록을 리뷰 실행 기준으로 재구성. **사내 기준이 OWASP보다 우선**
- **심각도 4등급 판정 도입(제20조)** — 긴급·높음 = `failed`, 보통 = pass 가능하되 followups 등재 필수, 낮음 = 코멘트. 기존의 임의 fail 조건을 대체
- **`scan_secure_coding.py` 신규** — 가이드 조항별 위반 후보 정적 사전점검(40여 규칙). `--changed-only`(git 변경분)·`--json`·`--strict` 지원. 게이트가 아니라 리뷰 입력
- **승인된 예외 경로 신설(제9장)** — `require_review.py`가 `security_review.status == "exception"` 을 허용하되 대상·사유·위험평가·보완통제·개선계획·**만료일**·승인자 7요건을 전부 검증하고 **만료 시 자동 재차단**. 예외는 보안리뷰에만 적용(코드리뷰는 계속 `passed`만 인정)
- **오탐 판단 근거 기록 의무화(제19조 3항)** — `security-review-log.md`를 취약점·오탐 판정·별첨1 20항목·재리뷰 4개 절 구조로 규정. 증적 최소 3년 보관·마스킹 명시(제21조)
- `security-design`이 세션/토큰·파일처리·SSRF·자원한계·로그 마스킹 항목을 설계에 포함하도록 확장, 별첨1 20항목을 게이트 기준으로 산출
- `security-baseline-ko.md`에 사내 조항↔OWASP 매핑과 **사내 기준이 더 엄격한 지점** 표 추가
- `code-review` 보안 냄새 항목을 가이드 조항과 연결(동적 실행·DOM 싱크·외부 입력 흐름 추가)
- 훅(`require_review`·`block_destructive`)이 한국어 차단 사유를 UTF-8로 출력하도록 수정 — Windows cp949 콘솔에서 깨지던 문제

## 0.12.0 — 2026-08-21
- **`serveone-bi-ui` 스킬 신규** — 사내 BI/대시보드 UI 규약(화면 전 4질문·절대규칙·차트 라이브러리 라우팅·데이터 컬러 hex·마크 스펙·타이포/밀도·안티패턴). 내장 `dataviz`보다 우선. 조직 맥락·도메인 용어·미확정 링크는 `reference/serveone-context-ko.md`
- **scaffold 생성 CLAUDE.md에 조직 맥락 + UI/UX 규약 항상 삽입** (`org_and_ui_md()`), 생성 skill.md 표에 `serveone-bi-ui` 상시 항목 추가
- **`code-review`에 UI 게이트 12항목 추가 — 전부 fail 사유**(화면·차트 변경 PR 한정). 체크리스트·`code-reviewer` 에이전트 동기화
- `frontend-react`·`role-frontend`를 Next.js App Router + TypeScript + Tailwind + shadcn/ui 스택으로 갱신, 서버/클라이언트 경계 규칙과 `serveone-bi-ui` 연계 명시
- `tool-recommendations-ko.md`에 프론트 스택·차트 라이브러리 라우팅 행 추가
- `/init-project`가 CLAUDE.md·skill.md 생성 확인을 명시하도록 보강

## 0.11.0 — 2026-07-20
- 역할 계층 3단계 정의 도입 — super agent(PM)/sub super agent(PL)/subagent. PL=PM 의사결정 보조+subagent 미진행 관리+비민감 allow 판단하 허용·민감건 팀장 컨펌. orchestrator SKILL·repo CLAUDE.md·scaffold 생성 CLAUDE.md 반영

## 0.10.0 — 2026-07-20
- orchestrator: 팔로우업 원장(Follow-up Ledger) 도입 — 지시 무손실(사람↔pm↔subagent) 추적, 매 루프 Sweep + 사람 배정 과제 확인 추적. scaffold가 docs/00-orchestration/followups.md 생성, 생성 CLAUDE.md 운영모델에 반영

## 0.9.0 — 2026-07-19
- PM/PMO 오케스트레이터 스킬(사람의 유일한 창구, 위임 지휘) + 역할 스킬 7종(role-*) + 생성 CLAUDE.md/skill.md에 오케스트레이션 운영모델

## 0.8.0 — 2026-07-19
- 전역 설치 자동화(install.ps1 + tools/merge_hooks.py) + README 루트폴더·부트스트랩 가이드 + 스크립트 경로 규칙

## 0.7.0 — 2026-07-19
- 가이드 모드(단계 끝 요약+확인 후 자동 진행) + 기존 프로젝트 갭 리포트(scan_project.py) + adopt 진입점 자동 제안

## 0.6.0 — 2026-07-19
- readme-writer 스킬 + /write-readme + 사용설명서(USAGE.md) + 스킬 저작 가이드(AUTHORING-SKILLS.md)

## 0.5.0 — 2026-07-19
- 기존 프로젝트 도입(project-adopt/adopt-project) + scaffold adopt 모드 + 설치·발동 가이드(INSTALL.md) + 로컬 마켓플레이스(marketplace.json)

## 0.4.0 — 2026-07-19
- 4~6단계(QA·테스트, 모니터링, 인수인계) + 월간 갱신(refresh-skills) 추가

