#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scaffold_project.py — 인터뷰 브리프(project-brief.json)로부터
프로젝트 루트에 CLAUDE.md · skill.md · docs/ 6단계 골격 · requirements.md 를 생성한다.

사용:
    python scaffold_project.py --brief docs/01-interview/project-brief.json [--root .] [--force]

원칙:
- 기존 파일은 덮어쓰지 않는다(--force 없으면 건너뜀). 사용자 작업 보호.
- 모든 파일은 UTF-8. 크로스플랫폼(Windows/macOS/Linux).
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

# ---- 라벨 매핑 (코드값 -> 한국어) -------------------------------------------
LABELS = {
    "product_type": {
        "dashboard": "대시보드/리포트", "data-api": "데이터 API",
        "ml-model": "분석/예측 모델", "pipeline": "데이터 파이프라인",
        "internal-tool": "내부 업무 툴",
    },
    "data_scale": {"small": "소규모(~수만)", "medium": "중규모(수십만~수백만)",
                   "large": "대규모(수천만+)", "unknown": "미정"},
    "refresh_cycle": {"realtime": "실시간/준실시간", "hourly": "시간별",
                      "daily": "일 배치", "weekly": "주/월 배치"},
    "sensitive_data": {"none": "없음", "pii": "개인정보 포함",
                       "payment": "결제/금융 포함", "confidential": "사내 기밀",
                       "unknown": "확인 필요"},
    "cloud": {"aws": "AWS", "onprem": "온프레/사내", "other": "기타 클라우드", "undecided": "미정"},
    "database": {"postgresql": "PostgreSQL", "mysql": "MySQL/MariaDB",
                 "aurora": "Aurora", "existing": "기존 사내 DB", "undecided": "미정"},
    "frontend": {"react": "React 반응형 웹", "admin-only": "관리자 화면만",
                 "none": "화면 없음", "undecided": "미정"},
    "backend": {"python-fastapi": "Python/FastAPI", "nodejs": "Node.js",
                "java-spring": "Java/Spring", "undecided": "미정"},
    "scale_users": {"few": "소수(팀 내)", "hundreds": "수십~수백",
                    "thousands": "수천+", "unknown": "미정"},
    "timeline": {"1m": "1개월 내 MVP", "2-3m": "2~3개월", "6m": "반기", "undecided": "미정"},
    "team": {"solo": "나 혼자", "small-team": "나 + 팀원 소수",
             "full-team": "팀 전체", "handover": "외부 인수인계 예정"},
}

STAGES = [
    ("01-interview", "1. 인터뷰", ["requirements.md", "project-brief.json"]),
    ("02-design", "2. 설계", ["architecture.drawio", "erd.md", "api-spec.md", "security.md"]),
    ("03-build", "3. 구현", ["implementation-plan.md", "code-review-log.md", "security-review-log.md"]),
    ("04-test", "4. 테스트", ["test-plan.md", "test-report.md"]),
    ("05-monitoring", "5. 모니터링", ["monitoring-plan.md"]),
    ("06-handover", "6. 최종점검", ["handover.md"]),
]


def L(brief, key):
    """브리프 값을 한국어 라벨로."""
    val = brief.get(key, "undecided")
    if isinstance(val, list):
        return ", ".join(LABELS.get(key, {}).get(v, v) for v in val) or "미정"
    return LABELS.get(key, {}).get(val, val if val else "미정")


