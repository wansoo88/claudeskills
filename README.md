# data-product-studio

데이터팀이 **부족한 역할(서비스전략·인프라/SW/DB 아키텍트·React 프론트·Docker 백엔드·QA)을 AI로 채워** 데이터 프로덕트를 1인 개발하기 위한 재사용 Claude Code 스킬셋(플러그인).

> 한국어 심층 인터뷰로 시작 → `CLAUDE.md`/`skill.md`와 6단계 산출물 골격을 자동 생성 → 설계·구현·리뷰·테스트·모니터링·인수인계까지 이어짐.

## 운영 모델 — PM/PMO 오케스트레이션
사람은 **PM/PMO 오케스트레이터**(`orchestrator` 스킬)에게만 질의합니다. 오케스트레이터가 계획·위임·추적·게이트·보고를 담당하고, 전문 역할(**subagent**)에게 이름으로 위임합니다. **사람은 subagent와 직접 대화하지 않습니다.** (herdr 워크스페이스의 오케스트레이터 세션이 사람의 창구)

각 역할은 3중 표현: `agents/`(subagent 페르소나) + `skills/role-*`(전문성 카드) + `skills/*`(그 역할의 절차).

## 현재 상태 (v0.9 — 전 구간 + PM/PMO 오케스트레이션 + 도입/설치)
인터뷰→인수인계 6단계, 가이드 모드, 월간 갱신, 기존 프로젝트 도입, PM/PMO 오케스트레이터, 설치/사용/저작 문서까지 구현·검증. (9 subagent · 21 skill · 5 command)
- ✅ **오케스트레이션**: `orchestrator`(PM/PMO) + 역할 스킬 `role-*` 7종
- ✅ **도입/설치**: `project-adopt` + `/adopt-project`, `install.ps1`, `INSTALL.md`, `marketplace.json`
- ✅ **문서**: `readme-writer`(`/write-readme`), `USAGE.md`, `AUTHORING-SKILLS.md`

## 📚 문서 안내
| 문서 | 용도 |
|---|---|
| [USAGE.md](USAGE.md) | **사용 설명서** — 커맨드 흐름·시나리오·FAQ (팀원 온보딩) |
| [INSTALL.md](INSTALL.md) | 설치 & 발동 확인 (신규/기존 어디서나) |
| [AUTHORING-SKILLS.md](AUTHORING-SKILLS.md) | **스킬 직접 만드는 법** (팀 확장용) |
| [MONTHLY-REFRESH.md](MONTHLY-REFRESH.md) | 월간 갱신 루틴 |
| CLAUDE.md | 스킬셋 개발 규약 |

- ✅ **1단계 인터뷰**: `project-interview`(한국어 4라운드) + `service-strategist` + `/init-project` + `scaffold_project.py`
- ✅ **2단계 설계**: `infra-architect`·`software-architect`·`db-architect` + `architecture-design`(gen_drawio→draw.io) + `db-modeling`(gen_erd→Mermaid ERD+dbml) + `security-design` + `/next-stage`
- ✅ **3단계 구현**: `frontend-react`·`backend-docker`·`code-reviewer`·`security-reviewer` + `implementation-plan`·`code-review`·`security-review` + **강제 hook**(두 리뷰 passed 전 커밋 차단, 위험명령 차단)
- ✅ **4단계 테스트**: `qa-engineer` + `testing-unit-e2e`(Pytest/Jest + Playwright)
- ✅ **5단계 모니터링**: `monitoring-setup`(Grafana/Prometheus/CloudWatch)
- ✅ **6단계 인수인계**: `handover-check`(완결성 체크 + handover.md)
- ✅ **월간 갱신**: `refresh-skills` + `/refresh-skills` + `bump_version.py` + `MONTHLY-REFRESH.md` (로컬/수동)

## 폴더 구조
```
data-product-studio/
├── .claude-plugin/plugin.json
├── agents/
│   ├── service-strategist.md        # 1단계
│   ├── infra-architect.md           # 2단계
│   ├── software-architect.md        # 2·3단계
│   └── db-architect.md              # 2단계
├── skills/
│   ├── project-interview/           # 1단계: 인터뷰+골격생성 (scaffold_project.py)
│   ├── architecture-design/         # 2단계: AWS 아키텍처 (gen_drawio.py)
│   ├── db-modeling/                 # 2단계: ERD (gen_erd.py)
│   └── security-design/             # 2단계: 보안설계
├── commands/
│   ├── init-project.md              # /init-project
│   └── next-stage.md                # /next-stage
├── CLAUDE.md
└── README.md
```

