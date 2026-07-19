# Claude Skill 생성 — 최신 트렌드 리서치 (2026년 7월)

> 조사 방식: deep-research 워크플로우 (107개 에이전트, 25개 소스, 124개 주장 추출 → 상위 25개 주장 3표 적대적 검증, 25개 전부 확인).
> 신뢰도 표기: **[검증됨]** = 공식 1차 출처 + 3표 검증 통과 / **[방향성]** = 1차 소스에서 추출됐으나 검증 예산 컷으로 3표 검증은 미실시.

---

## 0. 한 줄 결론

Anthropic의 **Skill · Subagent · Plugin · Hook** 4종 인프라는 당신이 원하는 "1인 다역할 개발 시스템"을 만들기에 **이미 완성되어 있다**(공식 문서로 전부 확인). 남은 일은 인프라가 아니라 **각 역할(아키텍트·개발자·QA)의 전문 내용을 채우는 것**이다.

---

## 1. Skill이란 무엇인가 [검증됨]

- **구조**: 하나의 디렉토리 + 그 안의 `SKILL.md` 파일. 여기에 지침·스크립트·참고자료를 묶는다.
- **필수 메타데이터는 딱 2개** (YAML frontmatter):
  - `name`: 최대 64자, 소문자·숫자·하이픈만, `anthropic`/`claude` 예약어 금지
  - `description`: 최대 1024자, **"무엇을 하는지 + 언제 쓰는지"를 반드시 명시** (이 문장이 Skill 자동 호출을 결정함)
  - `allowed-tools`는 **필수 아님**(선택 항목).
- **3단계 점진적 공개(progressive disclosure)** — 토큰 비용 설계의 핵심:
  - **L1**: 모든 Skill의 이름+설명은 시작 시 항상 로드 (Skill당 ~100토큰)
  - **L2**: 본문(SKILL.md)은 **트리거될 때만** 로드 (목표 5,000토큰 미만, **500줄 미만 권장**)
  - **L3+**: 참조파일(`reference/*.md`)·스크립트(`scripts/*`)는 **실제로 읽을 때만** 비용 발생. 스크립트를 bash로 실행하면 **코드가 아니라 실행 결과만** 컨텍스트에 올라감.
  - → 그래서 Skill을 많이 설치해도 컨텍스트 부담이 거의 없음. 본문은 500줄 이내로, 넘치면 참조파일로 쪼개고, 참조는 **한 단계 깊이**로만.
- **Skill vs MCP** [검증됨]: **경쟁이 아니라 보완**. MCP = 외부 도구·데이터 "연결", Skill = 작업 "절차·지식". 하나의 Skill이 여러 MCP 서버를 조율할 수 있음. 2026년 개발자 합의 = **"둘 다 써라."**
- ⚠️ **중요 변화 (시점 민감)** [검증됨]: **2025년 12월 18일**부터 Agent Skills가 **오픈 표준**으로 공개됨. 정식 스펙은 이제 **`agentskills.io/specification`** 에 있음. `anthropics/skills` 레포 안의 스펙 파일은 리다이렉트 stub만 남음 → **옛 레포 스펙을 인용한 자료는 이미 낡음.**

**출처**: platform.claude.com (overview, best-practices), anthropic.com/engineering, github.com/anthropics/skills, agentskills.io

---

## 2. 다역할(멀티롤) 시스템 만드는 법 [검증됨]

당신이 필요로 한 7개 역할(서비스전략가 · 인프라/SW/DB 아키텍트 · React 프론트 · Docker 백엔드 · QA)을 이렇게 구성한다:

- **역할 1개 = Subagent 1개**. 각 Subagent는 **독립된 컨텍스트 창 + 전용 시스템 프롬프트 + 전용 도구권한**으로 격리 실행 → 한 역할의 작업이 메인 대화를 오염시키지 않음.
- **파일 형식**: `.claude/agents/` 안의 마크다운 파일 (YAML frontmatter는 `name`·`description`만 필수, `tools`·`model`·`color` 등은 선택). 본문 = 그 역할의 시스템 프롬프트. **버전관리에 커밋 → 팀 공유.**
- **파이프라인 구성** (architect → developer → code-review → QA): Claude에게 **"subagent들을 순서대로 실행"** 하라고 지시. 각 subagent가 결과를 메인 대화로 반환하면 그 컨텍스트를 다음 단계로 넘김.
- **베스트 프랙티스** (공식): ① 단일 책임 원칙으로 좁게 설계, ② description을 상세히(위임을 결정하므로), ③ 각 역할에 **필요한 도구만** 부여(보안·집중), ④ 프로젝트 subagent는 버전관리에 커밋.
- **전체를 Plugin으로 패키징**: 하나의 Plugin 디렉토리가 **skills + agents + hooks + MCP서버 + LSP + monitors**를 한 묶음으로 배포하는 단위. `agents/`·`commands/`·`skills/` 폴더 구조로 자동 발견. **marketplace로 배포**.
- ⚠️ **실전 주의** [검증됨]: **자동 위임(auto-delegation)은 실제로는 불안정**. 확실하게 트리거하려면 **이름으로 명시 호출**하는 게 안정적.

