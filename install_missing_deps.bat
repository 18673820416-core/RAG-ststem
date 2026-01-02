@echo off
chcp 65001 >nul
echo ====================================
echo 安装缺失的依赖包
echo ====================================
echo.

REM 检查虚拟环境是否存在
if not exist "myenv_stable\Scripts\activate.bat" (
    echo [错误] 虚拟环境 myenv_stable 不存在
    echo 请先运行: python setup_stable_env.py
    pause
    exit /b 1
)

echo [1/2] 激活虚拟环境 myenv_stable...
call myenv_stable\Scripts\activate.bat

echo.
echo [2/2] 安装缺失的依赖包...
echo.

echo 安装 psutil...
python -m pip install psutil>=5.9.0

echo.
echo 安装 scikit-image...
python -m pip install scikit-image>=0.21.0

echo.
echo ====================================
echo 依赖包安装完成！
echo ====================================
echo.
pause
