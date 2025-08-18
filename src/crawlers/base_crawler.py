import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from models.article import Article

class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.session = None
        self.logger = logging.getLogger(f"crawler.{name}")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def crawl(self) -> List[Article]:
        """爬取数据，返回文章列表"""
        pass
    
    def should_crawl(self) -> bool:
        """判断是否应该爬取（可用于频率控制）"""
        return self.config.get('enabled', True)