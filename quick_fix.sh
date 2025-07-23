#!/bin/bash

# MacBook Air 安卓手机远程控制器 - 快速修复脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

print_success() {
    print_message "✅ $1" $GREEN
}

print_error() {
    print_message "❌ $1" $RED
}

print_warning() {
    print_message "⚠️ $1" $YELLOW
}

print_info() {
    print_message "ℹ️ $1" $BLUE
}

echo "🔧 MacBook Air 安卓手机远程控制器 - 快速修复"
echo "==============================================="
echo ""

# 1. 修复 ADB 路径问题
print_info "步骤 1: 修复 ADB 路径配置..."

# 检查 ADB 是否已安装但不在 PATH 中
if ! command -v adb &> /dev/null; then
    # 查找 ADB 安装位置
    ADB_PATHS=(
        "/opt/homebrew/Caskroom/android-platform-tools/*/platform-tools"
        "/usr/local/Caskroom/android-platform-tools/*/platform-tools"
        "/opt/homebrew/bin"
        "/usr/local/bin"
    )
    
    ADB_FOUND=""
    for path in "${ADB_PATHS[@]}"; do
        if [[ -f "$path/adb" ]]; then
            ADB_FOUND="$path"
            break
        fi
    done
    
    if [[ -n "$ADB_FOUND" ]]; then
        print_success "找到 ADB: $ADB_FOUND/adb"
        
        # 添加到当前会话
        export PATH="$PATH:$ADB_FOUND"
        
        # 添加到配置文件
        if [[ -f ~/.zshrc ]]; then
            if ! grep -q "$ADB_FOUND" ~/.zshrc; then
                echo "export PATH=\"\$PATH:$ADB_FOUND\"" >> ~/.zshrc
                print_success "已添加 ADB 到 ~/.zshrc"
            fi
        fi
        
        if [[ -f ~/.bash_profile ]]; then
            if ! grep -q "$ADB_FOUND" ~/.bash_profile; then
                echo "export PATH=\"\$PATH:$ADB_FOUND\"" >> ~/.bash_profile
                print_success "已添加 ADB 到 ~/.bash_profile"
            fi
        fi
        
        if [[ -f ~/.zprofile ]]; then
            if ! grep -q "$ADB_FOUND" ~/.zprofile; then
                echo "export PATH=\"\$PATH:$ADB_FOUND\"" >> ~/.zprofile
                print_success "已添加 ADB 到 ~/.zprofile"
            fi
        fi
    else
        print_warning "未找到 ADB，正在重新安装..."
        brew install --cask android-platform-tools
    fi
else
    print_success "ADB 已在 PATH 中"
fi

# 2. 验证 ADB 工作
print_info "步骤 2: 验证 ADB 工作状态..."
if command -v adb &> /dev/null; then
    adb_version=$(adb --version 2>/dev/null | head -n1)
    print_success "ADB 工作正常: $adb_version"
    
    # 启动 ADB 服务
    adb start-server 2>/dev/null
    print_success "ADB 服务已启动"
else
    print_error "ADB 仍然不可用"
    exit 1
fi

# 3. 验证 scrcpy
print_info "步骤 3: 验证 scrcpy..."
if command -v scrcpy &> /dev/null; then
    print_success "scrcpy 已安装"
else
    print_warning "scrcpy 未找到，正在安装..."
    brew install scrcpy
fi

# 4. 验证 Python 依赖
print_info "步骤 4: 验证 Python 依赖..."
if [[ -f "requirements.txt" ]]; then
    print_info "安装 Python 依赖..."
    
    # 检查是否需要创建虚拟环境
    if [[ ! -d "venv" ]]; then
        print_info "创建 Python 虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境已创建"
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    deactivate
    
    print_success "Python 依赖已安装到虚拟环境"
else
    print_warning "未找到 requirements.txt 文件"
fi

# 5. 检查设备连接
print_info "步骤 5: 检查设备连接..."
devices=$(adb devices 2>/dev/null | grep -v "List of devices attached" | grep -v "^$")
if [[ -n "$devices" ]]; then
    print_success "检测到安卓设备:"
    echo "$devices"
else
    print_warning "未检测到安卓设备"
    print_info "请确保:"
    echo "  1. 安卓设备已通过 USB 连接"
    echo "  2. 已启用 USB 调试模式"
    echo "  3. 已授权此计算机"
fi

# 6. 创建便捷启动脚本
print_info "步骤 6: 创建便捷启动脚本..."

# 创建命令行版本启动脚本
cat > start_cli.sh << 'EOF'
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

echo "🚀 启动命令行版本..."
python3 main.py
EOF

# 创建 Web 版本启动脚本
cat > start_web.sh << 'EOF'
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
EOF

# 创建演示脚本
cat > start_demo.sh << 'EOF'
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

echo "🎮 启动功能演示..."
python3 demo.py
EOF

# 设置执行权限
chmod +x start_cli.sh start_web.sh start_demo.sh

print_success "已创建启动脚本:"
echo "  - start_cli.sh   (命令行版本)"
echo "  - start_web.sh   (Web版本)"
echo "  - start_demo.sh  (功能演示)"

echo ""
print_success "🎉 修复完成!"
echo ""
echo "使用方法:"
echo "  命令行版本: ./start_cli.sh"
echo "  Web 版本:   ./start_web.sh"
echo "  功能演示:   ./start_demo.sh"
echo ""
echo "如果还有问题，请:"
echo "  1. 重新打开终端窗口"
echo "  2. 运行 'source ~/.zprofile'"
echo "  3. 确保安卓设备已连接并启用USB调试" 