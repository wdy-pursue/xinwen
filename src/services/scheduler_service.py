import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SchedulerService:
    """调度服务类"""
    
    def __init__(self, task_func):
        self.task_func = task_func
        self.running = False
    
    async def start_hourly_schedule(self):
        """启动每小时定时任务"""
        logger.info("已设置定时任务，每整点执行一次")
        self.running = True
        
        while self.running:
            try:
                # 计算下一个整点的时间
                now = datetime.now()
                next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                sleep_seconds = (next_hour - now).total_seconds()
                
                logger.info(f"等待 {sleep_seconds:.0f} 秒后执行下一次任务（{next_hour.strftime('%Y-%m-%d %H:%M:%S')}）")
                
                # 等待到下一个整点
                await asyncio.sleep(sleep_seconds)
                
                if self.running:
                    # 执行任务
                    logger.info(f"开始执行定时任务: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    await self.task_func()
                
            except Exception as e:
                logger.error(f"定时任务执行异常: {e}")
                # 出错后等待5分钟再重试
                await asyncio.sleep(300)
    
    def stop(self):
        """停止调度"""
        self.running = False
        logger.info("定时任务已停止")