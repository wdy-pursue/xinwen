from abc import ABC, abstractmethod
from typing import List, Optional
from models.article import Article

class BaseStorage(ABC):
    """存储基类"""
    
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    async def save_article(self, article: Article) -> bool:
        """保存文章"""
        pass
    
    @abstractmethod
    async def get_unpublished_articles(self, limit: int = 10, current_hour_only: bool = False) -> List[Article]:
        """获取未发布的文章"""
        pass
    
    @abstractmethod
    async def delete_article(self, article: Article) -> bool:
        """删除文章"""
        pass
    
    @abstractmethod
    async def article_exists(self, article: Article) -> bool:
        """检查文章是否已存在"""
        pass