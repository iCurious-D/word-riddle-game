@echo off
chcp 65001 >nul
title 字谜游戏 - 一键启动
echo ============================================
echo    字谜挑战 - 一键启动前后端
echo ============================================
echo.

REM 启动后端（新窗口）
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 未找到 backend\.venv，请先创建虚拟环境并安装依赖：
    echo     cd backend
    echo     python -m venv .venv
    echo     .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)
start "字谜后端 :8000" cmd /k ".venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"

REM 启动前端（新窗口）
cd /d "%~dp0fronted"
if not exist "node_modules" (
    echo [提示] 未找到 fronted\node_modules，正在安装前端依赖（首次较慢）...
    call npm install
)
start "字谜前端 :5173" cmd /k "npm run dev"

echo.
echo 已启动两个窗口：
echo    后端  http://127.0.0.1:8000
echo    前端  http://localhost:5173   ← 浏览器打开这个
echo.
echo 关闭那两个黑色窗口即可停止服务。
echo.
pause
