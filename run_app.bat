@echo off
title ReleaseGuard Launcher
echo ========================================================
echo  ReleaseGuard Platform Launcher
echo ========================================================
cd /d "D:\Release Guard"

REM Kill any stale processes on these ports first
echo [0/3] Clearing any stale processes on ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 "') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 "') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 1 >nul

echo [1/3] Starting Django Backend (http://127.0.0.1:8000)...
start "ReleaseGuard Backend" cmd /k "cd /d "D:\Release Guard" && .venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

echo Waiting for backend to start...
timeout /t 4 >nul

echo [2/3] Starting Background Worker...
start "ReleaseGuard Worker" cmd /k "cd /d "D:\Release Guard" && .venv\Scripts\python.exe manage.py runworker --interval 5"

echo [3/3] Starting Frontend Dev Server (http://localhost:3000)...
start "ReleaseGuard Frontend" cmd /k "cd /d "D:\Release Guard\frontend" && npm run dev"

echo Waiting for frontend to start...
timeout /t 6 >nul

echo ========================================================
echo  ReleaseGuard is running!
echo  Frontend:    http://localhost:3000
echo  Backend API: http://127.0.0.1:8000/api/v1/
echo  Admin:       http://127.0.0.1:8000/admin/
echo ========================================================
start http://localhost:3000
