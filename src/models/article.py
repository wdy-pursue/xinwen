from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
import hashlib
import datetime

@dataclass
class Article:
    """文章数据模型"""
    title: str
    content: str
    source: str
    url: str
    publish_time: datetime
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    published: bool = False
    rank: Optional[int] = None  # 新增排名字段
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['publish_time'] = self.publish_time.isoformat()
        data['tags'] = ','.join(self.tags) if self.tags else ''
        return data
    
    @property
    def hash(self) -> str:
        """生成文章哈希值，用于去重"""
        return hashlib.md5(
            (self.title + self.content).encode('utf-8')
        ).hexdigest()
    
    def get_filename(self) -> str:
        """生成文件名"""
        # 使用哈希值前8位作为文件名前缀，避免文件名冲突
        safe_title = ''.join(c if c.isalnum() else '_' for c in self.title[:20])
        # 当rank为None时，使用默认值1
        rank_value = self.rank if self.rank is not None else 1
        # 使用文章的发布时间而不是当前时间
        return f"{self.publish_time.strftime('%Y_%m_%d_%H')}_{self.source}_{rank_value}_{safe_title}_{self.hash[:8]}.txt"

@dataclass
class WechatArticle:
    """微信公众号文章模型"""
    title: str
    content: str
    thumb_media_id: str
    author: str = "公众号运营"
    digest: str = ""
    show_cover_pic: int = 1
    content_source_url: str = ""