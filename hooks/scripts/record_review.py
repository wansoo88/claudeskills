#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
record_review.py — SubagentStop 훅(matcher: code-reviewer|security-reviewer).
리뷰 서브에이전트가 끝나면 리뷰 원장(.review-state.json)에 '실행됨' 흔적을 남긴다(백스톱).

역할: code-review/security-review 스킬이 pass/fail을 기록하는 게 정상 경로이지만,
누군가 스킬 없이 리뷰어만 돌려도 최소한 '실행됨(ran)' 기록이 남도록 보장.
차단하지 않는다(항상 exit 0).

원장 경로: <cwd>/docs/03-build/.review-state.json
"""
import json
import sys
from datetime import datetime
from pathlib import Path

FIELDS = ("agent_type", "subagent_type", "agent", "agent_name", "name", "matcher")
KIND = {
    "code-reviewer": "code_review",
    "security-reviewer": "security_review",
}


def detect_kind(data):
    for f in FIELDS:
        v = str(data.get(f, "")).lower()
        for key, mapped in KIND.items():
            if key in v:
                return mapped
    # transcript/prompt 안에 이름이 들어오는 경우 대비
    blob = json.dumps(data, ensure_ascii=False).lower()
    for key, mapped in KIND.items():
        if key in blob:
            return mapped
    return None


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    kind = detect_kind(data)
    if not kind:
        return 0

    cwd = Path(data.get("cwd", "."))
    ledger = cwd / "docs" / "03-build" / ".review-state.json"
    state = {}
    if ledger.exists():
        try:
            state = json.loads(ledger.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}
    # 스킬이 이미 pass/fail을 기록했다면 건드리지 않음. 없을 때만 'ran' 백스톱.
    if kind not in state or not state[kind].get("status"):
        state[kind] = {"status": "ran", "at": datetime.now().isoformat(timespec="seconds"),
                       "note": "훅 백스톱 기록(스킬이 pass/fail 미기록)"}
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
