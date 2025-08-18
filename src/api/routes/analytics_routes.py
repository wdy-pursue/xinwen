"""
数据分析API路由
"""

from flask import Blueprint, jsonify, request
from ..controllers.analytics_controller import AnalyticsController

# 创建蓝图
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')

# 创建控制器实例
analytics_controller = AnalyticsController()

@analytics_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """获取数据分析信息"""
    try:
        result = analytics_controller.get_analytics_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/keywords', methods=['GET'])
def get_keywords():
    """获取关键词分析"""
    try:
        limit = request.args.get('limit', 50, type=int)
        result = analytics_controller.get_keywords_analysis(limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/trends', methods=['GET'])
def get_trends():
    """获取趋势分析"""
    try:
        result = analytics_controller.get_trends_analysis()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
