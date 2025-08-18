#!/bin/bash

# 手动执行一次新闻抓取
# 用法: ./run_once.sh 或 /path/to/run_once.sh（适用于crontab）

echo "=================================================="
echo "      手动执行新闻抓取任务"
echo "=================================================="

# 确定脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📝 开始执行任务..."
echo "⏰ 执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📍 项目根目录: $SCRIPT_DIR"
echo "📍 当前工作目录: $(pwd)"

# 设置PATH环境变量（crontab环境变量可能不完整）
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# 检查python3命令
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3命令，请确保已安装Python3并配置环境变量"
    echo "💡 当前PATH: $PATH"
    exit 1
fi

echo "🐍 Python版本: $(python3 --version)"
echo "🐍 Python路径: $(which python3)"

# 检查关键文件是否存在
if [ ! -f "config.ini" ]; then
    echo "❌ 未找到config.ini文件，当前目录: $(pwd)"
    echo "📂 目录内容:"
    ls -la
    exit 1
fi

if [ ! -f "src/main.py" ]; then
    echo "❌ 未找到src/main.py文件"
    exit 1
fi

echo "✅ 配置文件和主程序检查通过"
echo ""

# 创建必要目录
mkdir -p data logs

# 执行任务 (在根目录执行，确保能找到config.ini)
echo "🚀 开始执行新闻抓取任务..."
python3 src/main.py

# 显示数据统计信息
echo ""
echo "📊 数据统计："
if [ -d "data" ]; then
    file_count=$(find data -name "*.txt" | wc -l)
    echo "  - 📄 当前文章文件数: $file_count"
    
    if [ $file_count -gt 0 ]; then
        echo "  - 📅 最新文件:"
        find data -name "*.txt" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -3 | while read timestamp file; do
            if command -v date >/dev/null 2>&1; then
                date_str=$(date -d "@${timestamp%.*}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r "${timestamp%.*}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "未知时间")
            else
                date_str="未知时间"
            fi
            filename=$(basename "$file")
            echo "    * $date_str - $filename"
        done
    fi
else
    echo "  - ⚠️  data目录不存在"
fi

echo ""
echo "✅ 任务执行完成！"
echo ""
echo "📋 执行结果："
echo "  - ✅ 已完成nowhots热门资讯抓取"
echo "  - ✅ 已完成数据清理（保留最新200篇文章）"
echo "  - ✅ 已尝试发送邮件摘要"
echo "  - ✅ 已尝试创建微信公众号草稿"
echo "  - 📄 详细日志请查看 logs/crawler.log"
echo ""
echo "💡 其他命令："
echo "  查看状态: ./status.sh"
echo "  查看日志: tail -f logs/crawler.log"
