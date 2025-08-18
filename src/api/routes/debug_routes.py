"""
调试API路由 - 用于调试关键词搜索问题
"""

from flask import Blueprint, jsonify, request
from ..controllers.news_controller import NewsController
from ..controllers.analytics_controller import AnalyticsController

# 创建蓝图
debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')

# 创建控制器实例
news_controller = NewsController()
analytics_controller = AnalyticsController()

@debug_bp.route('/keywords', methods=['GET'])
def debug_keywords():
    """调试关键词提取"""
    try:
        # 获取分析数据
        analytics_data = analytics_controller.get_analytics_data()
        
        if not analytics_data['success']:
            return jsonify(analytics_data), 500
        
        keywords = analytics_data['data']['keywords'][:10]  # 前10个关键词
        
        # 获取所有新闻
        news_data = news_controller.get_news_list(page=1, per_page=1000)
        articles = news_data['data']['articles'] if news_data['success'] else []
        
        # 为每个关键词查找匹配的新闻
        debug_info = []
        for keyword in keywords:
            keyword_name = keyword['name']
            matches = []
            
            for article in articles:
                title = str(article.get('title', ''))
                content = str(article.get('content', ''))
                summary = str(article.get('summary', ''))
                
                if (keyword_name.lower() in title.lower() or 
                    keyword_name.lower() in content.lower() or 
                    keyword_name.lower() in summary.lower()):
                    matches.append({
                        'title': title,
                        'source': article.get('vendor_display', ''),
                        'rank': article.get('rank', 999)
                    })
            
            debug_info.append({
                'keyword': keyword_name,
                'frequency': keyword['value'],
                'matches_count': len(matches),
                'sample_matches': matches[:3]  # 前3个匹配示例
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_articles': len(articles),
                'total_keywords': len(keywords),
                'debug_info': debug_info
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debug_bp.route('/search/<keyword>', methods=['GET'])
def debug_search(keyword):
    """调试单个关键词搜索"""
    try:
        result = news_controller.get_news_by_keyword(keyword)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debug_bp.route('/articles/sample', methods=['GET'])
def debug_articles_sample():
    """获取文章样本用于调试"""
    try:
        news_data = news_controller.get_news_list(page=1, per_page=5)
        
        if not news_data['success']:
            return jsonify(news_data), 500
        
        articles = news_data['data']['articles']
        
        # 返回文章的关键信息
        sample_data = []
        for article in articles:
            sample_data.append({
                'title': article.get('title', ''),
                'content_preview': str(article.get('content', ''))[:100] + '...',
                'summary_preview': str(article.get('summary', ''))[:100] + '...',
                'source': article.get('vendor_display', ''),
                'rank': article.get('rank', 999),
                'file_name': article.get('file_name', '')
            })
        
        return jsonify({
            'success': True,
            'data': {
                'sample_articles': sample_data,
                'total_articles': news_data['data']['total']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
