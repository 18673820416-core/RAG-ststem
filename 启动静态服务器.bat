@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title RAG系统 - 静态Web服务器

:: 切换到批处理文件所在目录
cd /d "%~dp0"

echo ========================================
echo RAG系统 - 静态Web服务器启动器
echo ========================================
echo.
echo 功能：启动轻量级常驻服务器，提供启动控制
echo 端口：10808
echo 访问：http://localhost:10808
echo.
echo ========================================
echo.

echo 正在检查端口10808的占用情况...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :10808 ^| findstr LISTENING') do (
    echo 检测到端口被进程ID=%%a占用，正在关闭...
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! == 0 (
        echo ✅ 成功关闭旧进程 %%a
    ) else (
        echo ⚠️ 无法关闭进程 %%a（可能需要管理员权限）
    )
)

echo 等待端口释放...
timeout /t 2 /nobreak >nul

echo 正在启动静态服务器...
python static_server.py

pause
