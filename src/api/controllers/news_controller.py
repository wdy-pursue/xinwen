"""
新闻控制器 - 重构版本
处理新闻相关的API请求
"""

import os
import json
import glob
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import unquote

logger = logging.getLogger(__name__)

class NewsController:
    """新闻控制器类"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        
    def get_vendor_mapping(self) -> Dict[str, str]:
        """获取厂商名称映射"""
        return {
            'weread': '微信读书',
            'zhihu': '知乎',
            'douban': '豆瓣',
            'xiaohongshu': '小红书',
            'nowhots': '今日热榜',
            'toutiao': '今日头条',
            'baidu': '百度',
            'weibo': '微博',
            'douban-group': '豆瓣小组'
        }
    
    def parse_filename_info(self, filename: str) -> Dict[str, Any]:
        """
        解析文件名获取厂商和排名信息
        文件名格式: 2025_08_11_14_weread_1_我在监狱服刑的日子_ecc99523.txt
        返回: {'vendor': 'weread', 'rank': 1, 'vendor_display': '微信读书'}
        """
        try:
            # 移除扩展名并分割
            name_parts = filename.replace('.txt', '').split('_')
            
            # 文件名格式: 年_月_日_时_厂商_排名_标题_ID
            if len(name_parts) >= 6:
                vendor = name_parts[4]  # 厂商标识
                rank = int(name_parts[5]) if name_parts[5].isdigit() else 0  # 排名
                
                # 获取厂商显示名称
                vendor_mapping = self.get_vendor_mapping()
                vendor_display = vendor_mapping.get(vendor, vendor.title())
                
                return {
                    'vendor': vendor,
                    'rank': rank,
                    'vendor_display': vendor_display
                }
        except Exception as e:
            logger.warning(f"解析文件名失败 {filename}: {e}")
        
        return {
            'vendor': 'unknown',
            'rank': 0,
            'vendor_display': '未知来源'
        }
    
    def load_articles_from_files(self) -> List[Dict[str, Any]]:
        """从文件中加载文章数据"""
        articles = []
        
        if not os.path.exists(self.data_dir):
            logger.warning(f"数据目录不存在: {self.data_dir}")
            return articles
        
        try:
            # 获取所有文章文件
            pattern = os.path.join(self.data_dir, '*.txt')
            files = glob.glob(pattern)
            
            # 按文件修改时间倒序排列（最新的在前）
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)
                    
                    # 处理时间格式
                    if 'publish_time' in article_data:
                        try:
                            # 尝试解析ISO格式时间
                            dt = datetime.fromisoformat(
                                article_data['publish_time'].replace('Z', '+00:00')
                            )
                            article_data['publish_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                            article_data['timestamp'] = dt.isoformat()
                        except:
                            pass
                    
                    # 处理标签
                    if 'tags' in article_data and isinstance(article_data['tags'], str):
                        article_data['tags'] = [
                            tag.strip() for tag in article_data['tags'].split(',') if tag.strip()
                        ]
                    
                    # 添加文件信息
                    article_data['file_path'] = file_path
                    article_data['file_name'] = os.path.basename(file_path)
                    
                    # 解析文件名获取厂商信息
                    filename_info = self.parse_filename_info(article_data['file_name'])
                    article_data.update(filename_info)
                    
                    # 如果没有source字段，使用厂商信息
                    if not article_data.get('source'):
                        article_data['source'] = filename_info['vendor_display']
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.error(f"读取文章文件失败 {file_path}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"加载文章数据失败: {e}")
        
        logger.info(f"成功加载 {len(articles)} 篇文章")
        return articles
    
    def filter_articles(self, articles: List[Dict[str, Any]], 
                       search: Optional[str] = None,
                       vendor: Optional[str] = None) -> List[Dict[str, Any]]:
        """筛选文章"""
        filtered_articles = articles.copy()
        
        # 按搜索关键字过滤
        if search:
            search_lower = search.lower()
            filtered_articles = [
                article for article in filtered_articles
                if (search_lower in (article.get('title', '') or '').lower() or
                    search_lower in (article.get('content', '') or '').lower() or
                    search_lower in (article.get('summary', '') or '').lower())
            ]
            logger.info(f"按搜索词 '{search}' 筛选后剩余 {len(filtered_articles)} 篇文章")
        
        # 按厂商过滤
        if vendor:
            filtered_articles = [
                article for article in filtered_articles
                if (article.get('vendor_display', '') == vendor or 
                    article.get('source', '') == vendor)
            ]
            logger.info(f"按厂商 '{vendor}' 筛选后剩余 {len(filtered_articles)} 篇文章")
        
        return filtered_articles
    
    def generate_vendor_stats(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成厂商统计信息"""
        vendor_stats = {}
        
        for article in articles:
            vendor = article.get('vendor_display', '未知来源')
            
            if vendor not in vendor_stats:
                vendor_stats[vendor] = {
                    'count': 0,
                    'articles': []
                }
            
            vendor_stats[vendor]['count'] += 1
            vendor_stats[vendor]['articles'].append(article)
        
        # 对每个厂商的文章按排名排序
        for vendor_info in vendor_stats.values():
            vendor_info['articles'].sort(key=lambda x: x.get('rank', 999))
        
        return vendor_stats
    
    def get_news_list(self, page: int = 1, per_page: int = 20,
                     search: Optional[str] = None,
                     vendor: Optional[str] = None) -> Dict[str, Any]:
        """获取新闻列表"""
        try:
            # 限制每页数量 - 允许获取更多文章用于完整展示
            per_page = min(per_page, 1000)  # 增加限制到1000条
            
            # 加载所有文章
            all_articles = self.load_articles_from_files()
            
            # 筛选文章
            filtered_articles = self.filter_articles(all_articles, search, vendor)
            
            # 分页
            total = len(filtered_articles)
            start = (page - 1) * per_page
            end = start + per_page
            articles_page = filtered_articles[start:end]
            
            # 获取所有厂商列表（从原始数据中获取，确保完整性）
            all_vendor_stats = self.generate_vendor_stats(all_articles)
            vendors = list(all_vendor_stats.keys())
            vendors.sort()
            
            # 生成筛选后的厂商统计
            vendor_stats = self.generate_vendor_stats(filtered_articles)
            
            return {
                'success': True,
                'data': {
                    'articles': articles_page,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page
                    },
                    'vendors': vendors,  # 所有厂商列表
                    'sources': vendors,  # 兼容旧字段
                    'vendor_stats': vendor_stats,  # 当前筛选结果的厂商统计
                    'timestamp': datetime.now().isoformat(),
                    'filters': {
                        'search': search,
                        'vendor': vendor
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"获取新闻列表失败: {e}")
            return {
                'success': False,
                'message': f'获取新闻列表失败: {str(e)}',
                'error': str(e)
            }
    
    def get_news_detail(self, file_name: str) -> Dict[str, Any]:
        """获取新闻详情"""
        try:
            # URL解码文件名以处理中文字符
            decoded_file_name = unquote(file_name)
            file_path = os.path.join(self.data_dir, decoded_file_name)
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': '文章不存在',
                    'error': 'Article not found'
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
            
            # 处理时间格式
            if 'publish_time' in article_data:
                try:
                    dt = datetime.fromisoformat(
                        article_data['publish_time'].replace('Z', '+00:00')
                    )
                    article_data['publish_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    article_data['timestamp'] = dt.isoformat()
                except:
                    pass
            
            # 处理标签
            if 'tags' in article_data and isinstance(article_data['tags'], str):
                article_data['tags'] = [
                    tag.strip() for tag in article_data['tags'].split(',') if tag.strip()
                ]
            
            # 解析文件名信息
            filename_info = self.parse_filename_info(file_name)
            article_data.update(filename_info)
            
            return {
                'success': True,
                'data': article_data
            }
            
        except Exception as e:
            logger.error(f"获取新闻详情失败: {e}")
            return {
                'success': False,
                'message': f'获取新闻详情失败: {str(e)}',
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            articles = self.load_articles_from_files()
            
            # 按厂商统计
            vendor_stats = {}
            for article in articles:
                vendor = article.get('vendor_display', '未知来源')
                vendor_stats[vendor] = vendor_stats.get(vendor, 0) + 1
            
            # 按日期统计（最近7天）
            date_stats = {}
            for article in articles:
                try:
                    publish_time = article.get('publish_time', '')
                    if publish_time:
                        date = datetime.fromisoformat(
                            publish_time.replace('Z', '+00:00')
                        ).strftime('%Y-%m-%d')
                        date_stats[date] = date_stats.get(date, 0) + 1
                except:
                    pass
            
            return {
                'success': True,
                'data': {
                    'total_articles': len(articles),
                    'vendor_stats': vendor_stats,
                    'source_stats': vendor_stats,  # 兼容旧接口
                    'date_stats': dict(sorted(date_stats.items(), reverse=True)[:7]),
                    'last_updated': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                'success': False,
                'message': f'获取统计信息失败: {str(e)}',
                'error': str(e)
            }
    
    def get_news_by_keyword(self, keyword: str) -> Dict[str, Any]:
        """根据关键词获取相关新闻 - 使用与首页搜索相同的逻辑"""
        try:
            # URL解码关键词以处理中文字符
            decoded_keyword = unquote(keyword)
            # 加载所有文章
            articles = self.load_articles_from_files()
            logger.info(f"🔍 搜索关键词: '{decoded_keyword}', 总文章数: {len(articles)}")
            
            # 使用与 filter_articles 相同的逻辑进行搜索
            related_articles = self.filter_articles(articles, search=decoded_keyword)
            
            logger.info(f"关键词 '{decoded_keyword}' 找到 {len(related_articles)} 篇文章")
            
            # 按排名排序
            related_articles.sort(key=lambda x: x.get('rank', 999))
            
            return {
                'success': True,
                'data': {
                    'keyword': decoded_keyword,
                    'total': len(related_articles),
                    'articles': related_articles
                }
            }
            
        except Exception as e:
            logger.error(f"根据关键词获取新闻失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
