#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
require_review.py — PreToolUse(Bash) 훅. code-review·security-review 통과 전
'git commit'/'git push'를 차단한다. (사용자 요구: 리뷰 무조건 진행)

Claude Code 계약: 차단은 exit 2 + stderr. 허용은 exit 0.
판단 근거: <cwd>/docs/03-build/.review-state.json 원장.
  - code_review  : status == "passed" 여야 허용.
  - security_review : status == "passed", 또는 사내 시큐어코딩 가이드 v1.0 제9장(예외처리)에
    따른 **승인된 예외**(status == "exception" + 필수 5요건 + 미만료)여야 허용.
  - 그 외(파일 없음/누락/failed/ran) 는 차단.
git 이외 명령은 관여하지 않음(exit 0). 파싱 실패는 fail-open.

예외는 영구 면제가 아니다. expires_on 이 지나면 자동으로 다시 차단된다.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

GATED = re.compile(r"\bgit\s+(commit|push)\b", re.IGNORECASE)
REQUIRED = ("code_review", "security_review")
KO = {"code_review": "코드리뷰", "security_review": "보안리뷰"}
# 가이드 제9장 필수 기재사항 → 원장 필드
EXC_FIELDS = ("target", "reason", "risk", "compensating_controls",
              "remediation_plan", "expires_on", "approved_by")
EXC_KO = {
    "target": "대상(코드 위치)", "reason": "미준수 사유", "risk": "위험평가",
    "compensating_controls": "보완통제", "remediation_plan": "개선계획",
    "expires_on": "유효기간(YYYY-MM-DD)", "approved_by": "승인자",
}


def check_exception(entry):
    """승인된 예외인지 검증. (허용여부, 사유) 반환."""
    exc = entry.get("exception")
    if not isinstance(exc, dict):
        return False, "exception 블록 없음"

    missing = []
    for f in EXC_FIELDS:
        v = exc.get(f)
        if v is None or (isinstance(v, (str, list, tuple)) and len(v) == 0):
            missing.append(EXC_KO[f])
    if missing:
        return False, "필수 기재 누락: " + ", ".join(missing)

    try:
        expires = date.fromisoformat(str(exc["expires_on"]).strip()[:10])
    except ValueError:
        return False, f"유효기간 형식 오류(YYYY-MM-DD 필요): {exc['expires_on']!r}"
    if expires < date.today():
        return False, f"예외 만료됨({expires.isoformat()}) — 조치하거나 재승인 필요"

    return True, f"승인 {exc['approved_by']} / 만료 {expires.isoformat()}"


def main():
    if hasattr(sys.stderr, "reconfigure"):   # 차단 사유(한국어)가 깨지지 않게
        sys.stderr.reconfigure(encoding="utf-8")
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
    notes = []
    for key in REQUIRED:
        entry = state.get(key) or {}
        if not isinstance(entry, dict):
            entry = {}
        status = entry.get("status", "없음")
        if status == "passed":
            continue
        # 예외 경로는 보안리뷰에만 허용 (가이드 제9장은 시큐어코딩 미준수에 대한 예외)
        if key == "security_review" and status == "exception":
            ok, why = check_exception(entry)
            if ok:
                notes.append(f"보안리뷰: 승인된 예외로 통과 ({why})")
                continue
            missing.append(f"{KO[key]}(예외 무효 — {why})")
            continue
        missing.append(f"{KO[key]}({status})")

    if missing:
        sys.stderr.write(
            "[차단] code-review·security-review 통과 후에만 커밋/푸시할 수 있습니다.\n"
            f"  미통과: {', '.join(missing)}\n"
            "  해결: code-review, security-review 스킬(또는 서브에이전트)을 먼저 실행해\n"
            "  docs/03-build/.review-state.json 의 두 항목을 'passed'로 만드세요.\n"
            "  조치가 곤란하면 사내 시큐어코딩 가이드 제9장 예외처리(승인·보완통제·개선계획·만료일)를\n"
            "  거쳐 security_review 를 'exception' 으로 기록하세요. (security-review 스킬 §6)\n"
        )
        return 2

    if notes:
        sys.stderr.write("[주의] " + " / ".join(notes) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
