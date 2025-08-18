"""
Web服务器启动脚本
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上一级目录才是项目根目录
sys.path.insert(0, project_root)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """主函数"""
    print("🌐 启动新闻可视化Web服务器...")
    print(f"📍 项目根目录: {project_root}")
    
    # 确保必要目录存在
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    try:
        # 导入Flask应用（确保在项目根目录下运行）
        os.chdir(project_root)  # 切换到项目根目录
        from src.web.app import create_app
        
        app = create_app()
        
        # 使用8080端口，避免与nginx冲突
        port = 8080
        print(f"🚀 在端口 {port} 启动服务器...")
        print(f"📱 本地访问: http://localhost:{port}")
        print(f"📱 远程访问: http://你的服务器IP:{port}")
        print("💡 通过nginx代理可访问80端口")
        print("⏹️  按 Ctrl+C 停止服务器")
        print("")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请检查依赖是否正确安装")
        sys.exit(1)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {port} 已被占用")
            print("请停止其他Web服务或使用其他端口")
        else:
            print(f"❌ 系统错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
