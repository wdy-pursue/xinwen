"""
新闻API路由模块
"""

from flask import Blueprint, jsonify, request
from ..controllers.news_controller import NewsController

# 创建蓝图
news_bp = Blueprint('news', __name__)

# 创建控制器实例
news_controller = NewsController()

@news_bp.route('/news', methods=['GET'])
def get_news_list():
    """获取新闻列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        vendor = request.args.get('vendor', '', type=str)
        
        result = news_controller.get_news_list(page, per_page, search, vendor)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_bp.route('/news/<path:file_name>', methods=['GET'])
def get_news_detail(file_name):
    """获取新闻详情"""
    try:
        result = news_controller.get_news_detail(file_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_bp.route('/stats', methods=['GET'])
def get_news_stats():
    """获取新闻统计信息"""
    try:
        result = news_controller.get_stats()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_bp.route('/news/by-keyword/<keyword>', methods=['GET'])
def get_news_by_keyword(keyword):
    """根据关键词获取相关新闻"""
    try:
        result = news_controller.get_news_by_keyword(keyword)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500