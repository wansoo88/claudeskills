# 외부 추천 스킬 전역 설치 스크립트 (Windows PowerShell)
# 실행: 저장소 루트에서  powershell -ExecutionPolicy Bypass -File .\tools\install_external_skills.ps1
# 하는 일: 원 저장소 마켓플레이스 등록 + user scope 플러그인 설치(멱등) + watch 의존성(ffmpeg·yt-dlp) 설치.
# 목록·공존 규칙은 EXTERNAL-SKILLS.md. agentmemory 엔진(iii)은 수동 단계라 안내만 출력한다.
param(
    [switch]$DryRun,          # 실행 없이 명령만 출력
    [switch]$SkipDeps,        # winget 의존성 설치 생략
    [switch]$SkipAgentMemory  # agentmemory 제외 (엔진·상시 서버가 필요)
)

$ErrorActionPreference = "Stop"

# 마켓플레이스(owner/repo) - 플러그인 설치 id
$marketplaces = @(
    "bradautomates/claude-video",
    "multica-ai/andrej-karpathy-skills",
    "Lum1104/Understand-Anything",
    "rohitg00/agentmemory",
    "pbakaus/impeccable"
)
$plugins = @(
    "watch@claude-video",
    "andrej-karpathy-skills@karpathy-skills",
    "superpowers@claude-plugins-official",
    "understand-anything@understand-anything",
    "agentmemory@agentmemory",
    "impeccable@impeccable"
)
if ($SkipAgentMemory) {
    $marketplaces = $marketplaces | Where-Object { $_ -ne "rohitg00/agentmemory" }
    $plugins = $plugins | Where-Object { $_ -ne "agentmemory@agentmemory" }
}

function Invoke-Step([string]$label, [string[]]$cmd) {
    Write-Host "  > $($cmd -join ' ')"
    if ($DryRun) { return }
    & $cmd[0] $cmd[1..($cmd.Length - 1)]
    if ($LASTEXITCODE -ne 0) { Write-Host "  [경고] $label 실패 (exit $LASTEXITCODE)" -ForegroundColor Yellow }
}

Write-Host "=== 외부 추천 스킬 전역 설치 ===" -ForegroundColor Cyan
if ($DryRun) { Write-Host "(DryRun - 실행하지 않고 명령만 출력)" -ForegroundColor DarkGray }

if (-not $DryRun -and $null -eq (Get-Command claude -ErrorAction SilentlyContinue)) {
    throw "claude CLI가 PATH에 없습니다. Claude Code 설치 후 다시 실행하세요."
}

# 1) 마켓플레이스 등록 (이미 있으면 CLI가 건너뜀)
Write-Host "`n[1/3] 마켓플레이스 등록"
foreach ($m in $marketplaces) { Invoke-Step "marketplace add $m" @("claude", "plugin", "marketplace", "add", $m) }

# 2) 플러그인 설치 (설치된 것은 건너뜀)
Write-Host "`n[2/3] 플러그인 설치 (scope: user)"
$installed = @()
if (-not $DryRun) {
    $installed = (claude plugin list --json | ConvertFrom-Json) | ForEach-Object { $_.id }
}
foreach ($p in $plugins) {
    if ($installed -contains $p) { Write-Host "  = $p (설치됨, 건너뜀)"; continue }
    Invoke-Step "install $p" @("claude", "plugin", "install", $p, "--scope", "user")
}

# 3) watch 의존성
Write-Host "`n[3/3] watch 의존성 (ffmpeg · yt-dlp)"
if ($SkipDeps) {
    Write-Host "  (생략)"
} else {
    $deps = @(@{ bin = "ffmpeg"; id = "Gyan.FFmpeg" }, @{ bin = "yt-dlp"; id = "yt-dlp.yt-dlp" })
    foreach ($d in $deps) {
        if (Get-Command $d.bin -ErrorAction SilentlyContinue) { Write-Host "  = $($d.bin) (있음)"; continue }
        Invoke-Step "winget $($d.id)" @("winget", "install", "--id", $d.id, "-e", "--accept-source-agreements", "--accept-package-agreements", "--silent")
    }
}

Write-Host ""
Write-Host "설치 완료. Claude Code를 재시작하세요(또는 /reload-plugins). winget으로 설치했다면 새 터미널에서 PATH가 반영됩니다." -ForegroundColor Green
if (-not $SkipAgentMemory) {
    Write-Host ""
    Write-Host "[agentmemory 수동 단계] 서버가 떠 있어야 기록됩니다:" -ForegroundColor Yellow
    Write-Host "  1) https://github.com/iii-hq/iii/releases/tag/iii%2Fv0.11.2 에서 iii-x86_64-pc-windows-msvc.zip"
    Write-Host "     -> iii.exe 를 $env:USERPROFILE\.agentmemory\bin\ 에 복사"
    Write-Host "  2) 별도 터미널: npx -y @agentmemory/agentmemory@latest   (LLM 공급자는 keyless 선택)"
    Write-Host "  3) 확인: curl http://localhost:3111/agentmemory/health"
}
Write-Host "공존 규칙·보안 주의: EXTERNAL-SKILLS.md"
