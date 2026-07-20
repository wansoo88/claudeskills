# CLAUDE.md — data-product-studio (스킬셋 개발 규약)

> 이 파일은 **스킬셋 자체를 개발·유지**할 때의 규약입니다. (개별 프로젝트용 CLAUDE.md는 인터뷰 후 자동 생성됩니다.)

## 이 저장소는 무엇인가
데이터팀이 부족한 역할을 AI로 채워 데이터 프로덕트를 1인 개발하기 위한 Claude Code 플러그인. 역할=서브에이전트, 절차=스킬, 강제=hook, 배포=plugin.

## 운영 모델 — PM/PMO 오케스트레이션 (3계층)
- 사람은 **PM/PMO 오케스트레이터**(`orchestrator` 스킬)에게만 질의. 오케스트레이터가 계획·위임·추적·게이트·보고를 담당하고, 전문 **subagent에게 위임**한다. **사람은 subagent와 직접 대화하지 않는다.**
- herdr 워크스페이스에서 오케스트레이터 세션(pane)이 사람의 창구.
- **역할 계층(super agent · sub super agent · subagent)** — 상세는 `orchestrator` 스킬 §역할 계층:
  - **super agent = PM**(orchestrator): subagent 작업 **지시/하달/감독**, 계획·게이트·보고, 전략·주요 의사결정. 사람의 단일 창구.
  - **sub super agent = PL**(보조 오케스트레이터, 병목 시 증설): PM의 **전략·의사결정 보조·논의** + subagent **작업 관리(미진행·팔로우업 위주)** + subagent의 **비민감 allow는 판단하 허용, 민감건은 팀장 컨펌**.
  - **subagent**: 위임받은 실제 작업 수행. PM·PL은 **트랙을 나눠 소유**하고, 상대 트랙은 디컨플릭트 후 접근.
- 각 역할은 3중 표현: **subagent**(`agents/`, 페르소나) + **역할 스킬**(`skills/role-*`, 전문성 카드) + **절차 스킬**(`skills/*`, 그 역할의 작업).

## 스킬/에이전트 작성 규칙 (리서치 검증 반영)
- `SKILL.md` frontmatter는 **name, description만 필수**. name ≤64자(소문자·숫자·하이픈), description ≤1024자에 **"무엇을 + 언제"** 명시.
- 본문은 **500줄 미만**. 넘치면 `reference/*.md`, `scripts/*`로 분리(참조는 한 단계 깊이).
- 스크립트는 bash로 실행 — 코드가 아니라 **실행 결과만** 컨텍스트에 올라가므로 무거운 로직은 스크립트로.
- 서브에이전트는 **최소 도구권한**. 자동 위임은 불안정하므로 문서/커맨드에서 **이름으로 명시 호출**.
- 스펙 추적은 **agentskills.io** (구 anthropics/skills 인repo 스펙은 stub, 인용 금지).

## 사용자 대면 원칙
- 항상 **한국어**, AI 티 없이, 짧고 명확히. 결정은 AskUserQuestion으로.
- 외부(Confluence 등) 업로드·비가역 작업 전 반드시 확인.

## 로드맵 (파일럿 → 확장)
- [x] 1단계: project-interview 스킬 + service-strategist + /init-project + scaffold 스크립트 (검증 완료)
- [x] 2단계: infra/software/db-architect + architecture-design(gen_drawio)·db-modeling(gen_erd)·security-design 스킬 + /next-stage (생성기 검증 완료)
- [x] 3단계: frontend-react/backend-docker + code-reviewer/security-reviewer + implementation-plan·code-review·security-review 스킬 + **강제 hook**(block_destructive·require_review·record_review, 로직 검증 완료)
- [x] 4~6단계: qa-engineer + testing-unit-e2e(Pytest/Jest+Playwright) + monitoring-setup(Grafana/CloudWatch) + handover-check
- [x] 월간 갱신: refresh-skills 스킬 + /refresh-skills + bump_version.py + MONTHLY-REFRESH.md (로컬/수동, 검증 완료)

- [x] 도입/설치: `project-adopt` + `/adopt-project`(기존 프로젝트 도입, scaffold `--adopt`), `INSTALL.md`(전역/프로젝트별/마켓플레이스 설치 + 발동 확인), `.claude-plugin/marketplace.json`

> **파이프라인 6단계 + 월간 갱신 + 기존 프로젝트 도입 + 설치 가이드 완료 (v0.5).** 이후는 실사용 피드백 반영·개별 스킬 심화.

## 신규 vs 기존 프로젝트
- 신규: `/init-project` (전체 인터뷰 → 골격 생성).
- 기존/중간: `/adopt-project` (스캔 → 보강 인터뷰 → 기존 보존 도입, `CLAUDE.generated.md` 병합, 시작 단계 제안).
- 설치는 INSTALL.md. 전역 설치하면 어느 폴더에서든 발동.

## 리뷰 게이트 동작 요약 (3단계)
- `hooks/hooks.json`: PreToolUse(Bash)→ block_destructive + require_review, SubagentStop(code-reviewer|security-reviewer)→ record_review.
- 원장 `docs/03-build/.review-state.json`의 `code_review`·`security_review`가 **둘 다 `passed`** 여야 `git commit`/`git push` 허용. 아니면 차단.
- 리뷰 판정은 code-review/security-review 스킬(+리뷰어 서브에이전트)이 기록. record_review는 백스톱.

## 근거 문서
- `background/research/claude-skills-트렌드-리서치-2026-07.md`
- `background/design/스킬셋-전체설계도.md`
