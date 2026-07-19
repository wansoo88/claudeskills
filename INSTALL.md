# 설치 & 발동 확인 가이드

> 목표: **신규 프로젝트든, 이미 진행 중인(중간) 프로젝트든** 어디서나 이 스킬셋이 발동되게 하고, 발동됐는지 확인하는 법.

---

## 0. 먼저 개념 — "파일 생성"과 "발동"은 다릅니다

- 지금 `D:\cashflow\pjt0\data-product-studio\`에는 **플러그인 파일**이 있고 스크립트도 검증됐습니다.
- 하지만 Claude Code가 이 스킬을 **인식·발동**하려면 아래 위치 중 하나에 **설치**되어야 합니다.
  - 사용자 전역: `~/.claude/skills`, `~/.claude/agents`, `~/.claude/commands`  ← **모든 프로젝트에서 발동**
  - 프로젝트별: `<프로젝트>/.claude/...`  ← 그 프로젝트에서만
  - 플러그인: 마켓플레이스로 설치(팀 배포)
- **설치 후 Claude Code를 재시작**해야 새 스킬/커맨드/훅을 읽습니다.

---

## 방법 A. 전역 설치 (권장) — 어느 프로젝트에서나 발동

가장 확실하게 "신규/기존 어디서나" 발동시키는 방법. PowerShell에서:

```powershell
$src = "D:\cashflow\pjt0\data-product-studio"
$dst = "$env:USERPROFILE\.claude"
New-Item -ItemType Directory -Force "$dst\skills","$dst\agents","$dst\commands" | Out-Null
Copy-Item "$src\skills\*"   "$dst\skills\"   -Recurse -Force
Copy-Item "$src\agents\*"   "$dst\agents\"   -Recurse -Force
Copy-Item "$src\commands\*" "$dst\commands\" -Recurse -Force
```

그다음 **훅**을 `~/.claude/settings.json`의 `hooks` 키에 **병합**(이미 hooks가 있으면 배열에 추가). 경로는 절대경로:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [
        { "type": "command", "command": "python \"D:/cashflow/pjt0/data-product-studio/hooks/scripts/block_destructive.py\"" },
        { "type": "command", "command": "python \"D:/cashflow/pjt0/data-product-studio/hooks/scripts/require_review.py\"" }
      ]}
    ],
    "SubagentStop": [
      { "matcher": "code-reviewer|security-reviewer", "hooks": [
        { "type": "command", "command": "python \"D:/cashflow/pjt0/data-product-studio/hooks/scripts/record_review.py\"" }
      ]}
    ]
  }
}
```

→ **Claude Code 재시작**. 이제 어떤 폴더에서 열어도 스킬·커맨드가 살아있습니다.

> ⚠️ `settings.json`은 이미 `hooks` 키가 있을 수 있으니 **덮어쓰지 말고 병합**하세요. 복사(copy) 방식은 `${CLAUDE_PLUGIN_ROOT}`가 없으므로 훅 경로를 **절대경로**로 씁니다.

---

## 방법 B. 프로젝트별 설치 — 특정 프로젝트에서만

```powershell
$src = "D:\cashflow\pjt0\data-product-studio"
$dst = "<대상 프로젝트 경로>\.claude"
New-Item -ItemType Directory -Force "$dst\skills","$dst\agents","$dst\commands" | Out-Null
Copy-Item "$src\skills\*" "$dst\skills\" -Recurse -Force
Copy-Item "$src\agents\*" "$dst\agents\" -Recurse -Force
Copy-Item "$src\commands\*" "$dst\commands\" -Recurse -Force
```
훅은 `<프로젝트>\.claude\settings.json`에 위와 동일하게(경로만 맞게). 프로젝트 `.claude`는 git 커밋 시 팀과 공유됩니다.

---

## 방법 C. 로컬 마켓플레이스 — 팀 배포 정석

Claude Code 안에서:
```
/plugin marketplace add D:\cashflow\pjt0\data-product-studio
/plugin install data-product-studio@data-product-studio
```
- `.claude-plugin/marketplace.json`이 이미 준비돼 있습니다.
- 설치되면 커맨드는 `data-product-studio:init-project` 처럼 네임스페이스로 표시되고, `hooks.json`의 `${CLAUDE_PLUGIN_ROOT}` 훅이 그대로 작동합니다.
- 월간 갱신 시 `bump_version.py`로 버전을 올리면 팀원이 업데이트를 받습니다.

---

## 발동됐는지 확인하는 법 ✅

설치 + 재시작 후:

1. **커맨드 확인**: 입력창에 `/` 입력 → `init-project`, `adopt-project`, `next-stage`, `refresh-skills`가 보이면 설치됨.
2. **플러그인 확인**(방법 C): `/plugin` → 설치 목록에 data-product-studio.
3. **스킬 확인**: Claude에게 "지금 사용할 수 있는 스킬 알려줘"라고 물으면 로드된 스킬을 답함.
4. **실제 발동 증거**(가장 확실):
   - 신규 폴더에서 `/init-project` → 인터뷰가 뜨고, 끝나면 그 폴더에 `CLAUDE.md`·`skill.md`·`docs/`가 생김.
   - 그 **`skill.md`가 곧 "이 프로젝트에 어떤 스킬이 켜졌는지"의 기록**입니다.
5. **훅 확인**: 리뷰 없이 `git commit` 시도 → 차단되면 게이트 훅 작동 중.

> 리서치 검증: **자동 발동은 불안정**합니다. 그래서 확실한 트리거는 커맨드(`/init-project`, `/adopt-project`)를 **직접 실행**하는 것입니다.

---

## 신규 vs 기존(중간) 프로젝트 — 어느 쪽이든 발동

| 상황 | 실행 | 동작 |
|---|---|---|
| **신규 프로젝트** | `/init-project` | 4라운드 인터뷰 → `CLAUDE.md`·`skill.md`·`docs/` 골격 생성 |
| **기존/진행 중 프로젝트** | `/adopt-project` | 기존 코드 스캔 → 짧은 보강 인터뷰 → **기존 보존**하며 없는 것만 추가, `CLAUDE.generated.md`로 병합 안내, 시작 단계 제안 |

→ 전역 설치(방법 A)하면 **어느 폴더에서 Claude Code를 열든** 위 두 커맨드로 발동합니다.

---

## 문제 해결
- 커맨드가 안 보임 → 복사 위치/재시작 확인, 파일이 `~/.claude/commands/*.md`에 있는지.
- 훅이 안 걸림 → `settings.json` 병합·JSON 유효성·`python` PATH 확인. 훅은 Bash 도구에서 가장 확실.
- Python 없음 → `python`이 PATH에 있는지(또는 훅/스크립트 명령을 `py`로 교체).
