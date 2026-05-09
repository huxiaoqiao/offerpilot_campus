#!/usr/bin/env bash
# OfferPilot Campus - Development Startup Script
# Starts both backend (FastAPI) and frontend (Vite) servers

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  OfferPilot Campus - 开发环境启动"
echo "=========================================="

# --- Backend ---
echo ""
echo "[1/3] 启动后端 (FastAPI) ..."
cd "$PROJECT_DIR/backend"

if [ ! -f ".env" ]; then
    echo "  ⚠️  未找到 .env 文件，从 .env.example 复制..."
    cp .env.example .env
    echo "  📝 请编辑 backend/.env 配置 LLM API Key"
fi

if [ ! -d "data" ]; then
    mkdir -p data
fi

echo "  📦 安装 Python 依赖 ..."
pip install -r requirements.txt -q 2>/dev/null || true

echo "  🚀 启动 uvicorn (端口 8000) ..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "  ✅ 后端 PID: $BACKEND_PID"

# --- Frontend ---
echo ""
echo "[2/3] 启动前端 (Vite) ..."
cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "  📦 安装 npm 依赖 ..."
    npm install
fi

echo "  🚀 启动 vite dev server (端口 5173) ..."
npm run dev &
FRONTEND_PID=$!
echo "  ✅ 前端 PID: $FRONTEND_PID"

# --- Wait ---
echo ""
echo "[3/3] 服务启动完成!"
echo ""
echo "=========================================="
echo "  后端 API:  http://localhost:8000"
echo "  前端应用:  http://localhost:5173"
echo "  API 文档:  http://localhost:8000/docs"
echo "  健康检查:  http://localhost:8000/api/health"
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止所有服务"

# Trap to kill both on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
