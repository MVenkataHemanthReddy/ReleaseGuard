Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting ReleaseGuard Platform..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location "D:\Release Guard"

Write-Host "[1/3] Starting Django Backend Server (http://127.0.0.1:8000)..." -ForegroundColor Green
Start-Process cmd.exe -ArgumentList '/k', '".venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"'

Write-Host "[2/3] Starting ReleaseGuard Background Worker..." -ForegroundColor Green
Start-Process cmd.exe -ArgumentList '/k', '".venv\Scripts\python.exe manage.py runworker --interval 5"'

Write-Host "[3/3] Starting Frontend Dev Server (http://localhost:3000)..." -ForegroundColor Green
Set-Location "D:\Release Guard\frontend"
Start-Process cmd.exe -ArgumentList '/k', '"npm run dev"'

Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
