#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_project.py — 기존 프로젝트를 스캔해 스택과 단계별 진척(갭 리포트)을 산출.

사용:
    python scan_project.py [--root .] [--json docs/01-interview/scan-report.json]

출력: 사람이 읽는 갭 표(stdout) + (옵션) JSON. project-adopt 스킬이 이걸로
"어느 단계부터 시작할지"를 제안한다. 결정적 검사만 하며, 애매하면 '부분'으로 표시.
"""
import argparse
import json
import sys
from pathlib import Path


def any_exists(root, patterns):
    for p in patterns:
        if list(root.glob(p)):
            return True
    return False


def has_code(root):
    # 설정/문서 제외한 실제 소스 흔적
    return any_exists(root, [
        "src/**/*.py", "src/**/*.ts", "src/**/*.tsx", "src/**/*.js", "src/**/*.jsx",
        "backend/**/*.py", "backend/**/*.js", "app/**/*.py",
        "frontend/**/*.tsx", "frontend/**/*.jsx", "frontend/src/**/*",
        "*.py", "**/main.py", "**/app.py",
    ])


def detect_stack(root):
    stack = {}
    pkg = root / "package.json"
    stack["frontend_react"] = False
    if pkg.exists():
        try:
            txt = pkg.read_text(encoding="utf-8", errors="ignore").lower()
            stack["frontend_react"] = "react" in txt
        except OSError:
            pass
    stack["backend_python"] = any_exists(root, ["requirements.txt", "pyproject.toml", "**/requirements.txt"])
    stack["backend_node"] = pkg.exists()
    stack["docker"] = any_exists(root, ["Dockerfile", "**/Dockerfile", "docker-compose.yml", "compose.yml", "docker-compose.yaml"])
    stack["db"] = any_exists(root, ["**/migrations/**", "**/alembic*", "prisma/**", "**/*.sql", ".env.example"])
    stack["ci"] = any_exists(root, [".github/workflows/*.yml", ".github/workflows/*.yaml", ".gitlab-ci.yml"])
    stack["tests"] = any_exists(root, ["**/test_*.py", "**/*_test.py", "**/*.test.ts", "**/*.test.js", "**/*.spec.ts", "tests/**", "e2e/**", "**/playwright*"])
    return stack


def stage_status(root, stack):
    d = root / "docs"
    s = {}
    # 1 인터뷰
    s[1] = "있음" if (d / "01-interview" / "requirements.md").exists() else "없음"
    # 2 설계
    design = [(d/"02-design"/"architecture.drawio"), (d/"02-design"/"erd.md"), (d/"02-design"/"security.md")]
    design_n = sum(1 for f in design if f.exists()) + (1 if any_exists(root, ["*.drawio", "**/*.drawio"]) else 0)
    s[2] = "있음" if design_n >= 2 else ("부분" if design_n >= 1 else "없음")
    # 3 구현 (+리뷰)
    code = has_code(root)
    plan = (d / "03-build" / "implementation-plan.md").exists()
    review = (d / "03-build" / ".review-state.json").exists()
    if code and plan and review:
        s[3] = "있음"
    elif code:
        s[3] = "부분"  # 코드는 있으나 계획/리뷰 게이트 미흡
    else:
        s[3] = "없음"
    # 4 테스트
    s[4] = "있음" if (stack["tests"] or (d/"04-test"/"test-report.md").exists()) else "없음"
    # 5 모니터링
    s[5] = "있음" if (d/"05-monitoring"/"monitoring-plan.md").exists() else "없음"
    # 6 인수인계
    s[6] = "있음" if (d/"06-handover"/"handover.md").exists() else "없음"
    return s


def recommend(root, stack, s):
    has_claude = (root / "CLAUDE.md").exists()
    review_missing = not (root / "docs" / "03-build" / ".review-state.json").exists()
    notes = []
    if not has_claude:
        notes.append("CLAUDE.md 없음 → 먼저 생성해 AI 컨텍스트 확보(최우선).")
    if has_code(root) and review_missing:
        notes.append("코드는 있으나 리뷰 게이트 미적용 → 3단계 리뷰 게이트부터 적용 권장.")
    # 시작 단계: 첫 '없음/부분'
    start = 6
    for i in range(1, 7):
        if s[i] in ("없음", "부분"):
            start = i
            break
    return start, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    root = Path(args.root).resolve()
    stack = detect_stack(root)
    s = stage_status(root, stack)
    start, notes = recommend(root, stack, s)

    names = {1: "인터뷰", 2: "설계", 3: "구현+리뷰", 4: "테스트", 5: "모니터링", 6: "인수인계"}
    print(f"=== 기존 프로젝트 갭 리포트: {root.name} ===")
    print("[스택 감지]")
    print(f"  React 프론트: {'O' if stack['frontend_react'] else 'X'} | "
          f"Python백엔드: {'O' if stack['backend_python'] else 'X'} | "
          f"Docker: {'O' if stack['docker'] else 'X'} | DB흔적: {'O' if stack['db'] else 'X'} | "
          f"테스트: {'O' if stack['tests'] else 'X'} | CI: {'O' if stack['ci'] else 'X'}")
    print("[단계별 진척]")
    for i in range(1, 7):
        print(f"  {i}. {names[i]:<8} : {s[i]}")
    print(f"[권장 시작 단계] {start}. {names[start]}")
    for n in notes:
        print(f"  - {n}")

    if args.json:
        out = Path(args.json)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(
            {"stack": stack, "stages": s, "recommended_start": start, "notes": notes},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[기록] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
