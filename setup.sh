#!/bin/bash

# Agentic-AI 环境快速设置脚本
# 使用方法: ./setup.sh [local|test|prod] [--non-interactive]

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python环境
check_python() {
    print_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    print_success "Python版本: $python_version"
    
    # 检查版本是否满足要求
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Python版本满足要求 (>= 3.8)"
    else
        print_error "Python版本过低，需要 3.8 或更高版本"
        exit 1
    fi
}

# 检查pip
check_pip() {
    print_info "检查pip..."
    
    if ! python3 -m pip --version &> /dev/null; then
        print_error "pip 未安装，请先安装pip"
        exit 1
    fi
    
    print_success "pip 可用"
}

# 创建虚拟环境（可选）
setup_venv() {
    if [ "$SETUP_VENV" = "true" ]; then
        print_info "设置虚拟环境..."
        
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            print_success "虚拟环境已创建"
        else
            print_info "虚拟环境已存在"
        fi
        
        # 激活虚拟环境
        source venv/bin/activate
        print_success "虚拟环境已激活"
    fi
}

# 显示帮助信息
show_help() {
    echo "Agentic-AI 环境设置脚本"
    echo ""
    echo "使用方法:"
    echo "  ./setup.sh [环境类型] [选项]"
    echo ""
    echo "环境类型:"
    echo "  local    本地开发环境 (默认)"
    echo "  test     测试环境"
    echo "  prod     生产环境"
    echo ""
    echo "选项:"
    echo "  --non-interactive    非交互式模式"
    echo "  --venv              创建并使用虚拟环境"
    echo "  --help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./setup.sh                    # 设置本地开发环境（交互式）"
    echo "  ./setup.sh local --venv       # 设置本地环境并创建虚拟环境"
    echo "  ./setup.sh test --non-interactive  # 非交互式设置测试环境"
}

# 主函数
main() {
    # 默认参数
    ENV_TYPE="local"
    INTERACTIVE="true"
    SETUP_VENV="false"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            local|test|prod)
                ENV_TYPE="$1"
                shift
                ;;
            --non-interactive)
                INTERACTIVE="false"
                shift
                ;;
            --venv)
                SETUP_VENV="true"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_info "开始设置 Agentic-AI $ENV_TYPE 环境..."
    
    # 检查基础环境
    check_python
    check_pip
    
    # 设置虚拟环境（如果需要）
    setup_venv
    
    # 检查Python设置脚本是否存在
    if [ ! -f "scripts/setup_environment.py" ]; then
        print_error "设置脚本不存在: scripts/setup_environment.py"
        exit 1
    fi
    
    # 构建Python命令参数
    python_args="scripts/setup_environment.py setup --env $ENV_TYPE"
    if [ "$INTERACTIVE" = "false" ]; then
        python_args="$python_args --non-interactive"
    fi
    
    # 运行Python设置脚本
    print_info "运行环境设置脚本..."
    if python3 $python_args; then
        print_success "环境设置完成！"
        
        # 显示后续步骤
        echo ""
        print_info "后续步骤:"
        echo "1. 检查环境状态: python3 scripts/setup_environment.py status"
        echo "2. 运行测试: python3 -m pytest tests/ (如果有测试)"
        echo "3. 启动应用: python3 src/mcp/orchestrator.py"
        
        if [ "$SETUP_VENV" = "true" ]; then
            echo ""
            print_warning "记住激活虚拟环境: source venv/bin/activate"
        fi
        
    else
        print_error "环境设置失败"
        exit 1
    fi
}

# 检查是否在项目根目录
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    print_error "请在项目根目录运行此脚本"
    exit 1
fi

# 运行主函数
main "$@"