# data-product-studio 전역 설치 스크립트 (Windows PowerShell)
# 실행: 이 폴더에서  powershell -ExecutionPolicy Bypass -File .\install.ps1
# 하는 일: skills/agents/commands를 ~/.claude로 복사 + hooks를 settings.json에 병합.
# 설치 후 Claude Code를 재시작하면 /init-project 등이 활성화됩니다.

$ErrorActionPreference = "Stop"
$src = $PSScriptRoot
$dst = "$env:USERPROFILE\.claude"

Write-Host "=== data-product-studio 전역 설치 ===" -ForegroundColor Cyan
Write-Host "소스: $src"
Write-Host "대상: $dst"

# 1) 폴더 준비
New-Item -ItemType Directory -Force "$dst\skills", "$dst\agents", "$dst\commands", "$dst\data-product-studio\hooks" | Out-Null

# 2) 복사
Copy-Item "$src\skills\*"   "$dst\skills\"   -Recurse -Force
Copy-Item "$src\agents\*"   "$dst\agents\"   -Recurse -Force
Copy-Item "$src\commands\*" "$dst\commands\" -Recurse -Force
Copy-Item "$src\hooks\*"    "$dst\data-product-studio\hooks\" -Recurse -Force

# 3) __pycache__ 정리
Get-ChildItem "$dst\skills", "$dst\data-product-studio" -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 4) 훅 병합 (기존 보존, 멱등)
$py = (Get-Command python -ErrorAction SilentlyContinue)
if ($null -eq $py) {
    Write-Host "[경고] python이 PATH에 없습니다. 스크립트/훅 실행에 Python이 필요합니다." -ForegroundColor Yellow
} else {
    python "$src\tools\merge_hooks.py"
}

Write-Host ""
Write-Host "설치 완료. Claude Code를 재시작하면 /init-project · /adopt-project · /next-stage · /write-readme · /refresh-skills 가 활성화됩니다." -ForegroundColor Green
Write-Host "확인: Claude Code에서 '/' 입력 시 위 커맨드가 보이면 성공."
