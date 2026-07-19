#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_hooks.py — data-product-studio 리뷰 게이트 훅을 ~/.claude/settings.json에 병합.
기존 설정 보존, 멱등(중복 추가 안 함), 최초 1회 백업(settings.json.dps-backup).
install.ps1이 호출한다. 어떤 사용자/PC에서도 동작하도록 경로는 홈 기준으로 계산.
"""
import json
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SETTINGS = os.path.expanduser("~/.claude/settings.json")
BACKUP = SETTINGS + ".dps-backup"
HOOKS_DIR = os.path.expanduser("~/.claude/data-product-studio/hooks/scripts").replace("\\", "/")


def cmd(name):
    return f'python "{HOOKS_DIR}/{name}"'


def main():
    if not os.path.exists(SETTINGS):
        # settings.json이 없으면 최소 골격 생성
        data = {}
    else:
        with open(SETTINGS, encoding="utf-8") as f:
            data = json.load(f)
        if not os.path.exists(BACKUP):
            shutil.copy(SETTINGS, BACKUP)

    H = data.setdefault("hooks", {})

    def has_cmd(event, needle):
        return any(needle in h.get("command", "")
                   for grp in H.get(event, []) for h in grp.get("hooks", []))

    added = []
    H.setdefault("PreToolUse", [])
    if not has_cmd("PreToolUse", "block_destructive.py"):
        H["PreToolUse"].append({
            "matcher": "Bash",
            "hooks": [
                {"type": "command", "command": cmd("block_destructive.py")},
                {"type": "command", "command": cmd("require_review.py")},
            ],
        })
        added.append("PreToolUse(block_destructive, require_review)")

    H.setdefault("SubagentStop", [])
    if not has_cmd("SubagentStop", "record_review.py"):
        H["SubagentStop"].append({
            "matcher": "code-reviewer|security-reviewer",
            "hooks": [{"type": "command", "command": cmd("record_review.py")}],
        })
        added.append("SubagentStop(record_review)")

    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if added:
        print("훅 병합 완료:", ", ".join(added))
    else:
        print("훅 이미 설치됨(변경 없음).")
    print("현재 hooks 이벤트:", list(H.keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
