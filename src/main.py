import asyncio
import logging
import os
import sys
from datetime import datetime

# 将父目录添加到Python路径中，以便导入配置文件等
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.file_storage import FileStorage
from services.config_manager import ConfigManager
from services.publisher_manager import PublisherManager
from services.article_service import ArticleService
from services.publish_service import PublishService
# from services.scheduler_service import SchedulerService  # 使用crontab方式，不需要内置调度器
from utils.logger import setup_logger

# 设置日志
setup_logger()
logger = logging.getLogger("main")

class NewsApp:
    """新闻应用主类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # 初始化存储
        storage_config = {
            'data_dir': self.config.get('data_dir', 'data')
        }
        self.storage = FileStorage(storage_config)
        
        # 初始化服务
        self.publisher_manager = PublisherManager(self.config)
        self.article_service = ArticleService(self.storage)
        self.publish_service = PublishService(self.storage, self.publisher_manager, self.config)
        # 注释掉 scheduler，因为使用crontab方式不需要内置定时器
        # self.scheduler = SchedulerService(self.crawl_and_publish)
    
    async def crawl_and_publish(self):
        """爬取并发布文章"""
        try:
            logger.info("开始爬取和发布任务")
            
            # 爬取文章
            crawlers_config = self.config.get('crawlers', {})
            articles = await self.article_service.crawl_articles(crawlers_config)

            # 保存文章
            await self.article_service.save_articles(articles)
            
            # 获取未发布文章
            max_publish = self.config.get('publish_settings', {}).get('max_articles_per_hour', 1)
            unpublished = await self.article_service.get_unpublished_articles(limit=max_publish, current_hour_only=True)

            # 发布到各平台
            await self.publish_service.publish_to_wechat(unpublished)
            await self.publish_service.publish_to_xiaohongshu(unpublished)
            await self.publish_service.send_email_digest()
            
            logger.info("爬取和发布任务完成")
            
        except Exception as e:
            logger.error(f"爬取和发布任务异常: {e}")
    
    async def run_once(self):
        """运行一次爬取和发布"""
        logger.info("开始执行单次爬取和发布任务")
        
        try:
            # 执行爬取和发布
            await self.crawl_and_publish()
            logger.info("爬取和发布任务完成")
            
            # 清理旧数据（根据配置文件）
            data_config = self.config.get('data_management', {})
            if data_config.get('cleanup_enabled', True):
                keep_count = data_config.get('keep_count', 200)
                keep_days = data_config.get('keep_days', 7)
                
                logger.info(f"开始清理旧数据（保留{keep_count}篇文章或{keep_days}天内数据）...")
                deleted_count = await self.storage.cleanup_old_articles(keep_count=keep_count, keep_days=keep_days)
                if deleted_count > 0:
                    logger.info(f"数据清理完成，删除了 {deleted_count} 个旧文件")
                else:
                    logger.info("无需清理数据")
            else:
                logger.info("数据清理已禁用")
                
        except Exception as e:
            logger.error(f"执行爬取和发布任务时出错: {e}")
            raise
    
    # async def run_scheduled(self):
    #     """运行定时任务（已弃用，改用crontab方式）"""
    #     # 先运行一次
    #     await self.run_once()
    #     
    #     # 启动定时任务
    #     await self.scheduler.start_hourly_schedule()
    
    def setup_directories(self):
        """创建必要的目录"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("resources", exist_ok=True)
        os.makedirs("services", exist_ok=True)

async def main_async():
    """异步主函数"""
    logger.info("启动爬虫程序")
    
    app = NewsApp()
    app.setup_directories()
    
    # 只运行一次任务（适用于crontab调度）
    await app.run_once()
    
    logger.info("单次任务执行完成，程序退出")

def main():
    """主函数"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行异常: {e}")

if __name__ == "__main__":
    main()