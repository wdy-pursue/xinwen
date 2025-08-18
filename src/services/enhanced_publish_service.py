"""
增强发布服务 - 支持归档模式
"""

import logging
from typing import List
from datetime import datetime
from models.article import Article
from storage.file_storage import FileStorage
from storage.archive_storage import ArchiveStorage
from services.publisher_manager import PublisherManager

logger = logging.getLogger(__name__)

class EnhancedPublishService:
    """增强发布服务类 - 支持数据保留"""
    
    def __init__(self, storage: FileStorage, publisher_manager: PublisherManager, config: dict):
        self.storage = storage
        self.publisher_manager = publisher_manager
        self.config = config
        
        # 初始化归档存储
        self.archive_storage = ArchiveStorage()
        
        # 是否保留原始数据用于Web展示
        self.preserve_for_web = config.get('web', {}).get('preserve_data', True)
        
    async def publish_all(self) -> dict:
        """发布所有启用的平台"""
        results = {}
        
        # 获取未发布的文章
        articles = await self.storage.get_unpublished_articles(limit=200)
        
        if not articles:
            logger.info("没有待发布的文章")
            return results
        
        logger.info(f"开始发布流程，共 {len(articles)} 篇文章")
        
        # 发布到微信
        if self._is_enabled('wechat'):
            results['wechat'] = await self.publish_to_wechat(articles)
        
        # 发送邮件摘要
        if self._is_enabled('email'):
            results['email'] = await self.send_email_digest()
        
        logger.info(f"发布完成: {results}")
        return results
    
    async def publish_to_wechat(self, articles: List[Article]) -> int:
        """发布到微信公众号"""
        if not self._is_enabled('wechat'):
            return 0
        
        publisher = self.publisher_manager.get_publisher('wechat')
        if not publisher:
            return 0
        
        # 发布汇总文章
        if await publisher.send_digest(articles, f"{datetime.now().strftime('%Y-%m-%d %H:%M')} 热点资讯汇总"):
            logger.info(f"微信汇总发布成功，共 {len(articles)} 篇文章")
            
            # 如果保留Web数据，先归档再删除
            if self.preserve_for_web:
                await self.archive_storage.batch_archive_articles(articles)
            
            # 删除原始文件
            deleted_count = 0
            for article in articles:
                if await self.storage.delete_article(article):
                    deleted_count += 1
            
            logger.info(f"已删除 {deleted_count} 个原始文件")
            return len(articles)
        
        return 0
    
    async def send_email_digest(self) -> bool:
        """发送邮件摘要"""
        if not self._is_enabled('email'):
            return False
        
        publisher = self.publisher_manager.get_publisher('email')
        if not publisher:
            return False
        
        # 获取当前小时的未发布文章
        recent_articles = await self.storage.get_unpublished_articles(
            limit=200,
            current_hour_only=True
        )
        
        min_articles = self.config.get('email', {}).get('min_articles', 1)
        
        if len(recent_articles) < min_articles:
            logger.info(f"文章数量不足({len(recent_articles)})，未发送邮件")
            return False
        
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        subject = f"{date_str} 每小时新闻汇总"
        
        if await publisher.send_digest(recent_articles, subject):
            logger.info(f"邮件发送成功: {subject}, 共 {len(recent_articles)} 篇文章")
            
            # 如果保留Web数据，先归档再删除
            if self.preserve_for_web:
                await self.archive_storage.batch_archive_articles(recent_articles)
            
            # 删除原始文件
            deleted_count = 0
            for article in recent_articles:
                if await self.storage.delete_article(article):
                    deleted_count += 1
            
            logger.info(f"已删除 {deleted_count} 个原始文件")
            return True
        else:
            logger.error(f"邮件发送失败: {subject}")
            return False
    
    def _is_enabled(self, platform: str) -> bool:
        """检查平台是否启用"""
        return self.config.get(platform, {}).get('enabled', False)
