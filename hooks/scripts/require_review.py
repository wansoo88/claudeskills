#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
require_review.py — PreToolUse(Bash) 훅. code-review·security-review 통과 전
'git commit'/'git push'를 차단한다. (사용자 요구: 리뷰 무조건 진행)

Claude Code 계약: 차단은 exit 2 + stderr. 허용은 exit 0.
판단 근거: <cwd>/docs/03-build/.review-state.json 원장.
  - 두 리뷰(code_review, security_review) 모두 status == "passed" 여야 커밋/푸시 허용.
  - 그 외(파일 없음/누락/failed/ran) 는 차단.
git 이외 명령은 관여하지 않음(exit 0). 파싱 실패는 fail-open.
"""
import json
import re
import sys
from pathlib import Path

GATED = re.compile(r"\bgit\s+(commit|push)\b", re.IGNORECASE)
REQUIRED = ("code_review", "security_review")
KO = {"code_review": "코드리뷰", "security_review": "보안리뷰"}


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    cmd = (data.get("tool_input", {}) or {}).get("command", "") or ""
    if not GATED.search(cmd):
        return 0  # 커밋/푸시가 아니면 관여 안 함

    cwd = Path(data.get("cwd", "."))
    build_dir = cwd / "docs" / "03-build"
    if not build_dir.exists():
        return 0  # data-product-studio 관리 프로젝트가 아니면 게이트 미적용(일반 repo 보호)
    ledger = build_dir / ".review-state.json"
    state = {}
    if ledger.exists():
        try:
            state = json.loads(ledger.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}

    missing = []
    for key in REQUIRED:
        if state.get(key, {}).get("status") != "passed":
            cur = state.get(key, {}).get("status", "없음")
            missing.append(f"{KO[key]}({cur})")

    if missing:
        sys.stderr.write(
            "[차단] code-review·security-review 통과 후에만 커밋/푸시할 수 있습니다.\n"
            f"  미통과: {', '.join(missing)}\n"
            "  해결: code-review, security-review 스킬(또는 서브에이전트)을 먼저 실행해\n"
            "  docs/03-build/.review-state.json 의 두 항목을 'passed'로 만드세요.\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
