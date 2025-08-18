"""
归档存储 - 保留已发布文章的副本用于Web展示
"""

import os
import json
import shutil
import logging
from typing import List
from datetime import datetime
from models.article import Article

logger = logging.getLogger(__name__)

class ArchiveStorage:
    """归档存储类 - 保留已发布文章的副本"""
    
    def __init__(self, data_dir: str = 'data', archive_dir: str = 'data/archive'):
        self.data_dir = data_dir
        self.archive_dir = archive_dir
        self.logger = logging.getLogger("storage.archive")
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
    
    async def archive_article(self, article: Article) -> bool:
        """归档文章到archive目录"""
        try:
            source_filename = article.get_filename()
            source_path = os.path.join(self.data_dir, source_filename)
            
            if not os.path.exists(source_path):
                self.logger.warning(f"源文件不存在，无法归档: {source_path}")
                return False
            
            # 生成归档文件名，添加时间戳避免冲突
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_filename = f"archived_{timestamp}_{source_filename}"
            archive_path = os.path.join(self.archive_dir, archive_filename)
            
            # 复制文件到归档目录
            shutil.copy2(source_path, archive_path)
            
            # 修改归档文件中的标记
            with open(archive_path, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
            
            article_data['published'] = True
            article_data['archived_time'] = datetime.now().isoformat()
            article_data['original_file'] = source_filename
            
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"文章已归档: {article.title} -> {archive_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"归档文章失败: {e}")
            return False
    
    async def batch_archive_articles(self, articles: List[Article]) -> int:
        """批量归档文章"""
        archived_count = 0
        for article in articles:
            if await self.archive_article(article):
                archived_count += 1
        
        self.logger.info(f"批量归档完成，共归档 {archived_count} 篇文章")
        return archived_count
    
    def get_archive_files(self) -> List[str]:
        """获取所有归档文件"""
        if not os.path.exists(self.archive_dir):
            return []
        
        files = [f for f in os.listdir(self.archive_dir) if f.endswith('.txt')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.archive_dir, x)), reverse=True)
        return files
    
    async def clean_old_archives(self, keep_days: int = 30) -> int:
        """清理旧的归档文件"""
        try:
            if not os.path.exists(self.archive_dir):
                return 0
            
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (keep_days * 24 * 3600)
            
            cleaned_count = 0
            for filename in os.listdir(self.archive_dir):
                if not filename.endswith('.txt'):
                    continue
                
                file_path = os.path.join(self.archive_dir, filename)
                file_time = os.path.getmtime(file_path)
                
                if file_time < cutoff_time:
                    os.remove(file_path)
                    cleaned_count += 1
                    self.logger.info(f"已清理旧归档文件: {filename}")
            
            self.logger.info(f"清理完成，共清理 {cleaned_count} 个旧归档文件")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"清理归档文件失败: {e}")
            return 0
