---
name: project-adopt
description: 이미 진행 중인(중간) 기존 프로젝트에 이 스킬셋을 도입할 때 사용한다. 사용자가 /adopt-project를 실행하거나 "기존 프로젝트에 적용/도입/온보딩"을 요청하면 발동. 기존 코드를 스캔해 스택·진행단계를 추정하고, 짧은 보강 인터뷰 후 기존 파일을 보존하며 CLAUDE.md/skill.md와 없는 산출물만 추가한다.
---

# 기존 프로젝트 도입 (adopt)

목표: **이미 코드가 있는 프로젝트**에 스킬셋을 얹는다. 신규(/init-project)와 달리 **기존 것을 지우지 않고**, 현재 상태를 반영해 파이프라인에 올린다.

## 진행 순서

### 1. 현재 상태 스캔 → 갭 리포트
스캔 스크립트로 스택·단계별 진척·권장 시작 단계를 산출한다:
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/project-adopt/scripts/scan_project.py" \
  --json docs/01-interview/scan-report.json
```
출력된 **갭 리포트**(단계별 있음/부분/없음 + 권장 시작 단계)를 한국어 표로 사용자에게 보여준다.
스크립트가 못 잡는 뉘앙스(코드 품질·문서 최신성)는 직접 파일을 열어 보완한다.

### 2. 보강(gap) 인터뷰 — 짧게
`../project-interview/reference/interview-bank-ko.md`에서 **스캔으로 못 알아낸 항목만** 골라 AskUserQuestion으로 묻는다(신규처럼 전부 묻지 말 것). 특히 서비스 목적·성공기준·민감정보·목표 단계.

### 3. 브리프 작성 (도입 정보 포함)
`docs/01-interview/project-brief.json`에 스캔+인터뷰 결과를 쓰되 다음을 포함:
```json
{ "mode": "adopt", "current_stage": <추정 시작 단계 1-6>, ... }
```
기존 brief가 있으면 병합.

### 4. 골격 도입 (기존 보존)
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/project-interview/scripts/scaffold_project.py" \
  --brief docs/01-interview/project-brief.json --adopt --stage <시작단계>
```
- 기존 파일은 **보존**. `CLAUDE.md`/`skill.md`가 이미 있으면 `*.generated.md`로 생성되니 **검토 후 병합**한다.
- 없는 docs 골격만 추가된다.

### 5. 병합 & 진입점 안내 (가이드 모드)
- `CLAUDE.generated.md`의 스택·역할·현황을 기존 `CLAUDE.md`에 병합(사용자 확인).
- 스캔 리포트의 **권장 시작 단계**를 근거로 어디서 시작할지 제안(예: 코드 있으나 테스트 없음 → 4단계, 리뷰 미도입 → 3단계 리뷰 게이트).
- AskUserQuestion으로 시작 단계를 확정한 뒤 **`/next-stage`의 가이드 루프로 진행**(각 단계 끝 요약+확인, 3단계 리뷰 게이트는 하드 스톱).

## 하지 말 것
- 기존 파일 임의 덮어쓰기(항상 보존·병합). 스캔으로 아는 것을 중복 질문.
- 없는 진척을 "완료"로 표시(추정은 "검증 필요"로 명시).
