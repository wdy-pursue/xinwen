from abc import ABC, abstractmethod
from typing import Dict, Any
from models.article import Article

class BasePublisher(ABC):
    """发布器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def publish(self, article: Article) -> bool:
        """发布文章"""
        pass