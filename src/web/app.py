"""
Flask Web应用主文件 - 重构版本
"""

import os
import sys
from flask import Flask, render_template, jsonify, request
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入重构后的API路由
from src.api.routes.news_routes import news_bp
from src.api.routes.analytics_routes import analytics_bp
from src.api.routes.debug_routes import debug_bp

def create_app():
    """创建Flask应用"""
    # 设置正确的模板和静态文件路径
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir,
                static_url_path='/static')
    
    # 配置
    app.config['SECRET_KEY'] = 'news-crawler-web-2024'
    app.config['JSON_AS_ASCII'] = False  # 支持中文JSON
    
    # 设置CORS响应头和缓存控制
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # 对于静态资源设置缓存控制
        if request.endpoint == 'static':
            # 对于JS和CSS文件，设置较短的缓存时间
            if request.path.endswith(('.js', '.css')):
                response.headers['Cache-Control'] = 'public, max-age=300'  # 5分钟缓存
            else:
                response.headers['Cache-Control'] = 'public, max-age=3600'  # 1小时缓存
        else:
            # 对于HTML页面，禁用缓存
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    # 注册API蓝图
    app.register_blueprint(news_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp)
    app.register_blueprint(debug_bp)
    
    # 主页路由 - 平台名片页面
    @app.route('/')
    def index():
        """主页 - 平台名片页面"""
        return render_template('platform_cards.html')
    
    # 新闻列表页面
    @app.route('/news')
    def news():
        """新闻列表页面"""
        import time
        return render_template('index.html', current_timestamp=int(time.time()))
    
    # 缓存测试页面
    @app.route('/cache-test')
    def cache_test():
        """缓存测试页面"""
        cache_test_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'cache_test.html')
        with open(cache_test_path, 'r', encoding='utf-8') as f:
            content = f.read()
        from flask import Response
        return Response(content, mimetype='text/html')
    
    # 健康检查接口
    @app.route('/health')
    def health():
        """健康检查"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'service': 'news-crawler-web',
            'version': '2.0'
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': '页面未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=False)
