import logging
import aiohttp
import json
import os
import base64
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Template
from models.article import Article
from publishers.base_publisher import BasePublisher

class XiaohongshuPublisher(BasePublisher):
    """小红书发布器"""

    def __init__(self, config: Dict[str, Any], template_config: Dict[str, str]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.api_url = config.get('api_url', 'https://api.xiaohongshu.com/open/v1/notes/publish')
        self.template_config = template_config
        self.logger = logging.getLogger("publisher.xiaohongshu")
        self.access_token = None
        self.token_expires = 0

    async def publish(self, article: Article) -> bool:
        """发布文章到小红书"""
        try:
            # 确保有访问令牌
            if not self.access_token or datetime.now().timestamp() > self.token_expires:
                await self._get_access_token()
                if not self.access_token:
                    self.logger.error("无法获取小红书访问令牌")
                    return False

            # 准备文章内容
            xhs_content = await self._prepare_content(article)
            
            # 准备图片
            images = await self._prepare_images(article)
            
            # 发布笔记
            return await self._publish_note(xhs_content, images, article)

        except Exception as e:
            self.logger.error(f"发布小红书文章异常: {e}")
            return False

    async def _get_access_token(self):
        """获取小红书访问令牌"""
        try:
            token_url = self.config.get('token_url', 'https://api.xiaohongshu.com/open/v1/token')
            data = {
                'client_id': self.api_key,
                'client_secret': self.api_secret,
                'grant_type': 'client_credentials'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, json=data) as response:
                    result = await response.json()
                    
                    if 'access_token' in result:
                        self.access_token = result['access_token']
                        # 设置过期时间（通常是7200秒）
                        self.token_expires = datetime.now().timestamp() + result.get('expires_in', 7200) - 300  # 提前5分钟刷新
                        self.logger.info("成功获取小红书访问令牌")
                    else:
                        self.logger.error(f"获取小红书访问令牌失败: {result}")
        except Exception as e:
            self.logger.error(f"获取小红书访问令牌异常: {e}")

    async def _prepare_content(self, article: Article) -> Dict[str, Any]:
        """准备小红书发布内容"""
        # 使用模板美化内容
        template_name = self.config.get('template', 'default')
        template_str = self.template_config.get(template_name, '{{ title }}\n\n{{ content }}')
        template = Template(template_str)
        
        # 渲染内容
        content = template.render(
            title=article.title,
            content=article.content,
            summary=article.summary or '',
            author=article.author or '',
            source=article.source,
            url=article.url,
            publish_time=article.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            tags=article.tags
        )
        
        # 提取标签
        tags = article.tags.copy() if article.tags else []
        # 添加默认标签
        default_tags = self.config.get('default_tags', [])
        for tag in default_tags:
            if tag not in tags:
                tags.append(tag)
        
        # 限制内容长度
        max_length = self.config.get('max_content_length', 1000)
        if len(content) > max_length:
            content = content[:max_length-3] + '...'
        
        return {
            'title': article.title[:30],  # 小红书标题限制
            'content': content,
            'tags': tags[:20]  # 小红书标签数量限制
        }

    async def _prepare_images(self, article: Article) -> List[str]:
        """准备图片，返回图片的base64编码列表"""
        images = []
        
        # 使用默认封面图
        default_image_path = self.config.get('default_image')
        if default_image_path and os.path.exists(default_image_path):
            try:
                with open(default_image_path, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    images.append(base64_data)
            except Exception as e:
                self.logger.error(f"读取默认图片失败: {e}")
        
        # 如果没有图片，使用文字生成图片（实际项目中可以接入图像生成API）
        if not images:
            # 这里可以接入图像生成API，例如使用文章标题生成图片
            # 为简化示例，这里省略实际图片生成代码
            pass
        
        return images

    async def _publish_note(self, content: Dict[str, Any], images: List[str], article: Article) -> bool:
        """发布小红书笔记"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求数据
            data = {
                'title': content['title'],
                'desc': content['content'],
                'tags': content['tags'],
                'images': images,
                'type': 'normal'  # 普通笔记类型
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get('success'):
                        self.logger.info(f"成功发布小红书笔记: {content['title']}")
                        return True
                    else:
                        self.logger.error(f"发布小红书笔记失败: {result}")
                        return False
        except Exception as e:
            self.logger.error(f"发布小红书笔记异常: {e}")
            return False