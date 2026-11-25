# Dừng demo xem lại đang chạy ở nền (chỉ app_replay.py chạy với đúng cổng này).
# Dùng: powershell -ExecutionPolicy Bypass -File demo\stop_demo.ps1 [-Port 7860]
param([int]$Port = 7860)
$pattern = "*app_replay.py*--port $Port*"
# venv trên Windows chạy python qua tiến trình con, nên tìm theo dòng lệnh thay vì chỉ theo PID đã lưu
$procs = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object { $_.CommandLine -like $pattern })
foreach ($p in $procs) {
  Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  Write-Host "Đã dừng PID $($p.ProcessId)"
}
Remove-Item (Join-Path $PSScriptRoot "demo_server.pid") -ErrorAction SilentlyContinue
if ($procs.Count -eq 0) { Write-Host "Không thấy demo nào đang chạy trên cổng $Port." }
