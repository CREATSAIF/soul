#!/bin/bash
cd "$(dirname "$0")"

# 确保 ADB 在 PATH 中
if ! command -v adb &> /dev/null; then
    # 查找 ADB
    for path in /opt/homebrew/Caskroom/android-platform-tools/*/platform-tools /usr/local/Caskroom/android-platform-tools/*/platform-tools; do
        if [[ -f "$path/adb" ]]; then
            export PATH="$PATH:$path"
            break
        fi
    done
fi

# 激活虚拟环境（如果存在）
if [[ -d "venv" ]]; then
    source venv/bin/activate
fi

echo "🌐 启动 Web 版本..."
echo "请在浏览器中访问: http://localhost:5000"
python3 web_interface.py
