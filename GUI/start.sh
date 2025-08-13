#!/bin/bash

echo "🚀 启动LLM测试界面..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 安装依赖包..."
    pip install -r requirements.txt
fi

# 启动应用
echo "🌐 启动Streamlit应用..."
echo "📱 应用将在 http://localhost:8501 启动"
echo "🛑 按 Ctrl+C 停止应用"
echo ""

streamlit run app.py --server.port=8501
