import logging
from typing import List
from datetime import datetime

from models.article import Article
from storage.file_storage import FileStorage
from services.crawler_factory import CrawlerFactory
from utils.article_aggregator import ArticleAggregator

logger = logging.getLogger(__name__)

class ArticleService:
    """文章服务类"""
    
    def __init__(self, storage: FileStorage):
        self.storage = storage
        self.aggregator = ArticleAggregator()
    
    async def crawl_articles(self, crawlers_config: dict) -> List[Article]:
        """爬取文章"""
        all_articles = []
        
        for name, crawler_config in crawlers_config.items():
            if not crawler_config.get('enabled', True):
                continue

            crawler_type = crawler_config.get('type')
            crawler = CrawlerFactory.create_crawler(crawler_type, name, crawler_config)

            if not crawler:
                continue

            try:
                async with crawler:
                    articles = await crawler.crawl()
                    logger.info(f"爬虫 {name} 获取到 {len(articles)} 篇文章")
                    all_articles.extend(articles)
            except Exception as e:
                logger.error(f"爬虫 {name} 运行异常: {e}")
        
        return all_articles
    
    async def save_articles(self, articles: List[Article]) -> int:
        """保存文章"""
        saved_count = 0
        for article in articles:
            if await self.storage.save_article(article):
                saved_count += 1
        
        logger.info(f"共保存 {saved_count} 篇新文章")
        return saved_count
    
    async def get_unpublished_articles(self, limit: int = 10, current_hour_only: bool = False) -> List[Article]:
        """获取未发布文章"""
        return await self.storage.get_unpublished_articles(limit=limit, current_hour_only=current_hour_only)