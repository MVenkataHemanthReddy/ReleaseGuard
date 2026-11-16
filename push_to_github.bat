@echo off
title Push ReleaseGuard to GitHub
cd /d "D:\Release Guard"
echo ==============================================================
echo Pushing ReleaseGuard to https://github.com/MVenkataHemanthReddy/ReleaseGuard
echo ==============================================================
echo.
"C:\Users\mitta\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe" push -u origin main
echo.
echo ==============================================================
echo If you saw "Repository not found", make sure you created the
echo repository named "ReleaseGuard" at https://github.com/new first!
echo ==============================================================
pause
