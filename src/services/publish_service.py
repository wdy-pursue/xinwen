import logging
from typing import List, Dict, Any
from datetime import datetime

from models.article import Article
from storage.file_storage import FileStorage
from services.publisher_manager import PublisherManager
from utils.article_aggregator import ArticleAggregator

logger = logging.getLogger(__name__)

class PublishService:
    """发布服务类"""
    
    def __init__(self, storage: FileStorage, publisher_manager: PublisherManager, config: Dict[str, Any]):
        self.storage = storage
        self.publisher_manager = publisher_manager
        self.config = config
        self.aggregator = ArticleAggregator()
    
    async def publish_to_wechat(self, articles: List[Article]) -> int:
        """发布到微信"""
        if not self._is_enabled('wechat'):
            return 0

        publisher = self.publisher_manager.get_publisher('wechat')
        if not publisher:
            return 0
        
        # 检查是否启用汇总模式
        digest_mode = self.config.get('wechat', {}).get('digest_mode', False)
        
        # 检查是否需要保留Web数据
        preserve_for_web = self.config.get('web', {}).get('preserve_data', True)
        
        if digest_mode:
            # 汇总模式：将所有文章作为列表传递给发布器
            try:
                if await publisher.publish(articles):
                    # 汇总发布成功
                    if not preserve_for_web:
                        # 删除所有文章
                        deleted_count = 0
                        for article in articles:
                            if await self.storage.delete_article(article):
                                deleted_count += 1
                        logger.info(f"微信汇总发布成功，共 {len(articles)} 篇文章，已删除 {deleted_count} 个文件")
                    else:
                        logger.info(f"微信汇总发布成功，共 {len(articles)} 篇文章，Web数据保留模式启用，跳过删除文件")
                    return len(articles)
                else:
                    logger.error(f"微信汇总发布失败，共 {len(articles)} 篇文章")
                    return 0
            except Exception as e:
                logger.error(f"微信汇总发布异常: 共 {len(articles)} 篇文章, 错误: {e}")
                return 0
        else:
            # 单篇发布模式：逐个发布文章
            published_count = 0
            for article in articles:
                try:
                    # 将单个文章包装成列表传递
                    if await publisher.publish([article]):
                        if not preserve_for_web:
                            await self.storage.delete_article(article)
                        published_count += 1
                        logger.info(f"微信发布成功: {article.title}")
                    else:
                        logger.error(f"微信发布失败: {article.title}")
                except Exception as e:
                    logger.error(f"微信发布异常: {article.title}, 错误: {e}")
            
            if preserve_for_web:
                logger.info(f"微信共发布 {published_count} 篇文章，Web数据保留模式启用，跳过删除文件")
            else:
                logger.info(f"微信共发布 {published_count} 篇文章")
            return published_count
    
    async def publish_to_xiaohongshu(self, articles: List[Article]) -> int:
        """发布到小红书"""
        if not self._is_enabled('xiaohongshu'):
            return 0
        
        publisher = self.publisher_manager.get_publisher('xiaohongshu')
        if not publisher:
            return 0
        
        # 按日期汇总文章
        date_articles = self.aggregator.aggregate_by_date(articles, days=1)
        published_count = 0
        
        # 检查是否需要保留Web数据
        preserve_for_web = self.config.get('web', {}).get('preserve_data', True)
        
        for date_str, date_articles_list in date_articles.items():
            if not date_articles_list:
                continue
            
            digest = self.aggregator.create_daily_digest(date_str, date_articles_list)
            if not digest:
                continue
            
            if await publisher.publish(digest):
                logger.info(f"小红书发布成功: {digest.title}")
                if not preserve_for_web:
                    for article in date_articles_list:
                        await self.storage.delete_article(article)
                    logger.info(f"已删除 {len(date_articles_list)} 个文章文件")
                else:
                    logger.info(f"Web数据保留模式启用，跳过删除 {len(date_articles_list)} 个文章文件")
                published_count += len(date_articles_list)
            else:
                logger.error(f"小红书发布失败: {digest.title}")
        
        return published_count
    
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
            
            # 检查是否需要保留Web数据
            preserve_for_web = self.config.get('web', {}).get('preserve_data', True)
            
            if not preserve_for_web:
                # 删除文章文件
                deleted_count = 0
                for article in recent_articles:
                    if await self.storage.delete_article(article):
                        deleted_count += 1
                
                logger.info(f"已删除 {deleted_count} 个文章文件")
            else:
                logger.info(f"Web数据保留模式启用，跳过删除 {len(recent_articles)} 个文章文件")
            
            return True
        else:
            logger.error(f"邮件发送失败: {subject}")
            return False
    
    def _is_enabled(self, platform: str) -> bool:
        """检查平台是否启用"""
        return self.config.get(platform, {}).get('enabled', False)