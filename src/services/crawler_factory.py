import logging
from typing import Dict, Type, Optional

from crawlers.base_crawler import BaseCrawler
from crawlers.rss_crawler import RSSCrawler
from crawlers.zhihu_crawler import ZhihuColumnCrawler
from crawlers.nowhots_crawler import NowHotsCrawler

logger = logging.getLogger(__name__)

class CrawlerFactory:
    """爬虫工厂类"""
    
    _crawler_map: Dict[str, Type[BaseCrawler]] = {
        "RSSCrawler": RSSCrawler,
        "ZhihuCrawler": ZhihuColumnCrawler,
        "NowHotsCrawler": NowHotsCrawler,
    }
    
    @classmethod
    def create_crawler(cls, crawler_type: str, name: str, config: dict) -> Optional[BaseCrawler]:
        """创建爬虫实例"""
        crawler_class = cls._crawler_map.get(crawler_type)
        if not crawler_class:
            logger.error(f"未知的爬虫类型: {crawler_type}")
            return None
        
        return crawler_class(name, config)
    
    @classmethod
    def register_crawler(cls, crawler_type: str, crawler_class: Type[BaseCrawler]):
        """注册新的爬虫类型"""
        cls._crawler_map[crawler_type] = crawler_class