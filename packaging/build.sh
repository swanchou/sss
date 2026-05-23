#!/bin/bash

echo "============================================"
echo "  Excel 识别工具 - 打包准备脚本"
echo "============================================"
echo ""

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGING_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/4] 检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js"
    exit 1
fi
echo "      Node.js 环境正常"

echo ""
echo "[2/4] 安装前端依赖..."
cd "$ROOT_DIR"
npm install --silent
echo "      依赖安装完成"

echo ""
echo "[3/4] 构建前端静态资源..."
npm run build
if [ $? -ne 0 ]; then
    echo "错误: 前端构建失败"
    exit 1
fi
echo "      前端构建完成"

echo ""
echo "[4/4] 生成软件图标..."
cd "$PACKAGING_DIR"
python3 generate_icon.py 2>/dev/null || python generate_icon.py 2>/dev/null || echo "警告: 图标生成跳过（需要 Python）"
echo "      图标生成完成"

echo ""
echo "============================================"
echo "  准备工作完成！"
echo ""
echo "  要在 Windows 上打包，请将整个项目目录"
echo "  复制到 Windows 电脑，然后运行:"
echo "  packaging\\build.bat"
echo "============================================"