def write_file(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return f"  건너뜀(이미 존재): {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"  생성: {path}"


def write_root_doc(path: Path, content: str, args) -> str:
    """루트 핵심 문서(CLAUDE.md/skill.md) 쓰기. adopt 모드에서 기존이 있으면
    덮어쓰지 않고 <name>.generated.md 로 남겨 병합하게 한다."""
    if path.exists() and not args.force:
        if getattr(args, "adopt", False):
            alt = path.with_name(path.stem + ".generated" + path.suffix)
            alt.write_text(content, encoding="utf-8")
            return f"  기존 보존: {path.name} → 생성본 {alt.name} (검토 후 병합하세요)"
        return f"  건너뜀(이미 존재): {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"  생성: {path}"


def pipeline_checklist(brief) -> str:
    """신규/기존(adopt) 모드와 current_stage에 맞춰 6단계 현황 체크리스트 생성."""
    stages = ["인터뷰", "설계 (아키텍처·ERD·보안)",
              "구현 (**code-review·security-review 무조건**)",
              "테스트 (단위·e2e)", "모니터링", "최종점검(인수인계)"]
    try:
        cur = int(brief.get("current_stage", 1) or 1)
    except (TypeError, ValueError):
        cur = 1
    cur = max(1, min(cur, 6))
    mode = brief.get("mode", "new")
    out = ["## 6단계 파이프라인 현황"]
    if mode == "adopt":
        out.append(f"> 기존 프로젝트 도입(adopt): 1~{max(cur-1,1)}단계는 기존 진척으로 간주(검증 필요), "
                   f"**{cur}단계부터 진행 권장**.")
    for i, nm in enumerate(stages, 1):
        if mode == "adopt":
            if i < cur:
                mark, note = "[x]", " — 기존 반영(검증 필요)"
            elif i == cur:
                mark, note = "[ ]", " ← 여기서 시작 권장"
            else:
                mark, note = "[ ]", ""
        else:  # new
            mark, note = ("[x]", " — 완료 (이 파일 생성)") if i == 1 else ("[ ]", "")
        out.append(f"- {mark} {i}. {nm}{note}")
    return "\n".join(out)


def org_and_ui_md() -> str:
    """조직 맥락 + UI/UX 규약. 모든 프로젝트 CLAUDE.md에 삽입한다.

    조회성 표(컬러 hex·마크 스펙·차트 선택 매트릭스)는 여기 넣지 않는다 —
    CLAUDE.md는 매 요청 컨텍스트에 상주하므로 `serveone-bi-ui` 스킬에 둔다.
    """
    return """## 조직 맥락

서브원(ServeOne) CTO 조직 산하 Data/AI 팀이 소유하는 코드베이스다. 전략구매·경영기획·영업·IT 조직과 협업한다.

- 의사소통은 **한국어** 기본, 기술 용어는 영어 그대로. **커밋 메시지·코드 주석·변수명은 영어, UI 문구와 문서는 한국어.**
- 사용자는 일반 소비자가 아니라 **하루 종일 같은 화면을 보는 사내 현업 담당자**다. 온보딩 친화성보다 **스캔 속도와 정보 밀도**를 우선한다.
- 의사결정 계층이 셋이고 화면 설계가 달라진다: **현업 담당자**(품목·거래처 행 단위 / 예외 탐지) · **팀장**(품목군·조직 집계 / 추세와 편차) · **경영층**(전사·사업부 / 단일 지표 + 기준선).

### 도메인 용어 — 임의로 번역·풀어쓰지 않는다
**전가율**(매입가 인상분이 매출가에 반영된 비율, 핵심 수익성 지표) · **GP Impact**(전가 실패의 매출총이익 영향액) · **매입가 반영억제** · **순액 조정** · **직송/무재고/센터/VMI**(배송 유형, P/O 연결과 재고 소유 주체가 다름).
**매입가와 매출원가는 서로 다른 개념이다. 화면 레이블에서 혼용 금지.**
**CI**는 서브원 코퍼레이트 아이덴티티 — 데이터 컬러와 구분한다.

> 용어 정의 전문·사내 플랫폼(SSP·S-MRO·G-lab)·미확정 링크는 `serveone-bi-ui` 스킬의 `reference/serveone-context-ko.md`.

## UI/UX 규약

상세 기준(차트 선택 매트릭스, 컬러 hex, 마크 스펙)은 **`serveone-bi-ui` 스킬**에 있다.
아래는 **스킬 로드 여부와 무관하게 항상 적용되는 제약**이다.

### 화면을 만들기 전에 — 4개 질문
브리프에 없으면 스스로 정하고 사용자에게 명시한 뒤 진행한다.
1. 이 화면이 답하는 **단일 질문**은 무엇인가. 두 개면 화면을 두 개로 나눈다.
2. 의사결정 주체는 위 세 계층 중 누구인가.
3. 비교 **기준선**은 무엇인가 — 목표 / 전월 / 전년동기 / 임계값.
4. 이 화면을 보고 취할 수 있는 **행동**은 무엇인가. 없으면 그 지표를 뺀다.

### 절대 규칙
- **기준선 없는 절대값 금지.** 모든 지표에 델타·목표 대비·추세 중 하나가 붙는다.
- **이중 y축 금지.** 스케일이 둘이면 차트를 둘로 쪼개거나 지수화한다.
- **색은 의미를 인코딩한다. 순서를 인코딩하지 않는다.** 시리즈 8개 초과 시 색을 늘리지 말고 "기타"로 접거나 small multiples로 분리한다. Status 색(정상/주의/경고/위험)은 예약색 — 일반 시리즈로 재사용 금지.
- **색만으로 상태를 표현하지 않는다.** 색 + 아이콘 또는 색 + 레이블.
- **모든 숫자에 `font-variant-numeric: tabular-nums`.**
- **데이터 타임스탬프를 노출한다.** `2026-08-18 03:10 KST` 형식.
- **손익 방향은 레이블로 명시한다.** 한국 사용자는 적색을 상승, 청색을 하락으로 읽는 관례가 있으므로 색만으로 방향을 전달하지 않고 "미달/초과" 같은 문구를 병기한다.
- **CI 컬러는 크롬(헤더·네비·브랜드)에만.** 데이터 컬러로 쓰지 않는다 — "브랜드 색 = 그 지표"라는 잘못된 의미가 생긴다.

### 프론트 스택 · 경계
```
Next.js (App Router) + TypeScript + Tailwind + shadcn/ui
차트: shadcn/ui charts(Recharts) 기본 → 커스텀은 Recharts 직접
      heatmap/treemap/sankey/geo·10만 포인트+ 는 ECharts (반드시 dynamic, ssr:false)
Tremor는 의존성으로 추가하지 않는다 — 필요한 컴포넌트만 copy-paste (토큰 이중화 방지)
```
- 데이터 조회·집계는 **Server Component에서 끝낸다.** Client Component에는 직렬화된 결과와 차트만 내린다.
- `'use client'` 경계는 차트·인터랙션 컴포넌트 파일 최상단에만. 페이지는 서버로 유지한다.
- DB(Redshift 등) 쿼리를 클라이언트에서 직접 호출하지 않는다. 서버 라우트 또는 Data MCP 경유.
- 대시보드 grain은 쿼리 레벨에서 확정한다. 클라이언트에서 재집계하지 않는다.

### 타이포그래피 · 밀도 · 문구
- 본문 폰트 **Pretendard Variable**(Inter는 한글 폴백으로 자간이 깨지므로 금지). 가중치는 **400·500만**. 최소 11px. 테이블 행 높이 32~36px.
- 테두리는 `0.5px solid` hairline. 카드 drop shadow 금지. 문장형 대소문자(Title Case·전체 대문자 금지).
- 레이블은 시스템 용어가 아니라 사용자가 쓰는 말로. "Total Revenue"가 아니라 "매출액", "Margin Rate"가 아니라 "전가율".
- 에러는 사과하지 않는다 — 무엇이 잘못됐고 무엇을 하면 되는지 한 문장. 빈 화면은 "데이터 없음"이 아니라 다음 행동을 안내. "성공적으로/간단히/쉽게" 같은 부사를 뺀다.

### 안티패턴 — 발견 즉시 수정
같은 배경색·같은 크기 KPI 카드 4개 나열 / 구성비 도넛 차트(→가로 누적 막대·테이블) / 퍼플·바이올렛 강조색·그라디언트·glow·blur / 델타 없는 절대값·기준선 없는 추세선 / 이모지 아이콘(→Lucide SVG) / 로딩 중 레이아웃 시프트(→skeleton으로 자리 선점).

### UI 코드리뷰 게이트 — **12항목 전부 fail 사유**
화면·차트 변경 PR은 아래를 **모두** 통과해야 code-review가 pass된다(미충족 시 훅이 커밋 차단).

- [ ] 화면의 단일 질문이 제목 또는 첫 문장에 드러남
- [ ] 모든 지표에 기준선이 있음
- [ ] 이중축 차트 없음
- [ ] 색이 순서가 아닌 의미를 인코딩 (Status 예약색 재사용 없음)
- [ ] 상태 표현이 색 + 아이콘/레이블 조합
- [ ] 숫자에 tabular-nums 적용
- [ ] 데이터 타임스탬프 노출
- [ ] 라이트·다크 모드 양쪽에서 모든 텍스트 판독 가능
- [ ] 키보드 조작 가능, 포커스 링 표시
- [ ] `prefers-reduced-motion` 존중
- [ ] 1280 / 1440 / 1920 폭에서 테이블 미파손
- [ ] ECharts가 dynamic(ssr:false)로 감싸짐 + 차트 요소에 `role="img"` + `aria-label`

"""


def claude_md(brief) -> str:
    name = brief.get("project_name", "(이름 미정)")
    mode = brief.get("mode", "new")
    mode_note = ("> 도입 방식: **기존 프로젝트에 스킬셋 도입(adopt)** — 기존 파일은 보존하고 없는 것만 추가했습니다.\n"
                 if mode == "adopt" else
                 "> 도입 방식: **신규 프로젝트** — 인터뷰 기반으로 골격을 생성했습니다.\n")
    assumed = brief.get("_assumed", [])
    assumed_note = ""
    if assumed:
        assumed_note = "\n> ⚠️ 인터뷰에서 확정되지 않아 가정한 값: " + ", ".join(assumed) + " — 확정 시 갱신하세요.\n"
    return f"""# CLAUDE.md — {name}

> 이 파일은 data-product-studio 스킬셋이 인터뷰(1단계) 기반으로 자동 생성했습니다.
> Claude Code가 매 세션 자동으로 읽습니다. 프로젝트의 단일 진실 소스로 유지하세요.
{mode_note}{assumed_note}
## 운영 모델 — PM/PMO 오케스트레이션
당신(어시스턴트)은 이 프로젝트의 **PM/PMO 오케스트레이터**입니다. herdr 워크스페이스에서 **사람이 질의하는 유일한 상대**이며, 전문 역할(subagent)들을 지휘합니다. **사람은 subagent와 직접 대화하지 않습니다** — 당신이 위임하고 종합해 보고합니다.
- 사람 요청 → 당신이 **계획** → subagent에 **이름으로 위임**(자동위임 불안정) → 결과를 **한국어로 요약 보고** → 결정은 **AskUserQuestion**.
- 상세 행동 규범은 **`orchestrator` 스킬**을 따르세요(Sweep→Intake→Plan→Delegate→Track→Gate→Report).
- **역할 계층(3계층)**: **super agent=PM**(당신, 총괄·지시/감독·단일 창구) · **sub super agent=PL**(병목 시 증설, PM 의사결정 보조 + subagent 미진행 관리 + 비민감 allow는 판단하 허용·민감건은 팀장 컨펌) · **subagent**(위임 실행). PM·PL은 트랙을 나눠 소유하고 상대 트랙은 디컨플릭트 후 접근. 상세는 `orchestrator` 스킬 §역할 계층.
- **팔로우업 무손실**: 모든 지시(사람↔나, 나↔subagent, 나→사람)를 `docs/00-orchestration/followups.md` 원장에 등재하고, 검증된 완료 전까지 닫지 않습니다. 매 보고 직전 미완료분을 훑어(sweep) 놓친 게 없는지 확인합니다.
- 진행 상태는 이 파일과 `skill.md`에 항상 최신으로 유지.

## 프로젝트 개요
- **무엇을**: {L(brief,'product_type')}
- **누가 씀**: {brief.get('primary_users','미정')}
- **핵심 문제**: {brief.get('core_problem','미정')}
- **성공 기준**: {brief.get('success_metrics','미정')}

## 기술 스택
| 항목 | 선택 |
|---|---|
| 클라우드 | {L(brief,'cloud')} |
| DB | {L(brief,'database')} |
| 프론트엔드 | {L(brief,'frontend')} |
| 백엔드 | {L(brief,'backend')} {'(Docker)' if brief.get('docker') else ''} |
| 데이터 소스 | {L(brief,'data_sources')} |
| 데이터 규모 | {L(brief,'data_scale')} / 갱신 {L(brief,'refresh_cycle')} |

## 위임 대상 역할(subagent) — PM/PMO가 지휘
| 단계 | 위임할 역할 |
|---|---|
| 인터뷰/기획 | service-strategist |
| 설계 | infra-architect · software-architect · db-architect |
| 구현 | software-architect → frontend-react / backend-docker |
| 리뷰(필수) | code-reviewer · security-reviewer |
| 테스트 | qa-engineer |
> 오케스트레이터가 위 역할을 **이름으로 명시 호출**해 위임(자동위임 불안정). 사람은 이들과 직접 대화하지 않음.

{pipeline_checklist(brief)}

{org_and_ui_md()}
## 산출물 저장 원칙
- 문서 허브: **Confluence** (doc_store={brief.get('doc_store','confluence')})
- 아키텍처: **draw.io**, ERD/UML: **Mermaid/PlantUML**, e2e: **Playwright** — 무료 우선.
- 외부(Confluence 등) 업로드 전 항상 사용자 확인.

## 제약 / 보안
- 사용자 규모: {L(brief,'scale_users')} · 일정: {L(brief,'timeline')} · 팀: {L(brief,'team')}
- 민감정보: {L(brief,'sensitive_data')}
- 보안 요구: {brief.get('security_requirements','미정')}

## 진행 방식 — 가이드 모드
각 단계는 **끝나면 요약 + 확인 후 다음 단계로 이어간다**(멈춤 지점 유지):
1. 해당 단계 작업 수행(서브에이전트는 이름으로 명시 호출).
2. 산출물을 3~5줄 한국어로 요약.
3. AskUserQuestion으로 묻는다: **"다음 단계(N: 이름)로 갈까요?"** [예 / 이번 단계 수정 / 여기서 멈춤].
4. **예** → 다음 단계 자동 진행. **수정** → 이번 단계 보완. **멈춤** → skill.md 갱신 후 종료.
5. ⚠️ **3단계 리뷰 게이트는 하드 스톱**: code-review·security-review가 모두 passed 되기 전에는 다음으로 못 넘어간다(훅이 커밋도 차단).
> 사용자가 "쭉 진행"을 명시하면 소프트 확인은 줄이되, 3단계 리뷰 게이트는 항상 지킨다.

## 규칙
- 모든 사용자 대면 소통은 **한국어**, 짧고 명확하게.
- 진행은 `/next-stage`(가이드 모드로 다음 단계) 또는 해당 단계 스킬 호출.
- **스킬 스크립트 경로**: 플러그인 설치면 `${{CLAUDE_PLUGIN_ROOT}}/skills/<스킬>/scripts/...`, 전역(복사) 설치면 `~/.claude/skills/<스킬>/scripts/...` 를 절대경로로 실행. (`${{CLAUDE_PLUGIN_ROOT}}`가 안 잡히면 후자)

---
*생성일: {brief.get('created', str(date.today()))} · data-product-studio v0.1*
"""


def skill_md(brief) -> str:
    name = brief.get("project_name", "(이름 미정)")
    return f"""# skill.md — {name} 활성 스킬

> 이 프로젝트에서 켜진 data-product-studio 스킬과 상태. 단계 진행 시 갱신됩니다.
> **운영 모델**: 사람은 **PM/PMO 오케스트레이터**(`orchestrator` 스킬)에게만 질의. 오케스트레이터가 아래 스킬/역할을 지휘하고 subagent에 위임.

| 스킬 | 단계 | 상태 |
|---|---|---|
| **orchestrator (PM/PMO)** | 총괄 | ▶ 상시 |
| **serveone-bi-ui** | UI 규약 | ▶ 상시 (화면·차트 작업 시) |
| project-interview | 1 인터뷰 | ✅ 완료 |
| architecture-design | 2 설계 | ⬜ 대기 |
| db-modeling | 2 설계 | ⬜ 대기 |
| security-design | 2 설계 | ⬜ 대기 |
| implementation-plan | 3 구현 | ⬜ 대기 |
| code-review | 3 구현 | ⬜ 필수 게이트 |
| security-review | 3 구현 | ⬜ 필수 게이트 |
| testing-unit-e2e | 4 테스트 | ⬜ 대기 |
| monitoring-setup | 5 모니터링 | ⬜ 대기 |
| handover-check | 6 최종점검 | ⬜ 대기 |

## 프로젝트 설정
- 문서 허브: {brief.get('doc_store','confluence')}
- 대상 스택: {L(brief,'frontend')} / {L(brief,'backend')} / {L(brief,'database')} @ {L(brief,'cloud')}

*생성일: {brief.get('created', str(date.today()))}*
"""


def requirements_md(brief) -> str:
    name = brief.get("project_name", "(이름 미정)")
    return f"""# 요구사항 정의서 — {name}

> 1단계 인터뷰 산출물. 2단계 설계의 입력.

## 1. 서비스 정의
- 유형: {L(brief,'product_type')}
- 주 사용자: {brief.get('primary_users','미정')}
- 해결할 문제: {brief.get('core_problem','미정')}
- 성공 기준(KPI): {brief.get('success_metrics','미정')}

## 2. 데이터 요구사항
- 소스: {L(brief,'data_sources')}
- 규모: {L(brief,'data_scale')}
- 갱신 주기: {L(brief,'refresh_cycle')}
- 민감정보: {L(brief,'sensitive_data')}

## 3. 기술 요구사항
- 클라우드: {L(brief,'cloud')}
- DB: {L(brief,'database')}
- 프론트엔드: {L(brief,'frontend')}
- 백엔드: {L(brief,'backend')} {'(Docker 기반)' if brief.get('docker') else ''}

## 4. 운영 & 제약
- 사용자/동시접속 규모: {L(brief,'scale_users')}
- 보안·규정: {brief.get('security_requirements','미정')}
- 일정: {L(brief,'timeline')}
- 팀/인수인계: {L(brief,'team')}

## 5. 다음 단계
2단계 설계에서 위 요구사항을 근거로 AWS 아키텍처(draw.io)·ERD·보안설계를 작성한다.

---
*생성일: {brief.get('created', str(date.today()))}*
"""


def followups_md(brief) -> str:
    """PM/PMO 팔로우업 원장 초안(지시 무손실 추적)."""
    today = brief.get("created", str(date.today()))
    return (
        "# 팔로우업 원장 (Follow-up Ledger)\n"
        "> 규칙: 모든 지시(사람↔나, 나↔subagent, 나→사람)를 등재. `done` 외 항목은 매 보고에서 다시 훑는다(sweep).\n"
        "> 상태값: open(진행/대기) · blocked(막힘) · waiting-human(사람 확인 대기) · done(검증 완료).\n"
        "> 상세 규범은 `orchestrator` 스킬 §팔로우업 원장 참조.\n\n"
        "| ID | 등재일 | 요청자→담당 | 내용 | 기대 산출물 | 상태 | 기한 | 최근확인/비고 |\n"
        "|----|--------|-------------|------|-------------|------|------|----------------|\n"
        f"| F1 | {today} | 팀장→pm | (예시) 프로젝트 킥오프 | 계획 요약 | done | - | 삭제하고 실제 항목으로 |\n"
    )


def placeholder(stage_title, filename) -> str:
    return f"""# {filename} — {stage_title}

> data-product-studio 골격. 이 단계 스킬 실행 시 채워집니다.

(아직 작성 전)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True, help="project-brief.json 경로")
    ap.add_argument("--root", default=".", help="프로젝트 루트 (기본: 현재 폴더)")
    ap.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
    ap.add_argument("--adopt", action="store_true", help="기존 프로젝트 도입 모드(기존 파일 보존, 없는 것만 추가)")
    ap.add_argument("--stage", type=int, default=None, help="진행 시작 단계(1-6). adopt 시 유용")
    args = ap.parse_args()

    # Windows 콘솔 등에서 한글 깨짐 방지 (실패해도 무시)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    root = Path(args.root).resolve()
    brief_path = Path(args.brief)
    if not brief_path.is_absolute():
        brief_path = root / brief_path

    if not brief_path.exists():
        print(f"[오류] 브리프 파일 없음: {brief_path}", file=sys.stderr)
        return 1
    try:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}", file=sys.stderr)
        return 1

    brief.setdefault("created", str(date.today()))
    # 모드/진행단계: CLI 인자가 브리프 값을 덮어씀(명시 우선)
    if args.adopt:
        brief["mode"] = "adopt"
    brief.setdefault("mode", "new")
    if args.stage is not None:
        brief["current_stage"] = args.stage
    brief.setdefault("current_stage", 1)
    results = []

    # 루트 문서 (adopt 모드는 기존 보존 + .generated 로 병합 유도)
    results.append(write_root_doc(root / "CLAUDE.md", claude_md(brief), args))
    results.append(write_root_doc(root / "skill.md", skill_md(brief), args))

    # docs 골격
    for folder, title, files in STAGES:
        for fn in files:
            if fn == "project-brief.json":
                continue  # 이미 존재
            if folder == "01-interview" and fn == "requirements.md":
                content = requirements_md(brief)
            else:
                content = placeholder(title, fn)
            results.append(write_file(root / "docs" / folder / fn, content, args.force))

    # PM/PMO 팔로우업 원장(지시 무손실) — 6단계 밖 상시 산출물
    results.append(write_file(root / "docs" / "00-orchestration" / "followups.md",
                              followups_md(brief), args.force))

    print("=== data-product-studio 골격 생성 결과 ===")
    for r in results:
        print(r)
    print(f"\n완료. 프로젝트 루트: {root}")
    print("다음: /next-stage 로 2단계 설계 진행")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
