import os
import json
import logging
from typing import List, Dict, Set
from datetime import datetime
from models.article import Article
from storage.base_storage import BaseStorage

class FileStorage(BaseStorage):
    """文件存储实现"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.data_dir = config.get('data_dir', 'data')
        self.logger = logging.getLogger("storage.file")
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def save_article(self, article: Article) -> bool:
        """保存文章到文件"""
        try:
            # 检查文章是否已存在
            if await self.article_exists(article):
                self.logger.info(f"文章已存在: {article.title}")
                return False
            
            # 生成文件路径
            filename = article.get_filename()
            filepath = os.path.join(self.data_dir, filename)
            
            # 保存文章内容
            article_data = article.to_dict()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"文章已保存: {article.title}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存文章失败: {e}")
            return False
    
    async def get_unpublished_articles(self, limit: int = 10, current_hour_only: bool = False) -> List[Article]:
        """获取未发布的文章
        
        Args:
            limit: 返回文章数量限制
            current_hour_only: 是否只获取当前小时的文章
        """
        articles = []
        count = 0
        
        # 如果需要筛选当前小时，生成当前小时的前缀
        current_hour_prefix = None
        if current_hour_only:
            current_hour_prefix = datetime.now().strftime('%Y_%m_%d_%H')
        
        try:
            for filename in os.listdir(self.data_dir):
                if not filename.endswith('.txt'):
                    continue
                
                # 如果需要筛选当前小时，检查文件名是否以当前小时开头
                if current_hour_only and not filename.startswith(current_hour_prefix):
                    continue
                
                filepath = os.path.join(self.data_dir, filename)
                
                # 从文件名中解析rank
                # 文件名格式: YYYY_MM_DD_HH_source_rank_title_hash.txt
                try:
                    parts = filename.replace('.txt', '').split('_')
                    if len(parts) >= 6:
                        rank = int(parts[5])  # rank在第6个位置（索引5）
                    else:
                        rank = 1  # 默认值
                except (ValueError, IndexError):
                    rank = 1  # 解析失败时使用默认值
                
                # 读取文章内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    article_data = json.load(f)
        
                # 创建文章对象，包含rank字段
                article = Article(
                    title=article_data['title'],
                    content=article_data['content'],
                    source=article_data['source'],
                    url=article_data['url'],
                    publish_time=datetime.fromisoformat(article_data['publish_time']),
                    author=article_data.get('author'),
                    tags=article_data.get('tags', '').split(',') if article_data.get('tags') else [],
                    summary=article_data.get('summary'),
                    published=False,
                    rank=rank  # 设置从文件名解析出的rank
                )
        
                articles.append(article)
                count += 1
        
                if count >= limit:
                    break
        
        except Exception as e:
            self.logger.error(f"获取未发布文章失败: {e}")
        
        return articles
    
    async def delete_article(self, article: Article) -> bool:
        """删除文章文件"""
        try:
            filename = article.get_filename()
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"文章文件已删除: {article.title}")
                return True
            else:
                self.logger.warning(f"文章文件不存在: {filepath}")
                return False
        
        except Exception as e:
            self.logger.error(f"删除文章文件失败: {e}")
            return False
    
    async def article_exists(self, article: Article) -> bool:
        """检查文章是否已存在"""
        # 检查文件是否存在
        filename = article.get_filename()
        filepath = os.path.join(self.data_dir, filename)
        
        return os.path.exists(filepath)
    
    async def cleanup_old_articles(self, keep_count: int = 200, keep_days: int = 7) -> int:
        """清理旧文章，只保留最新时间的数据
        
        Args:
            keep_count: 保留的文章数量（按时间排序）
            keep_days: 保留的天数（当设置为1时，只保留最新时间的数据）
        
        Returns:
            删除的文章数量
        """
        try:
            if not os.path.exists(self.data_dir):
                return 0
            
            # 获取所有文章文件
            all_files = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.data_dir, filename)
                    file_stat = os.stat(filepath)
                    
                    # 从文件名中提取时间戳用于排序
                    file_timestamp = self._extract_timestamp_from_filename(filename)
                    
                    all_files.append({
                        'path': filepath,
                        'name': filename,
                        'mtime': file_stat.st_mtime,
                        'size': file_stat.st_size,
                        'timestamp': file_timestamp
                    })
            
            if not all_files:
                return 0
            
            self.logger.info(f"开始数据清理: 当前{len(all_files)}个文件，保留策略: {keep_days}天内数据")
            
            # 如果keep_days为1，实现"只保留最新一次"的逻辑
            if keep_days == 1:
                from collections import defaultdict
                
                # 按时间戳分组文件
                time_groups = defaultdict(list)
                
                for file_info in all_files:
                    timestamp = file_info['timestamp']
                    if timestamp:
                        # 提取日期和小时作为分组键
                        dt = datetime.fromtimestamp(timestamp)
                        time_key = dt.strftime('%Y_%m_%d_%H')
                        time_groups[time_key].append(file_info)
                    else:
                        # 无法解析时间戳的文件，使用修改时间
                        dt = datetime.fromtimestamp(file_info['mtime'])
                        time_key = dt.strftime('%Y_%m_%d_%H')
                        time_groups[time_key].append(file_info)
                
                if not time_groups:
                    return 0
                
                # 找到最新的时间组
                latest_time_key = max(time_groups.keys())
                latest_files = time_groups[latest_time_key]
                
                self.logger.info(f"最新时间: {latest_time_key}，文件数量: {len(latest_files)}")
                
                # 计算要删除的文件（所有非最新时间的文件）
                files_to_delete = []
                for time_key, files in time_groups.items():
                    if time_key != latest_time_key:
                        files_to_delete.extend(files)
                
                self.logger.info(f"需要删除的旧文件数量: {len(files_to_delete)}")
                
            else:
                # 原有的基于天数和数量的清理逻辑
                # 按文件名中的时间戳排序（最新的在前），如果无法解析则使用修改时间
                all_files.sort(key=lambda x: x['timestamp'] if x['timestamp'] else x['mtime'], reverse=True)
                
                # 计算需要删除的文件
                files_to_delete = []
                current_time = datetime.now().timestamp()
                cutoff_time = current_time - (keep_days * 24 * 3600)
                
                # 第一步：删除所有超出时间限制的文件
                files_within_time = []
                for file_info in all_files:
                    file_time = file_info['timestamp'] if file_info['timestamp'] else file_info['mtime']
                    if file_time < cutoff_time:
                        files_to_delete.append(file_info)
                    else:
                        files_within_time.append(file_info)
                
                # 第二步：从时间范围内的文件中，只保留最新的keep_count个
                if len(files_within_time) > keep_count:
                    excess_files = files_within_time[keep_count:]
                    files_to_delete.extend(excess_files)
            
            if not files_to_delete:
                self.logger.info(f"无需清理: 当前{len(all_files)}个文件均在保留范围内")
                return 0
            
            # 删除文件
            deleted_count = 0
            total_size = 0
            
            for file_info in files_to_delete:
                try:
                    os.remove(file_info['path'])
                    deleted_count += 1
                    total_size += file_info['size']
                    self.logger.info(f"已删除旧文章: {file_info['name']}")
                except Exception as e:
                    self.logger.error(f"删除文件失败 {file_info['name']}: {e}")
            
            if deleted_count > 0:
                size_mb = total_size / (1024 * 1024)
                self.logger.info(f"清理完成: 删除 {deleted_count} 个文件，释放 {size_mb:.2f}MB 空间")
                self.logger.info(f"剩余文章数: {len(all_files) - deleted_count}")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理旧文章失败: {e}")
            return 0
    
    def _extract_timestamp_from_filename(self, filename):
        """
        从文件名中提取时间戳
        文件名格式: 2025_08_15_16_xxx.txt
        """
        try:
            # 移除扩展名
            name_without_ext = filename.replace('.txt', '')
            
            # 提取日期时间部分 (前4个下划线分隔的部分)
            parts = name_without_ext.split('_')
            if len(parts) >= 4:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                hour = int(parts[3])
                
                # 转换为时间戳
                from datetime import datetime
                dt = datetime(year, month, day, hour)
                return dt.timestamp()
        except (ValueError, IndexError) as e:
            # 如果无法解析，返回None
            pass
        
        return None