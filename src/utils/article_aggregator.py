import logging
from datetime import datetime, timedelta
from typing import List, Dict
from models.article import Article

class ArticleAggregator:
    """文章汇总工具"""
    
    def __init__(self):
        self.logger = logging.getLogger("aggregator")
    
    def aggregate_by_date(self, articles: List[Article], days: int = 1) -> Dict[str, List[Article]]:
        """按日期汇总文章
        
        Args:
            articles: 文章列表
            days: 汇总的天数，默认为1天
            
        Returns:
            按日期汇总的文章字典，格式为 {日期字符串: 文章列表}
        """
        result = {}
        today = datetime.now().date()
        
        # 创建日期范围
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            result[date_str] = []
        
        # 按日期分组文章
        for article in articles:
            article_date = article.publish_time.date()
            date_str = article_date.strftime('%Y-%m-%d')
            
            # 只保留指定天数内的文章
            if (today - article_date).days < days:
                if date_str not in result:
                    result[date_str] = []
                result[date_str].append(article)
        
        return result
    
    def create_daily_digest(self, date_str: str, articles: List[Article]) -> Article:
        """创建每日文章汇总
        
        Args:
            date_str: 日期字符串，格式为'YYYY-MM-DD'
            articles: 当天的文章列表
            
        Returns:
            汇总后的文章对象
        """
        if not articles:
            return None
        
        # 按来源分组
        sources = {}
        for article in articles:
            source = article.source
            if source not in sources:
                sources[source] = []
            sources[source].append(article)
        
        # 创建汇总内容
        title = f"{date_str} 每日热点汇总"
        content = f"# {title}\n\n"
        
        # 添加来源分组内容
        for source, src_articles in sources.items():
            content += f"## {source} 热点 ({len(src_articles)}篇)\n\n"
            
            for idx, article in enumerate(src_articles, 1):
                content += f"{idx}. **{article.title}**\n"
                if article.summary:
                    content += f"   {article.summary[:100]}...\n"
                content += f"   发布时间: {article.publish_time.strftime('%H:%M:%S')}\n\n"
        
        # 创建汇总文章
        digest = Article(
            title=title,
            content=content,
            source="每日汇总",
            url="",  # 无URL
            publish_time=datetime.now(),
            author="系统汇总",
            tags=["每日汇总", "热点", date_str],
            summary=f"{date_str}的热点新闻汇总，共包含{len(articles)}篇文章，来自{len(sources)}个来源。"
        )
        
        return digest