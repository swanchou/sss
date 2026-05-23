@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   Excel 识别工具 - Windows 打包脚本
echo ============================================
echo.

set "ROOT_DIR=%~dp0.."
set "PACKAGING_DIR=%~dp0"

echo [1/6] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo       Python 环境正常

echo.
echo [2/6] 安装 Python 依赖...
pip install flask flask-cors openpyxl pyinstaller --quiet
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo       依赖安装完成

echo.
echo [3/6] 检查前端构建产物...
if not exist "%ROOT_DIR%\dist\index.html" (
    echo 警告: 未找到前端构建产物，尝试构建...
    cd /d "%ROOT_DIR%"
    call npm install
    call npm run build
    if errorlevel 1 (
        echo 错误: 前端构建失败
        pause
        exit /b 1
    )
)
echo       前端构建产物正常

echo.
echo [4/6] 生成软件图标...
cd /d "%PACKAGING_DIR%"
python generate_icon.py
if errorlevel 1 (
    echo 警告: 图标生成失败，将使用默认图标
)

echo.
echo [5/6] 使用 PyInstaller 打包...
cd /d "%ROOT_DIR%"
pyinstaller --clean packaging/phone_finder.spec
if errorlevel 1 (
    echo 错误: PyInstaller 打包失败
    pause
    exit /b 1
)
echo       打包完成

echo.
echo [6/6] 复制额外文件...
if exist "%ROOT_DIR%\dist\Excel识别工具" (
    copy /Y "%ROOT_DIR%\src\华为授权服务中心_整理.json" "%ROOT_DIR%\dist\Excel识别工具\" >nul
    echo       额外文件复制完成
)

echo.
echo ============================================
echo   打包完成！
echo   输出目录: %ROOT_DIR%\dist\Excel识别工具
echo ============================================
echo.
echo 您可以将 "Excel识别工具" 文件夹压缩后分发给用户。
echo 用户解压后双击 "Excel识别工具.exe" 即可使用。
echo.

pause
