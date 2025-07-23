#!/bin/bash

# 图片批量水印工具安装脚本

set -e  # 遇到错误时停止

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示Logo
show_logo() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🖼️  图片批量水印工具                      ║"
    echo "║                   Image Watermark Tool                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Python版本
check_python() {
    log_info "检查Python环境..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python，请先安装Python 3.7+"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    MIN_VERSION="3.7"
    
    if [ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$MIN_VERSION" ]; then
        log_success "Python版本: $($PYTHON_CMD --version)"
    else
        log_error "Python版本过低，需要Python 3.7+，当前版本: $PYTHON_VERSION"
        exit 1
    fi
}

# 检查pip
check_pip() {
    log_info "检查pip..."
    
    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        log_error "未找到pip，请先安装pip"
        exit 1
    fi
    
    log_success "pip已安装"
}

# 创建虚拟环境
create_venv() {
    log_info "创建虚拟环境..."
    
    if [ -d "venv" ]; then
        log_warning "虚拟环境已存在，跳过创建"
    else
        $PYTHON_CMD -m venv venv
        log_success "虚拟环境创建成功"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log_success "虚拟环境已激活"
    else
        log_error "虚拟环境激活文件不存在"
        exit 1
    fi
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "依赖安装完成"
    else
        log_error "requirements.txt文件不存在"
        exit 1
    fi
}

# 检查核心文件
check_files() {
    log_info "检查核心文件..."
    
    required_files=(
        "watermark_processor.py"
        "watermark_cli.py"
        "watermark_gui.py"
        "demo.py"
        "requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "缺少核心文件: $file"
            exit 1
        fi
    done
    
    log_success "所有核心文件存在"
}

# 创建启动脚本
create_start_scripts() {
    log_info "创建启动脚本..."
    
    # 命令行版本启动脚本
    cat > start_cli.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python watermark_cli.py "$@"
EOF
    chmod +x start_cli.sh
    
    # GUI版本启动脚本
    cat > start_gui.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python watermark_gui.py
EOF
    chmod +x start_gui.sh
    
    # 演示脚本
    cat > start_demo.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python demo.py
EOF
    chmod +x start_demo.sh
    
    log_success "启动脚本创建完成"
}

# 运行基本测试
run_tests() {
    log_info "运行基本测试..."
    
    # 测试导入核心模块
    if python -c "from watermark_processor import WatermarkProcessor; print('核心模块导入成功')" 2>/dev/null; then
        log_success "核心模块测试通过"
    else
        log_error "核心模块测试失败"
        exit 1
    fi
    
    # 测试CLI帮助
    if python watermark_cli.py --help >/dev/null 2>&1; then
        log_success "CLI测试通过"
    else
        log_error "CLI测试失败"
        exit 1
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${CYAN}"
    echo "🎉 安装完成！"
    echo ""
    echo "使用方法："
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🖥️  图形界面版本 (推荐新手)："
    echo "   ./start_gui.sh"
    echo ""
    echo "💻 命令行版本："
    echo "   ./start_cli.sh --help          # 查看帮助"
    echo "   ./start_cli.sh batch -i ./photos -o ./output -w '水印文字'"
    echo ""
    echo "🎬 功能演示："
    echo "   ./start_demo.sh                # 查看各种效果演示"
    echo ""
    echo "📚 更多示例："
    echo "   ./start_cli.sh examples        # 查看使用示例"
    echo "   ./start_cli.sh formats         # 查看支持格式"
    echo ""
    echo "💡 提示："
    echo "   • 建议先运行演示查看效果"
    echo "   • 处理重要图片前请先备份"
    echo "   • 使用预览模式测试参数效果"
    echo -e "${NC}"
}

# 主函数
main() {
    show_logo
    
    log_info "开始安装图片批量水印工具..."
    echo ""
    
    # 检查系统环境
    check_python
    check_pip
    check_files
    
    echo ""
    log_info "开始安装过程..."
    
    # 创建和配置虚拟环境
    create_venv
    activate_venv
    
    # 安装依赖
    install_dependencies
    
    # 创建启动脚本
    create_start_scripts
    
    # 运行测试
    run_tests
    
    echo ""
    log_success "安装成功完成！"
    echo ""
    
    # 显示使用说明
    show_usage
}

# 错误处理
trap 'log_error "安装过程中出现错误，安装失败"' ERR

# 运行主函数
main "$@" 