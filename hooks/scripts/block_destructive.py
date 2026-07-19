#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
block_destructive.py — PreToolUse(Bash) 훅. 명백히 파괴적인 명령을 실행 전 차단.

Claude Code 계약:
  - stdin 으로 JSON({tool_name, tool_input:{command}, ...}) 수신.
  - 차단하려면 exit code 2 + stderr 메시지(그 내용이 Claude에게 전달됨).
  - 허용은 exit 0.
설계: 오탐을 줄이기 위해 '명백히 위험한' 패턴만 차단. 파싱 실패 시 fail-open(정상 작업 방해 금지).
"""
import json
import re
import sys

# 명백히 파괴적인 패턴(정규식). 필요 시 프로젝트 규약에 맞게 확장.
DANGEROUS = [
    (r"\brm\s+-[a-z]*r[a-z]*f?\b.*\s(/|~|\*|\.|/\*|[A-Za-z]:\\?)(\s|$)", "루트/홈/전체 경로 대상 rm -rf"),
    (r"\brm\s+-[a-z]*f[a-z]*r?\b.*\s(/|~|\*)(\s|$)", "위험한 rm -f 재귀 삭제"),
    (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "포크 밤(fork bomb)"),
    (r"\bmkfs(\.\w+)?\b", "파일시스템 포맷(mkfs)"),
    (r"\bdd\b.*\bof=/dev/(sd|nvme|disk|hd)", "디스크 직접 덮어쓰기(dd of=/dev/...)"),
    (r">\s*/dev/(sd|nvme|disk|hd)", "블록 디바이스 덮어쓰기"),
    (r"\bgit\s+push\b.*(--force|-f)\b.*\b(main|master|origin)\b", "보호 브랜치 강제 푸시"),
    (r"\bchmod\s+-R\s+777\s+/(\s|$)", "루트 권한 777 재귀"),
    (r"\b(curl|wget)\b.*\|\s*(sudo\s+)?(ba)?sh\b", "원격 스크립트 파이프 실행(curl|bash)"),
    (r"\bDROP\s+DATABASE\b", "DROP DATABASE"),
]


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0  # fail-open
    cmd = (data.get("tool_input", {}) or {}).get("command", "") or ""
    if not cmd:
        return 0
    for pattern, why in DANGEROUS:
        if re.search(pattern, cmd, re.IGNORECASE):
            sys.stderr.write(
                f"[차단] 위험한 명령으로 판단되어 실행을 막았습니다: {why}\n"
                f"  명령: {cmd}\n"
                f"  정말 필요하면 사용자가 직접 확인 후 수동 실행하세요.\n"
            )
            return 2  # 차단
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