**출처**: code.claude.com (sub-agents, plugins-reference), github.com/contains-studio/agents

---

## 3. 필수 게이트: code-review / security-review 강제 [검증됨]

당신이 "무조건 진행"이라 못박은 부분 — Hook으로 **결정론적으로 강제**한다:

- **Hook** = 특정 생명주기 지점에서 자동 실행되는 명령/HTTP/MCP도구/프롬프트/에이전트 (핸들러 5종: command, http, mcp_tool, prompt, agent).
- **PreToolUse hook**: 도구 실행 **직전에 하드 차단** 가능 — exit code 2 또는 JSON `permissionDecision: "deny"`. 예: 파괴적 Bash(`rm -rf`)·비인가 쓰기 차단.
- **SubagentStart / SubagentStop hook**: matcher로 **특정 역할**(예: `security-reviewer`, `code-reviewer`)이 시작/종료될 때 검증 스크립트 발동 → "보안리뷰 없이 다음 단계 못 감" 같은 게이트 구현.
- **Claude Code 내장 Code Review** [방향성]: 멀티에이전트 구조 — 여러 전문 에이전트가 diff를 병렬 분석(로직오류/보안취약점/엣지케이스/회귀) → 별도 검증 단계가 실제 코드 동작 대비 오탐 필터링.
- ⚠️ 주의 [검증됨]: `permissionDecision: "deny"`가 **Edit 도구에선 안 걸린 사례**(이슈 #37210) 보고됨 → 하드 게이트는 **Bash/MCP 도구에서 가장 확실**.

**출처**: code.claude.com (hooks, code-review, security)

---

## 4. 월 1회 자동 업데이트 구조 [검증됨] — 당신이 "중요"라고 강조한 부분

- **Plugin 버전 해석(version-resolution)에 연결**하는 게 정석:
  - `plugin.json`에 `version` 명시 → **그 필드를 올릴 때만** 사용자에게 업데이트 전달 (semver 권장). 커밋만 하고 안 올리면 반영 안 됨.
  - `version` **생략** → git 커밋 SHA로 대체 → **모든 새 커밋이 곧 새 버전(업데이트)**. Claude Code가 이 값을 캐시 키로 써서 자동 업데이트 여부 판단.
  - → 월간 갱신 구현: (a) 버전 미지정 Plugin에 **매월 커밋 스케줄**, 또는 (b) 매월 **semver 버전 올리기**.
- ⚠️ **핵심 함정** [방향성, 매우 중요]: 세션 범위 **scheduled task/loop는 생성 7일 후 자동 만료** → **지속적인 월간 갱신을 못 함**. 진짜 월간 자동화는 **Routines · Desktop 예약작업 · GitHub Actions** 중 하나로 돌려야 함.

**출처**: code.claude.com (plugins-reference, scheduled-tasks)

---

## 5. 참고할 실전 레포 (best practice GitHub) [방향성]

| 레포 | 규모 | 쓸모 |
|---|---|---|
| **wshobson/agents** | 94 plugins / 203 agents / 175 skills / 109 commands (~36.6K stars) | 당신이 만들려는 "대규모 멀티롤 스킬 시스템"의 **가장 큰 실전 예시**. marketplace 구조·모델 티어링까지 그대로 참고 |
| **VoltAgent/awesome-claude-code-subagents** | 154+ subagent, 10개 카테고리 (인프라 16 / 품질·보안 17 / 코어개발 등) | 당신의 7개 역할에 **직접 매핑**되는 subagent 카탈로그 |
| **VoltAgent/awesome-agent-skills** | 1,497+ skill 집계 | 공식+커뮤니티 Skill **최대 아카이브** |
| **contains-studio/agents** | — | subagent 실전 구조(`cp -r agents/* ~/.claude/agents/`) 확인용 |

---

## 6. 경쟁사·업계 트렌드 [방향성 — 1차 소스 추출, 3표 검증 미실시]

> 당신이 요청한 "AWS·Meta·Anthropic·OpenAI 등 해외 트렌드". 아래는 수집됐으나 검증 예산 컷으로 최종 검증 리스트엔 못 든 항목 → **방향성 참고용**.

- **OpenAI**: AgentKit / **Agent Builder** = 비주얼 드래그앤드롭 캔버스(노코드)로 멀티에이전트 워크플로우 작성·버전관리. → Anthropic의 **파일(마크다운) 기반**과 대비되는 **GUI 노선**.
- **오케스트레이션 방식 분화**: Claude Agent SDK = **subagents(병렬/중첩)** / OpenAI Agents SDK = **handoffs(선언적 위임)** / Google ADK = **graph 기반 분기 워크플로우**.
- **AWS**: **Kiro "powers"** = 도메인 컨텍스트·베스트프랙티스·예제·문서를 Kiro 에이전틱 IDE에 패키징 → **Claude Skill의 직접 대응물**. (Bedrock AgentCore + Kiro 조합으로 모더나이제이션 밀고 있음)
- **MCP 거버넌스 이전**: 2025년 12월, MCP 관리권이 Anthropic → **Linux Foundation의 Agentic AI Foundation(AAIF)** 으로 이관. 창립 멤버 Anthropic·OpenAI·Google·Microsoft·AWS → **중립적 멀티벤더 표준**이 됨.
- **큰 그림(수렴 vs 분화)**: 업계가 **"선언적 스킬/컨텍스트 파일 + MCP 연결"** 방향으로 **수렴** 중이고, Anthropic이 MCP에 이어 **Agent Skills로 표준 주도권**을 노리는 구도. 오케스트레이션 primitive(subagent vs handoff vs graph)는 **분화**.
- **Meta**: 이번 조사에서 유의미한 확인 결과 없음(gap).

**출처**: openai.com(introducing-agentkit), aws.amazon.com(bedrock-agentcore/kiro), thenewstack.io, composio.dev, zylos.ai

---

## 7. 당신 스택에 맞는 공식 레퍼런스 [방향성]

- **AWS 3-tier 참조 아키텍처**: React.js 프론트 + Nginx(web tier) / 애플리케이션 로직(middle=WAS tier) / 관계형 DB(data tier). ALB로 트래픽 분산. → **당신 목표 스택(React 프론트 + 컨테이너 백엔드 + DB)과 정확히 일치.**
- **출처**: github.com/aws-samples/aws-three-tier-web-architecture-workshop

---

## 8. ⚠️ 이번 리서치가 못 채운 공백 (정직한 한계)

Anthropic **인프라(뼈대)** 는 완벽히 검증됐지만, 아래는 검증된 결론이 없음 → **실제 skill 제작 단계에서 추가 조사 필요**:

1. **각 역할의 전문 "내용"**: AWS 3-tier 상세 설계, ERD/UML + draw.io 산출물 생성법, 구체적 code-review·security-review 체크리스트, CI + 단위/e2e 테스트(Playwright/Cypress) — **뼈대는 확인, 알맹이는 미확인**.
2. **경쟁사 세부 비교**: 위 6번은 방향성 수준. 정밀 비교는 미검증.
3. **당신 고유 요구의 공식 확인 안 됨**: AskUserQuestion 기반 한국어 인터뷰 흐름, 프로젝트 init 시 `CLAUDE.md`/`skill.md` 자동생성 관례, 커스텀 슬래시 커맨드 — 이 흐름들은 공식 문서 검증엔 안 잡힘(직접 설계 필요).

---

## 9. 이 리서치가 확정한 "설계 원칙" 요약 (skill 제작 시 그대로 적용)

1. 역할 = **subagent** (`.claude/agents/`), 절차·지식 = **skill** (`.claude/skills/`), 외부연결 = **MCP**, 강제 게이트 = **hook**, 배포 = **plugin + marketplace**.
2. SKILL.md 본문 **500줄 미만**, 넘치면 `reference/`·`scripts/`로 분리, `description`에 "무엇+언제" 명확히.
3. code-review·security-review는 **PreToolUse / SubagentStop hook으로 강제**.
4. 월간 갱신은 **plugin 버전 + GitHub Actions/Routines**(7일 만료되는 세션 task 금지).
5. 자동 위임 믿지 말고 **역할 이름으로 명시 호출**.
6. 스펙 추적은 **agentskills.io** (옛 anthropics/skills 스펙 인용 금지).

---

*생성: 2026-07-19 · deep-research 워크플로우 (Opus 4.8 1M) · 검증 25/25 통과, 반박 0.*
