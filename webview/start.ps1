# codeb webview launcher
# Usage:
#   .\webview\start.ps1                       # auto-detect root, port 8777
#   .\webview\start.ps1 -Port 9000
#   .\webview\start.ps1 -Root D:\work\project\codeb -Port 9000
param(
  [string]$Root = "",
  [int]$Port = 8777
)

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Split-Path -Parent $here
if (-not $Root) { $Root = $project }

Write-Host "codeb webview"
Write-Host "  workspace : $Root"
Write-Host "  url       : http://127.0.0.1:$Port"
Write-Host "  (Ctrl+C to stop)"
Write-Host ""

$args = @("$here\server.mjs", "--root", $Root, "--port", "$Port")
& node @args
