# Herdr 온보딩 & 셋업 재현 가이드 (Windows)

> 이 문서 하나로 새 PC에서 동일한 herdr + Claude Code 환경을 재현합니다.
> 최종 업데이트: 2026-07-19 · herdr 0.7.x (preview) · Windows 11
> 경로는 `%APPDATA%` / `%LOCALAPPDATA%` / `%USERPROFILE%` 로 일반화(사용자명 무관).
> 아래 PowerShell 블록은 **Windows PowerShell**에서 실행하세요.

## 구성 요약
| # | 항목 | 위치 |
|---|------|------|
| 1 | herdr 설치 + Claude Code 통합 | herdr / `~/.claude` |
| 2 | `config.toml` (테마·단축키·사이드바 space/agent·알림) | `%APPDATA%\herdr\config.toml` |
| 3 | **Claude Code 하단 status line** — 모델·effort + 실제 플랜 사용률(5H/7D) 막대, 클라이언트·`/usage`와 동일 | `~/.claude` |
| 4 | **탭 제목 = 현재 작업** 자동 동기화(스마트 폴링) | `%APPDATA%\herdr\scripts` |
| 5 | **사이드바 worktree 뱃지** — git 링크 worktree 스페이스에 `` 표시 | `%APPDATA%\herdr\scripts` |
| 6 | JetBrainsMono Nerd Font | 사용자 폰트 |
| 7 | **Neovim + LazyVim** — herdr 안 소스편집(`prefix+e`), `$EDITOR=nvim` | `%LOCALAPPDATA%\nvim` |
| 8 | **herdr 오케스트레이션 슬래시 명령** — `/herdr-status·worktree·panes·agents` | `~/.claude\commands` |

---

## 0. 사전 준비
- 터미널 앱 (권장: **Windows Terminal**)
- (선택) 최신 herdr — 아래 1번에서 설치
> 참고: 이 구성은 **Node.js/ccusage가 필요 없습니다.** 사용률은 Claude Code가 status line에 직접 넘겨주는 데이터를 씁니다.

---

## 1. herdr 설치 + Claude Code 통합
herdr는 https://herdr.dev 안내대로 설치. 설치 후 바이너리(PATH 등록됨):
`%LOCALAPPDATA%\Programs\Herdr\bin\herdr.exe`
```powershell
herdr status
herdr channel set preview          # 원본과 동일 (원하면 stable)
herdr integration install claude   # .claude\hooks\herdr-agent-state.ps1 훅 설치
herdr integration status           # claude: current 확인
```

---

## 2. 설정 파일 `config.toml`
경로: `%APPDATA%\herdr\config.toml`
```powershell
$cfg = "$env:APPDATA\herdr\config.toml"
New-Item -ItemType Directory -Force -Path (Split-Path $cfg) | Out-Null
@'
# herdr configuration — reload live:  herdr server reload-config  (or ctrl+b, shift+r)
onboarding = false

[theme]
# catppuccin, terminal, tokyo-night, dracula, nord, gruvbox,
# one-dark, solarized, kanagawa, rose-pine, vesper
name = "catppuccin"
auto_switch = true
dark_name = "catppuccin"
light_name = "catppuccin-latte"

[terminal]
new_cwd = "follow"          # 새 패널은 현재 디렉터리 상속

[update]
channel = "preview"
version_check = true

[keys]
# prefix 기본은 ctrl+b. ctrl+enter는 시도하지 말 것 — Enter는 이미 제어 문자(\r)라
# 대부분의 터미널(Kitty keyboard protocol / win32-input-mode 없이는 Windows Terminal 포함)이
# ctrl+enter와 평범한 enter를 구분해 보내지 않아서 prefix로 동작하지 않음.
# ctrl+space는 한 손으로 누르기 쉽고 거의 충돌이 없어 최종적으로 이걸로 확정.
prefix = "ctrl+space"

# 탭 전환: 기본 prefix+p/n 대신 좌우 화살표
previous_tab = "prefix+left"
next_tab = "prefix+right"

# 탭 생성/닫기: 기본 prefix+c / prefix+shift+x 대신 위/아래 화살표
# (탭 닫기 확인창 옵션은 없음 — confirm_close는 workspace 전용. 안에서 실행 중인
#  프로세스가 있을 때만 경고하는 기본 동작을 그대로 사용)
new_tab = "prefix+up"
close_tab = "prefix+down"

# 가로분할/세로분할: 기본 prefix+minus / prefix+v 대신 space/enter
split_horizontal = "prefix+space"
split_vertical = "prefix+enter"

last_pane = "prefix+backtick"     # prefix + ` : 최근 두 패널 토글

