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
- 상세 행동 규범은 **`orchestrator` 스킬**을 따르세요(Intake→Plan→Delegate→Track→Gate→Report).
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

    print("=== data-product-studio 골격 생성 결과 ===")
    for r in results:
        print(r)
    print(f"\n완료. 프로젝트 루트: {root}")
    print("다음: /next-stage 로 2단계 설계 진행")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
