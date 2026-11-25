# Mở demo xem lại ở nền (cửa sổ ẩn), chỉ trên máy này: http://127.0.0.1:7860
# Dùng: powershell -ExecutionPolicy Bypass -File demo\start_demo.ps1 [-Port 7860] [-DataRoot D:\MINHTRIHOCCODE\HOCKI5\CS331]
param([int]$Port = 7860, [string]$DataRoot = "")
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$py = Join-Path $repo ".venv-demo\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Chưa có .venv-demo. Xem demo\README.md mục Cài đặt." }
$busy = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($busy) { Write-Host "Cổng $Port đang được dùng (PID $($busy.OwningProcess)). Demo có thể đang chạy: http://127.0.0.1:$Port"; exit 0 }
$log = Join-Path $PSScriptRoot "demo_server.log"
$pyArgs = @("demo\app_replay.py", "--port", "$Port")
if ($DataRoot) { $pyArgs += @("--data-root", $DataRoot) }
$env:PYTHONIOENCODING = "utf-8"
$p = Start-Process -FilePath $py -ArgumentList $pyArgs -WorkingDirectory $repo -WindowStyle Hidden `
     -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru
Set-Content -Path (Join-Path $PSScriptRoot "demo_server.pid") -Value $p.Id
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Seconds 1
  if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "Demo đang chạy: http://127.0.0.1:$Port (PID $($p.Id)). Dừng: demo\stop_demo.ps1"; exit 0 }
  if ($p.HasExited) { break }
}
Write-Host "Demo chưa mở được. Xem $log và $log.err"; exit 1
