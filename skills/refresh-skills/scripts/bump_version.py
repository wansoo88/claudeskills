#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bump_version.py — 월간 갱신 시 plugin.json의 semver를 올리고 CHANGELOG.md에 기록.

사용:
    python bump_version.py [--level patch|minor|major] [--note "변경 요약"] [--date YYYY-MM-DD]
    (기본 level=minor: 월간 트렌드 반영은 보통 기능 갱신)

동작: Claude Code는 plugin.json의 version이 바뀔 때만 사용자에게 업데이트를 전달하므로,
월 1회 이 스크립트로 버전을 올리면 팀원 환경에 갱신이 반영된다.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

# 스크립트 위치 기준으로 플러그인 루트(.claude-plugin/plugin.json) 추적
PLUGIN_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_JSON = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CHANGELOG = PLUGIN_ROOT / "CHANGELOG.md"


def bump(version, level):
    parts = version.split("-")[0].split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"semver 형식 아님: {version}")
    major, minor, patch = (int(p) for p in parts)
    if level == "major":
        major, minor, patch = major + 1, 0, 0
    elif level == "patch":
        patch += 1
    else:  # minor
        minor, patch = minor + 1, 0
    return f"{major}.{minor}.{patch}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", choices=["patch", "minor", "major"], default="minor")
    ap.add_argument("--note", default="월간 트렌드 반영 갱신")
    ap.add_argument("--date", default=None, help="기록 날짜(기본: 오늘)")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if not PLUGIN_JSON.exists():
        print(f"[오류] plugin.json 없음: {PLUGIN_JSON}", file=sys.stderr)
        return 1
    data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    old = data.get("version", "0.0.0")
    try:
        new = bump(old, args.level)
    except ValueError as e:
        print(f"[오류] {e}", file=sys.stderr)
        return 1
    data["version"] = new
    PLUGIN_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    when = args.date or str(date.today())
    entry = f"## {new} — {when}\n- {args.note}\n\n"
    prev = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else "# CHANGELOG\n\n"
    # 헤더 다음에 최신 항목 삽입
    if prev.startswith("# CHANGELOG"):
        head, _, rest = prev.partition("\n\n")
        CHANGELOG.write_text(f"{head}\n\n{entry}{rest}", encoding="utf-8")
    else:
        CHANGELOG.write_text(f"# CHANGELOG\n\n{entry}{prev}", encoding="utf-8")

    print(f"[버전] {old} -> {new} (level={args.level})")
    print(f"[기록] {CHANGELOG.name}에 항목 추가")
    print("팀원 Claude Code가 다음 동기화 시 이 버전을 새 업데이트로 인식합니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