## 🗂️ 루트 폴더 — 어디에 두어야 모든 프로젝트가 참조하나

**핵심: "모든 프로젝트가 참조하는 root"는 `~/.claude/` (전역) 입니다. 프로젝트마다 따로 지정할 필요 없습니다.**

루트는 개념상 2가지로 나뉩니다:

| 구분 | 위치 | 역할 | 지정 방법 |
|---|---|---|---|
| **활성 루트** | `~/.claude/` (= `C:\Users\<나>\.claude`) | Claude Code가 **모든 프로젝트에서 자동으로 읽는** 곳. 여기 `skills/`·`agents/`·`commands/`가 있으면 어느 폴더서든 발동 | **지정 불필요 — 자동.** 여기에 설치만 하면 됨 |
| **소스(마스터) 루트** | 프로젝트 **밖** 안정적 위치 (git 저장소 권장) | 편집·버전관리·월간 갱신하는 원본 | 자유. 단 **특정 프로젝트 안에 두지 말 것** |

- ✅ 지금 이 PC는 **활성 루트(`~/.claude/`)에 설치 완료** → 재시작하면 모든 폴더에서 발동.
- ⚠️ 현재 소스 마스터가 `D:\cashflow\pjt0\data-product-studio`(pjt0 프로젝트 안)에 있습니다. 여러 프로젝트/팀이 공유하려면 **프로젝트 밖 안정 위치**(예: `C:\Users\<나>\.claude\plugins-src\data-product-studio` 또는 사내 git)로 옮기고 거기서 관리하는 것을 권장.
- 특정 프로젝트에서만 쓰려면 그 프로젝트의 `<프로젝트>\.claude\`에 설치(전역 대신).

## 설치 & 발동 확인
- **가장 쉬운 설치(권장)**: 소스 폴더에서 `powershell -ExecutionPolicy Bypass -File .\install.ps1` 실행 → `~/.claude`로 복사 + 훅 병합 자동.
- 수동 설치·프로젝트별·마켓플레이스 방법은 [INSTALL.md](INSTALL.md) 참고.
- 설치 후 **Claude Code 재시작** → `/` 입력 시 `init-project` 등이 보이면 완료.

## 🖥️ 다른 PC에서 첫 시작 (부트스트랩)

새 PC엔 아무것도 없으니 **다짜고짜 `/init-project`는 안 됩니다. 1회 설치가 먼저**입니다.

```
1) 소스 가져오기: git clone <저장소>   (또는 이 폴더를 복사/USB)
2) 설치: 그 폴더에서  powershell -ExecutionPolicy Bypass -File .\install.ps1
3) Python 설치 확인 (스크립트·훅 실행에 필요): python --version
4) Claude Code 재시작
5) 끝! 이제 아무 프로젝트 폴더에서나:
     /init-project   (신규)   또는   /adopt-project  (기존)
```
> **팀 배포 권장 = git + 마켓플레이스**: 소스를 사내 git에 두면, 각 PC는 `/plugin marketplace add <git>` → `/plugin install`, 월간 갱신은 버전 bump로 자동 전파(플러그인 방식은 `${CLAUDE_PLUGIN_ROOT}`도 자동 해결). 상세 [INSTALL.md](INSTALL.md).

## 사용 — 신규든 기존이든
```
/init-project     # 신규 프로젝트: 인터뷰 → CLAUDE.md·skill.md·docs 골격 생성
/adopt-project    # 기존/진행 중 프로젝트: 스캔 → 보강 인터뷰 → 기존 보존하며 도입
/next-stage       # 다음 단계(설계→구현→테스트→모니터링→인수인계)
/refresh-skills   # 월 1회 최신 트렌드 반영 + 버전 bump
```

## 산출물 도구 원칙 (무료 우선)
문서 허브 = **Confluence**, 아키텍처 = **draw.io**, ERD/UML = **Mermaid/PlantUML**, e2e = **Playwright**. 자세한 매핑은 `skills/project-interview/reference/tool-recommendations-ko.md`.

## 설계 근거
`background/research/claude-skills-트렌드-리서치-2026-07.md`, `background/design/스킬셋-전체설계도.md` (deep-research 검증 25/25).

## 갱신
월 1회 로컬/수동으로 최신 트렌드를 반영하고 `plugin.json`의 `version`을 올립니다.
