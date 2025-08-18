#!/bin/bash

# 新闻Web服务管理脚本
# 支持 start, stop, status, restart 命令

# 配置
PID_FILE="logs/web_server.pid"
LOG_FILE="logs/web_server.log"
PYTHON_SCRIPT="src/web_server.py"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查Python环境
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
        log_debug "使用Python: $(which python3)"
        return 0
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
        log_debug "使用Python: $(which python)"
        return 0
    else
        log_error "未找到Python环境"
        return 1
    fi
}

# 检查依赖
check_dependencies() {
    log_debug "检查依赖..."
    
    # 检查Flask
    if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
        log_error "Flask未安装，请运行: pip install flask"
        return 1
    fi
    
    # 检查必要文件
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_error "Web服务器脚本不存在: $PYTHON_SCRIPT"
        return 1
    fi
    
    log_debug "依赖检查通过"
    return 0
}

# 获取进程状态
get_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "running"
            return 0
        else
            rm -f "$PID_FILE"
            echo "stopped"
            return 1
        fi
    else
        echo "stopped"
        return 1
    fi
}

# 启动服务
start_server() {
    local status=$(get_status)
    
    if [ "$status" = "running" ]; then
        log_warn "Web服务器已在运行中 (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    log_info "启动新闻可视化Web服务器..."
    
    # 检查环境
    if ! check_python || ! check_dependencies; then
        return 1
    fi
    
    # 确保日志目录存在
    mkdir -p logs
    mkdir -p data
    
    # 生成测试数据（如果data目录为空）
    if [ ! "$(ls -A data)" ]; then
        log_info "生成测试数据..."
        cat > "data/system_start.txt" << EOF
{
    "title": "系统启动测试",
    "content": "Web服务器已成功启动，这是一条测试新闻。",
    "summary": "系统启动测试消息",
    "source": "系统",
    "vendor_display": "系统",
    "vendor": "system",
    "rank": 1,
    "publish_time": "$(date -Iseconds)",
    "timestamp": "$(date -Iseconds)"
}
EOF
        log_debug "测试数据生成完成"
    fi
    
    # 启动服务器
    nohup $PYTHON_CMD "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
    local server_pid=$!
    
    # 保存PID
    echo $server_pid > "$PID_FILE"
    
    # 等待启动
    sleep 2
    
    # 验证启动
    if kill -0 "$server_pid" 2>/dev/null; then
        log_info "✅ Web服务器启动成功"
        log_info "📱 访问地址: http://localhost:8080"
        log_info "📱 通过nginx访问: http://localhost"
        log_info "📋 进程ID: $server_pid"
        log_info "📄 日志文件: $LOG_FILE"
        return 0
    else
        log_error "Web服务器启动失败"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 停止服务
stop_server() {
    local status=$(get_status)
    
    if [ "$status" = "stopped" ]; then
        log_warn "Web服务器未运行"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    log_info "停止Web服务器 (PID: $pid)..."
    
    # 发送TERM信号
    if kill -TERM "$pid" 2>/dev/null; then
        # 等待进程退出
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # 如果仍在运行，强制杀死
        if kill -0 "$pid" 2>/dev/null; then
            log_warn "进程未响应TERM信号，发送KILL信号"
            kill -KILL "$pid" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        log_info "✅ Web服务器已停止"
        return 0
    else
        log_error "停止服务器失败"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 显示状态
show_status() {
    local status=$(get_status)
    
    echo "🌐 新闻Web服务器状态"
    echo "===================="
    
    if [ "$status" = "running" ]; then
        local pid=$(cat "$PID_FILE")
        log_info "状态: 运行中"
        echo "📋 进程ID: $pid"
        echo "📱 访问地址: http://localhost:8080"
        echo "📄 日志文件: $LOG_FILE"
        
        # 检查端口
        if command -v netstat >/dev/null 2>&1; then
            local port_info=$(netstat -tlnp 2>/dev/null | grep ":8080 " | head -1)
            if [ -n "$port_info" ]; then
                echo "🔌 端口状态: 8080端口已监听"
            else
                log_warn "8080端口未监听"
            fi
        fi
        
        # 显示最近日志
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "📄 最近日志:"
            tail -5 "$LOG_FILE" | sed 's/^/    /'
        fi
    else
        log_warn "状态: 未运行"
        
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "📄 最近日志:"
            tail -5 "$LOG_FILE" | sed 's/^/    /'
        fi
    fi
}

# 重启服务
restart_server() {
    log_info "重启Web服务器..."
    stop_server
    sleep 2
    start_server
}

# 显示帮助
show_help() {
    echo "新闻Web服务管理脚本"
    echo ""
    echo "用法:"
    echo "  $0 start    - 启动Web服务器"
    echo "  $0 stop     - 停止Web服务器"
    echo "  $0 status   - 显示服务器状态"
    echo "  $0 restart  - 重启Web服务器"
    echo "  $0 help     - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 restart"
}

# 主逻辑
case "${1:-start}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    status)
        show_status
        ;;
    restart)
        restart_server
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