[keys.indexed]
tabs = "ctrl"                     # Ctrl+1..9 로 탭 직접 전환 (prefix+1..9 도 유지)

# prefix+e → 현재 workspace 디렉터리에서 Neovim 열기 (:q 하면 pane 자동 닫힘)
# Windows는 cmd.exe /d /c 경유, 새 pane은 cwd 상속. (7번 Neovim 설치 후 동작)
[[keys.command]]
key = "prefix+e"
type = "pane"
command = "nvim ."

[ui]
agent_panel_sort = "priority"              # 주의 필요한 에이전트가 위로
show_agent_labels_on_pane_borders = true   # 분할 패널 테두리에 에이전트 라벨

[ui.sidebar.spaces]
# $worktree = 커스텀 토큰(5번 리포터가 채움): git 링크 worktree 스페이스에만 아이콘 표시
rows = [
  ["state_icon", "workspace"],
  ["branch", "git_status", "$worktree"],
]

[ui.sidebar.agents]
rows = [
  ["state_icon", "workspace", "tab"],
  ["agent"],
]

[ui.sidebar.agents.rows_by_agent]
# Claude 에이전트는 "지금 하는 작업"(터미널 제목)도 표시
claude = [
  ["state_icon", "workspace", "tab"],
  ["terminal_title_stripped"],
  ["agent"],
]

[ui.toast]
delivery = "system"    # 백그라운드 에이전트 상태변화 시 데스크톱 알림
delay_seconds = 1

[ui.sound]
enabled = true         # 상태변화 시 소리
'@ | Out-File -FilePath $cfg -Encoding utf8
herdr server reload-config     # "status":"applied", "diagnostics":[] 이면 정상
```

> ⚠️ **hjkl 페인 이동은 같은 탭 안에서만 동작합니다.** `focus_pane_left/down/up/right`(`prefix+h/j/k/l`)는
> 한 탭 안에서 분할된(split) 페인 사이만 이동하며 탭을 넘나들지 않습니다. 서로 다른 탭에 열린 두
> 세션은 hjkl로 이동이 안 되는 게 정상이며(prefix 키 문제 아님), `herdr pane list`의 `tab_id`로 확인 가능.
> 한 화면에서 나란히 보려면 `prefix+space`(가로분할)/`prefix+enter`(세로분할)로 새로 분할하거나
> `herdr pane move <pane_id> --tab <tab_id> --split right`로 기존 탭에 합치세요.

---

## 3. Claude Code 하단 status line (모델·effort + 실제 플랜 사용률)
표시 예 (색상 🟢<70 🟡70–89 🔴90+):
```
Opus 4.8 (1M context) · high  |  5H ██░░░░░░ 24% 2h39m   7D ██████░░ 78% 3d5h
```
- **모델**(시안) `·` **effort**(마젠타) — stdin `model.display_name` / `effort.level`에서 읽음. `/model`·`/effort`로 바꾸면 자동 반영, `/fast` 켜면 `high·fast`.
- **5H** = 5시간 롤링 윈도우 사용률 + 리셋까지 남은 시간
- **7D** = 7일(주간) 윈도우 사용률 + 리셋까지
- 사용률 값은 Claude Code가 status line stdin으로 넘겨주는 `rate_limits`에서 읽음 → **`/usage`·클라이언트와 100% 동일**. ccusage/캐시 불필요.
- ⚠️ `rate_limits`는 **Claude.ai Pro/Max**에서 **세션 첫 API 응답 이후** 채워집니다. 없으면 `(usage n/a)` 표시(모델·effort는 항상 표시).

### 3-1. status line 스크립트 : `%USERPROFILE%\.claude\scripts\cc-statusline.ps1`
```powershell
$dir = "$env:USERPROFILE\.claude\scripts"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
@'
# Claude Code status line: model . effort  |  REAL plan usage from stdin (same as /usage).
#   Opus 4.8 (1M context) . high  |  5H ##...  24%  7D ###.. 41%   (5H=5h window, 7D=weekly)
$ErrorActionPreference = 'SilentlyContinue'
$utf8 = New-Object System.Text.UTF8Encoding $false
[Console]::OutputEncoding = $utf8

$raw = try { [Console]::In.ReadToEnd() } catch { '' }
$j   = try { $raw | ConvertFrom-Json } catch { $null }

$e = [char]27
$R = "$e[0m"; $dim = "$e[2m"
function Col([double]$pct) { if ($pct -ge 90) { "$e[91m" } elseif ($pct -ge 70) { "$e[93m" } else { "$e[92m" } }
function Bar([double]$pct, [int]$cells) {
    $f = [int][math]::Round($pct / (100.0 / $cells))
    if ($f -gt $cells) { $f = $cells }; if ($f -lt 0) { $f = 0 }
    ([string][char]0x2588) * $f + ([string][char]0x2591) * ($cells - $f)
}
function Remaining($resetsAt) {
    if (-not $resetsAt) { return '' }
    $secs = [int64]$resetsAt - [int64][DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    if ($secs -le 0) { return '' }
    $d = [math]::Floor($secs / 86400)
    $h = [math]::Floor(($secs % 86400) / 3600)
    $m = [math]::Floor(($secs % 3600) / 60)
    if ($d -gt 0) { "{0}d{1}h" -f $d, $h } elseif ($h -gt 0) { "{0}h{1:00}m" -f $h, $m } else { "${m}m" }
}
function Segment($label, $win) {
    if (-not $win -or $null -eq $win.used_percentage) { return $null }
    $p  = [int][math]::Round([double]$win.used_percentage)
    $rs = Remaining $win.resets_at
    $tail = if ($rs) { " ${dim}${rs}${R}" } else { '' }
    "${dim}${label}${R} $(Col $p)$(Bar $p 8) ${p}%${R}$tail"
}

# --- model + effort (from stdin) ---
$cyan = "$e[96m"; $mag = "$e[95m"
$mid  = [string][char]0x00B7   # middle dot
$head = @()
$model = $j.model.display_name
if ($model) { $head += "${cyan}${model}${R}" }
$eff = $j.effort.level
if ($eff) {
    $et = if ($j.fast_mode) { "${eff}${mid}fast" } else { $eff }
    $head += "${mag}${et}${R}"
}

# --- plan usage (rate_limits) ---
$rl = $j.rate_limits
$parts = @()
$s = Segment '5H' $rl.five_hour;  if ($s) { $parts += $s }
$s = Segment '7D' $rl.seven_day;  if ($s) { $parts += $s }
if (-not $parts.Count) { $parts += "${dim}(usage n/a)${R}" }

$all = @()
if ($head.Count)  { $all += ($head  -join " ${dim}${mid}${R} ") }
if ($parts.Count) { $all += ($parts -join "  ") }
[Console]::Out.Write(($all -join "  ${dim}|${R}  "))
'@ | Out-File -FilePath "$dir\cc-statusline.ps1" -Encoding utf8
```

### 3-2. `settings.json`에 등록
`%USERPROFILE%\.claude\settings.json` 최상위 객체에 추가(기존 `hooks` 등 보존):
```json
"statusLine": {
  "type": "command",
  "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"%USERPROFILE%\\.claude\\scripts\\cc-statusline.ps1\"",
  "padding": 0
}
```
> ⚠️ **Claude Code를 재시작**해야 status line이 로드됩니다.

---

## 4. 탭 제목 = 현재 작업 자동 동기화 (스마트 폴링)
Claude 에이전트가 있는 탭의 이름을 그 에이전트의 "현재 작업"(터미널 제목)으로 갱신. **제목이 실제로 바뀐 경우에만** rename 호출. Claude 에이전트가 없는 탭은 손대지 않음(수동 이름 보존).

### 4-1. 스크립트 : `%APPDATA%\herdr\scripts\sync-tab-titles.ps1`
```powershell
$dir = "$env:APPDATA\herdr\scripts"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
@'
# Herdr: name each tab after the Claude Code task running in it.  (-Once for one shot)
param([switch]$Once)
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8   # decode herdr UTF-8 JSON (Korean-safe)
$herdr = Join-Path $env:LOCALAPPDATA 'Programs\Herdr\bin\herdr.exe'

function Get-Json($raw) { if ($raw) { try { return (($raw -join "`n") | ConvertFrom-Json) } catch {} } }
$script:lastTitles = @{}   # smart polling: only rename when the title changed

function Sync-Once {
    $ws = Get-Json (& $herdr workspace list)
    if (-not $ws) { return }
    foreach ($w in $ws.result.workspaces) {
        $pl = Get-Json (& $herdr pane list --workspace $w.workspace_id)
        if (-not $pl) { continue }
        foreach ($g in ($pl.result.panes | Group-Object tab_id)) {
            $claude = $g.Group | Where-Object { $_.agent -eq 'claude' -and $_.terminal_title_stripped } | Select-Object -First 1
            if (-not $claude) { continue }
            $title = ([string]$claude.terminal_title_stripped).Trim()
            if (-not $title) { continue }
            if ($title.Length -gt 24) { $title = $title.Substring(0, 23) + [char]0x2026 }
            if ($script:lastTitles[$g.Name] -eq $title) { continue }
            & $herdr tab rename $g.Name $title | Out-Null
            $script:lastTitles[$g.Name] = $title
        }
    }
}
if ($Once) { Sync-Once; return }
$mutex = New-Object System.Threading.Mutex($false, 'Global\HerdrTabTitleSync')   # single instance
if (-not $mutex.WaitOne(0)) { return }
try { while ($true) { Sync-Once; Start-Sleep -Seconds 15 } } finally { $mutex.ReleaseMutex() }
'@ | Out-File -FilePath "$dir\sync-tab-titles.ps1" -Encoding utf8
```

### 4-2. 로그인 자동 시작(HKCU Run) + 지금 시작
```powershell
$script = "$env:APPDATA\herdr\scripts\sync-tab-titles.ps1"
$cmd = "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
New-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'HerdrTabTitles' -Value $cmd -PropertyType String -Force | Out-Null
Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',$script
```
> 중지: Run 값 `HerdrTabTitles` 삭제 + 해당 powershell 프로세스 종료.
> 테스트: `powershell -File "$script" -Once`

---

## 5. 사이드바 worktree 뱃지 (스마트 폴링)
git **링크 worktree**로 열린 herdr 스페이스에만 사이드바에 아이콘(``, Nerd Font code-fork)을 붙임. 메인 체크아웃·비(非)git 스페이스는 표시 안 함(브랜치 이름은 기존 `branch` 토큰이 그대로 담당). 판별 기준: worktree의 git-dir(`…/.git/worktrees/<name>`)이 저장소 공통 git-dir(`…/.git`)과 다름. TTL 90초로 리포터가 죽으면 뱃지가 자동으로 사라짐.
> ⚠️ 2번 `config.toml`의 `[ui.sidebar.spaces]` 행에 `$worktree` 토큰이 포함돼 있어야 실제로 표시됩니다.

### 5-1. 리포터 : `%APPDATA%\herdr\scripts\report-worktree.ps1`
```powershell
$dir = "$env:APPDATA\herdr\scripts"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
@'
# Herdr: flag each workspace (space) that is a linked git worktree with a
# $worktree sidebar badge.  Main checkout / non-repo -> cleared.  (-Once for one shot)
param([switch]$Once)
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8    # herdr emits UTF-8 JSON (Korean-safe)
$herdr  = Join-Path $env:LOCALAPPDATA 'Programs\Herdr\bin\herdr.exe'
$Source = 'worktree-badge'
$Badge  = [string][char]0xf126     # Nerd Font code-fork: marks a linked worktree

function Get-Json($raw) { if ($raw) { try { return (($raw -join "`n") | ConvertFrom-Json) } catch {} } }

# A linked worktree's git-dir (.../.git/worktrees/<name>) differs from the repo's
# common git-dir (.../.git); for the main worktree they are the same path.
function Test-IsWorktree($cwd) {
    if (-not $cwd) { return $false }
    if (-not (Test-Path -LiteralPath $cwd)) { return $false }
    $gd = & git -C $cwd rev-parse --absolute-git-dir 2>$null
    if (-not $gd) { return $false }
    $cd = & git -C $cwd rev-parse --path-format=absolute --git-common-dir 2>$null
    if (-not $cd) { return $false }
    $a = ($gd -replace '/','\').TrimEnd('\')
    $b = ($cd -replace '/','\').TrimEnd('\')
    return ($a -ne $b)
}

function Sync-Once {
    $ws = Get-Json (& $herdr workspace list)
    if (-not $ws) { return }
    foreach ($w in $ws.result.workspaces) {
        $wid = $w.workspace_id
        $pl  = Get-Json (& $herdr pane list --workspace $wid)
        if (-not $pl) { continue }
        $pane = $pl.result.panes | Where-Object { $_.cwd } | Sort-Object { -not $_.focused } | Select-Object -First 1
        $cwd  = if ($pane) { [string]$pane.cwd } else { $null }
        if (Test-IsWorktree $cwd) {
            & $herdr workspace report-metadata $wid --source $Source --token "worktree=$Badge" --ttl-ms 90000 | Out-Null
        } else {
            & $herdr workspace report-metadata $wid --source $Source --clear-token worktree | Out-Null
        }
    }
}

if ($Once) { Sync-Once; return }
$mutex = New-Object System.Threading.Mutex($false, 'Global\HerdrWorktreeBadge')   # single instance
if (-not $mutex.WaitOne(0)) { return }
try { while ($true) { Sync-Once; Start-Sleep -Seconds 20 } } finally { $mutex.ReleaseMutex() }
'@ | Out-File -FilePath "$dir\report-worktree.ps1" -Encoding utf8
```

### 5-2. 로그인 자동 시작(HKCU Run) + 지금 시작
```powershell
$script = "$env:APPDATA\herdr\scripts\report-worktree.ps1"
$cmd = "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
New-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'HerdrWorktreeBadge' -Value $cmd -PropertyType String -Force | Out-Null
Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',$script
```
> 중지: Run 값 `HerdrWorktreeBadge` 삭제 + 해당 powershell 프로세스 종료.
> 테스트: `powershell -File "$script" -Once`

---

## 6. JetBrainsMono Nerd Font
> herdr 아이콘·막대(█░ 등)가 깨지지 않으려면 Nerd Font 필요. 한글은 시스템 폰트로 폴백.
```powershell
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$tmp = Join-Path $env:TEMP 'jbm-nf'; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zip = Join-Path $tmp 'JetBrainsMono.zip'
Invoke-WebRequest -Uri "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip" -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $tmp -Force
$dest = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"; New-Item -ItemType Directory -Force -Path $dest | Out-Null
$reg = "HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
Get-ChildItem $tmp -Filter "JetBrainsMonoNerdFont-*.ttf" | ForEach-Object {
    $t = Join-Path $dest $_.Name; Copy-Item $_.FullName $t -Force
    New-ItemProperty -Path $reg -Name ("JetBrainsMono NF " + ($_.BaseName -replace 'JetBrainsMonoNerdFont-','') + " (TrueType)") -Value $t -PropertyType String -Force | Out-Null
}
```
그다음 **터미널 글꼴을 `JetBrainsMono Nerd Font`로 지정**(Windows Terminal: 설정 → 프로필 → 모양 → 글꼴). 목록에 없으면 터미널 재시작.

---

## 7. Neovim + LazyVim (herdr 안 소스편집)
herdr 패널에서 `prefix + e` → 현재 workspace 디렉토리에서 nvim 열기(`:q` 하면 pane 자동 닫힘). `$EDITOR=nvim`.

### 7-1. 설치 (winget)
```powershell
winget install -e --id Neovim.Neovim --silent --accept-package-agreements --accept-source-agreements
winget install -e --id zig.zig --silent --accept-package-agreements --accept-source-agreements                 # treesitter C 컴파일러
winget install -e --id BurntSushi.ripgrep.MSVC --silent --accept-package-agreements --accept-source-agreements  # telescope grep (rg)
winget install -e --id sharkdp.fd --silent --accept-package-agreements --accept-source-agreements               # telescope 파일 (fd)
```
> winget이 PATH를 갱신하므로 **새 터미널**에서 `nvim`/`rg`/`fd`/`zig`가 잡힙니다(기존 창은 재시작). node(LSP)는 이미 있음.

### 7-2. LazyVim 설정
```powershell
$nvim = "$env:LOCALAPPDATA\nvim"
if (-not (Test-Path $nvim)) {
  git clone --depth 1 https://github.com/LazyVim/starter $nvim
  Remove-Item -LiteralPath "$nvim\.git" -Recurse -Force
}
nvim --headless "+Lazy! sync" +qa    # 플러그인 부트스트랩(첫 1회)
```
- 커스터마이즈: `%LOCALAPPDATA%\nvim\lua\plugins\*.lua`, 관리 `:Lazy` / `:Mason`.
- treesitter는 main 브랜치(async). 번들 파서(lua/c/vim/markdown 등)는 즉시 동작, 그 외 언어는 해당 파일 첫 오픈 시 자동 설치(필요시 `:TSInstall <lang>`).

### 7-3. `$EDITOR` + herdr 키바인딩
```powershell
[Environment]::SetEnvironmentVariable('EDITOR','nvim','User')
[Environment]::SetEnvironmentVariable('VISUAL','nvim','User')
```
herdr 키바인딩(`prefix+e`)은 **2번 config 템플릿에 이미 포함**돼 있습니다. 2번을 안 썼거나 나중에 추가한다면 `[keys.indexed]` 다음에:
```toml
[[keys.command]]
key = "prefix+e"
type = "pane"          # :q 하면 pane 닫힘
command = "nvim ."     # Windows는 cmd.exe /d /c 경유, 새 pane은 cwd 상속
```
추가/변경 후 `herdr server reload-config`.

---

## 8. herdr 오케스트레이션 슬래시 명령 (Claude Code)
> herdr의 Claude 통합은 **훅만** 설치하고 슬래시 명령은 만들지 않습니다(herdr→Claude 단방향 텔레메트리). 아래는 자주 쓰는 herdr 동작을 Claude Code에 노출하는 **커스텀 명령**(`~/.claude\commands\*.md`). herdr가 PATH에 있어 명령 내부에서 `` !`herdr …` ``로 실시간 상태를 주입합니다.

| 명령 | 하는 일 |
|------|--------|
| `/herdr-status` | 읽기전용 개요 — 모든 workspace/agent와 상태(working/idle/blocked), 주의 필요 항목 상단 |
| `/herdr-worktree` | worktree 목록/생성/열기/제거 (병렬 작업선) |
| `/herdr-panes` | pane/레이아웃 조회·분할·zoom·focus·close |
| `/herdr-agents` | agent list/start/send/wait/read (오케스트레이션 제어) |

- 각 파일 frontmatter는 `allowed-tools: Bash(herdr:*)`. 예: `/herdr-worktree create feat-x` → `herdr worktree create --branch feat-x --focus`.
- 제거·텍스트 전송 등 파괴적/개입 동작은 **확인 후 실행**하도록 프롬프트에 명시돼 있음.
- 핵심 오케스트레이션 원시명령: `herdr agent start … -- <argv>`, `herdr agent send/wait`, `herdr wait agent-status`, `herdr api snapshot`.

---

## 9. 최종 확인
```powershell
herdr status                                   # server running
herdr integration status                       # claude: current
Get-Content "$env:USERPROFILE\.claude\settings.json" | Select-String statusLine
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name HerdrTabTitles
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name HerdrWorktreeBadge
nvim --version | Select-Object -First 1        # NVIM v0.12.x
Get-ChildItem "$env:USERPROFILE\.claude\commands\herdr-*.md" | Select-Object Name   # 슬래시 명령 4종
```
그리고 **Claude Code 재시작** → 하단에 `모델 · effort | 5H … 7D …`, 탭 이름이 현재 작업으로 바뀌고, worktree로 연 스페이스에 `` 뱃지, `prefix+e`로 nvim, `/herdr-*` 명령이 뜨면 완료.

---

## 되돌리기 / 조정
| 항목 | 방법 |
|------|------|
| status line 색상 임계값/막대 길이 | `cc-statusline.ps1` (Col 70·90, Bar 8칸) |
| status line 모델·effort 색 | `cc-statusline.ps1`의 `$cyan`(모델)·`$mag`(effort) |
| status line 끄기 | `settings.json`의 `statusLine` 제거 후 Claude 재시작 |
| 탭 동기화 주기 | `sync-tab-titles.ps1`의 `Start-Sleep -Seconds 15` |
| 탭 동기화 끄기 | Run 키 `HerdrTabTitles` 삭제 + 프로세스 종료 |
| worktree 뱃지 아이콘 | `report-worktree.ps1`의 `$Badge`([char]0xf126) |
| worktree 뱃지 끄기 | Run 키 `HerdrWorktreeBadge` 삭제 + 프로세스 종료, config 행에서 `$worktree` 제거 |
| 데스크톱 알림 끄기 | `config.toml` `[ui.toast] delivery = "off"` |
| prefix 변경 | `config.toml` `[keys] prefix = "..."` 후 reload |
| 테마 | `[theme] name` 변경 후 reload |
| nvim 에디터 키 | `config.toml`의 `[[keys.command]] key`(기본 `prefix+e`) |
| nvim 설정 | `%LOCALAPPDATA%\nvim\lua\plugins\*.lua`, `:Lazy`/`:Mason` |
| herdr 슬래시 명령 | `~/.claude\commands\herdr-*.md` 편집/삭제 |

**주요 경로**
- herdr 설정: `%APPDATA%\herdr\config.toml`
- herdr 스크립트: `%APPDATA%\herdr\scripts\sync-tab-titles.ps1`, `%APPDATA%\herdr\scripts\report-worktree.ps1`
- Claude 설정/스크립트: `%USERPROFILE%\.claude\settings.json`, `%USERPROFILE%\.claude\scripts\cc-statusline.ps1`
- Claude 슬래시 명령: `%USERPROFILE%\.claude\commands\herdr-*.md`
- Neovim 설정/데이터: `%LOCALAPPDATA%\nvim`, `%LOCALAPPDATA%\nvim-data`
- herdr 바이너리: `%LOCALAPPDATA%\Programs\Herdr\bin\herdr.exe`
- 사용자 폰트: `%LOCALAPPDATA%\Microsoft\Windows\Fonts`

> 개발 과정에서 쓰던 "사이드바 사용량 바 + 3분 예약 작업 + ccusage 리포터"는 모두 제거되었습니다(사용률은 Claude Code status line의 실제 rate_limits 데이터로 대체).
