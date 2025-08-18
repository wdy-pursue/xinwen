import logging
import aiohttp
import json
from typing import Dict, Any, List
from jinja2 import Template
from models.article import Article, WechatArticle
from publishers.base_publisher import BasePublisher
from datetime import datetime

class WechatPublisher(BasePublisher):
    """微信公众号发布器 - 使用新版草稿箱API"""

    def __init__(self, config: Dict[str, Any], template_config: Dict[str, str]):
        super().__init__(config)
        self.app_id = config.get('app_id')
        self.app_secret = config.get('app_secret')
        self.template_config = template_config
        self.access_token = None
        self.logger = logging.getLogger("publisher.wechat")

    async def publish(self, article: Article) -> bool:
        """发布文章到微信公众号（使用草稿箱方式）"""
        try:
            # 确保有访问令牌
            if not self.access_token:
                await self._get_access_token()
                if not self.access_token:
                    self.logger.error("无法获取访问令牌")
                    return False

            # 准备文章内容
            wechat_article = await self._prepare_article(article)

            # 检查必需的字段
            if not wechat_article.thumb_media_id:
                self.logger.error("缺少封面图片media_id，需要先上传封面图片")
                return False

            # 第一步：添加草稿
            draft_media_id = await self._add_draft(wechat_article, article)
            if not draft_media_id:
                return False

            # 第二步：发布草稿（可选，也可以只创建草稿）
            if self.config.get('auto_publish', False):
                return await self._publish_draft(draft_media_id)
            else:
                self.logger.info(f"草稿创建成功: {article.title}, media_id: {draft_media_id}")
                self.logger.info("请在微信公众号后台手动发布该草稿")
                return True

        except Exception as e:
            self.logger.error(f"发布文章异常: {e}")
            return False

    async def _add_draft(self, wechat_article: WechatArticle, article: Article) -> str:
        """添加草稿"""
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
        wechat_article.title = wechat_article.title.strip()
        # 检查长度
        print(f"标题长度: {len(wechat_article.title)} 字符")
        print(f"标题字节长度: {len(wechat_article.title.encode('utf-8'))} 字节")
        print(f"author字节长度: {len(wechat_article.author.encode('utf-8'))} 字节")

        data = {
            "articles": [{
                "title": wechat_article.title,
                "author": wechat_article.author,
                "digest": wechat_article.digest,
                "content": wechat_article.content,
                "content_source_url": wechat_article.content_source_url or article.url,
                "thumb_media_id": wechat_article.thumb_media_id,
                "need_open_comment": 0,  # 0-不打开评论，1-打开评论
                "only_fans_can_comment": 0  # 0-所有人可评论，1-仅粉丝可评论
            }]
        }

        self.logger.info(f"添加草稿数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Accept': 'application/json',
                    'Accept-Charset': 'utf-8'
                }
                async with session.post(url, data=json_data.encode('utf-8'), headers=headers) as response:
                    response_text = await response.text()
                    self.logger.info(f"添加草稿响应状态码: {response.status}")
                    self.logger.info(f"添加草稿响应内容: {response_text}")

                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        self.logger.error(f"无法解析JSON响应: {response_text}")
                        return ""

            # 检查微信API错误码
            if 'errcode' in result and result['errcode'] != 0:
                error_msg = self._get_error_message(result['errcode'])
                self.logger.error(f"微信API返回错误: {result['errcode']} - {error_msg}")

                # 如果是access_token相关错误，尝试重新获取
                if result['errcode'] in [40001, 40014, 42001]:
                    self.logger.info("访问令牌可能过期，尝试重新获取")
                    await self._get_access_token()
                    if self.access_token:
                        # 重试一次
                        return await self._add_draft(wechat_article, article)

                return ""

            if 'media_id' in result:
                self.logger.info(f"草稿添加成功: media_id: {result['media_id']}")
                return result['media_id']
            else:
                self.logger.error(f"草稿添加失败，未返回media_id: {result}")
                return ""

        except Exception as e:
            self.logger.error(f"添加草稿异常: {e}")
            return ""

    async def _publish_draft(self, media_id: str) -> bool:
        """发布草稿"""
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={self.access_token}"

        data = {
            "media_id": media_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json; charset=utf-8'
                }
                async with session.post(url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    self.logger.info(f"发布草稿响应状态码: {response.status}")
                    self.logger.info(f"发布草稿响应内容: {response_text}")

                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        self.logger.error(f"无法解析JSON响应: {response_text}")
                        return False

            # 检查微信API错误码
            if 'errcode' in result and result['errcode'] != 0:
                error_msg = self._get_error_message(result['errcode'])
                self.logger.error(f"发布草稿失败: {result['errcode']} - {error_msg}")
                return False

            if 'publish_id' in result:
                self.logger.info(f"草稿发布成功: publish_id: {result['publish_id']}")
                return True
            else:
                self.logger.error(f"草稿发布失败: {result}")
                return False

        except Exception as e:
            self.logger.error(f"发布草稿异常: {e}")
            return False

    async def check_publish_status(self, publish_id: str) -> Dict[str, Any]:
        """查询发布状态"""
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={self.access_token}"

        data = {
            "publish_id": publish_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json; charset=utf-8'
                }
                async with session.post(url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    self.logger.info(f"查询发布状态响应: {response_text}")

                    try:
                        result = json.loads(response_text)
                        return result
                    except json.JSONDecodeError:
                        self.logger.error(f"无法解析JSON响应: {response_text}")
                        return {}

        except Exception as e:
            self.logger.error(f"查询发布状态异常: {e}")
            return {}

    async def get_draft_list(self, offset: int = 0, count: int = 20) -> Dict[str, Any]:
        """获取草稿列表"""
        url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={self.access_token}"

        data = {
            "offset": offset,
            "count": count,
            "no_content": 0  # 0-返回内容，1-不返回内容
        }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json; charset=utf-8'
                }
                async with session.post(url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    self.logger.info(f"获取草稿列表响应: {response_text}")

                    try:
                        result = json.loads(response_text)
                        return result
                    except json.JSONDecodeError:
                        self.logger.error(f"无法解析JSON响应: {response_text}")
                        return {}

        except Exception as e:
            self.logger.error(f"获取草稿列表异常: {e}")
            return {}

    async def delete_draft(self, media_id: str) -> bool:
        """删除草稿"""
        url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={self.access_token}"

        data = {
            "media_id": media_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json; charset=utf-8'
                }
                async with session.post(url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    self.logger.info(f"删除草稿响应: {response_text}")

                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        self.logger.error(f"无法解析JSON响应: {response_text}")
                        return False

            if 'errcode' in result and result['errcode'] == 0:
                self.logger.info(f"草稿删除成功: {media_id}")
                return True
            else:
                error_msg = self._get_error_message(result.get('errcode', -1))
                self.logger.error(f"删除草稿失败: {result.get('errcode')} - {error_msg}")
                return False

        except Exception as e:
            self.logger.error(f"删除草稿异常: {e}")
            return False

    async def _get_access_token(self):
        """获取微信访问令牌"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response_text = await response.text()
                    self.logger.info(f"获取token响应: {response_text}")

                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        self.logger.error(f"无法解析token响应: {response_text}")
                        return

            if 'access_token' in result:
                self.access_token = result['access_token']
                self.logger.info("获取访问令牌成功")
            elif 'errcode' in result:
                error_msg = self._get_error_message(result['errcode'])
                self.logger.error(f"获取访问令牌失败: {result['errcode']} - {error_msg}")
            else:
                self.logger.error(f"获取访问令牌失败: {result}")

        except Exception as e:
            self.logger.error(f"获取访问令牌异常: {e}")

    async def _prepare_article(self, article: Article) -> WechatArticle:
        """准备微信公众号文章"""
        # 选择模板
        template_name = self.config.get('template', 'news')
        template_html = self.template_config.get(template_name, '')

        # 渲染模板
        template = Template(template_html)
        content = template.render(**article.to_dict())

        # 获取封面图片media_id（如果配置了默认封面）
        thumb_media_id = self.config.get('thumb_media_id', '')
        if not thumb_media_id:
            # 如果没有配置默认封面，可以尝试上传一个默认图片
            thumb_media_id = await self._get_default_thumb_media_id()

        # 创建微信文章
        return WechatArticle(
            title=article.title,
            content=content,
            thumb_media_id=thumb_media_id,
            author=article.author or self.config.get('default_author', '公众号运营'),
            digest=article.summary[:120] if article.summary else article.title[:120],
            content_source_url=article.url,
            show_cover_pic=self.config.get('show_cover_pic', 1)
        )

    async def _get_default_thumb_media_id(self) -> str:
        """获取默认封面图片的media_id"""
        # 这里可以实现上传默认封面图片的逻辑
        # 或者返回预先上传好的图片media_id
        default_thumb = self.config.get('default_thumb_media_id', '')
        if default_thumb:
            return default_thumb

        self.logger.warning("未配置默认封面图片media_id")
        return ''

    def _get_error_message(self, errcode: int) -> str:
        """获取微信API错误码对应的错误信息"""
        error_codes = {
            -1: "系统繁忙，此时请开发者稍候再试",
            0: "请求成功",
            40001: "AppSecret错误或者AppSecret不属于这个公众号",
            40002: "不合法的凭证类型",
            40003: "不合法的OpenID",
            40004: "不合法的媒体文件类型",
            40005: "不合法的文件类型",
            40006: "不合法的文件大小",
            40007: "不合法的媒体文件id",
            40008: "不合法的消息类型",
            40009: "不合法的图片文件大小",
            40010: "不合法的语音文件大小",
            40011: "不合法的视频文件大小",
            40012: "不合法的缩略图文件大小",
            40013: "不合法的AppID",
            40014: "不合法的access_token",
            40015: "不合法的菜单类型",
            40016: "不合法的按钮个数",
            40017: "不合法的按钮个数",
            40018: "不合法的按钮名字长度",
            40019: "不合法的按钮KEY长度",
            40020: "不合法的按钮URL长度",
            40021: "不合法的菜单版本号",
            40022: "不合法的子菜单级数",
            40023: "不合法的子菜单按钮个数",
            40024: "不合法的子菜单按钮类型",
            40025: "不合法的子菜单按钮名字长度",
            40026: "不合法的子菜单按钮KEY长度",
            40027: "不合法的子菜单按钮URL长度",
            40028: "不合法的自定义菜单使用用户",
            40029: "不合法的oauth_code",
            40030: "不合法的refresh_token",
            40031: "不合法的openid列表",
            40032: "不合法的openid列表长度",
            40033: "不合法的请求字符，不能包含\\uxxxx格式的字符",
            40035: "不合法的参数",
            40038: "不合法的请求格式",
            40039: "不合法的URL长度",
            40050: "不合法的分组id",
            40051: "分组名字不合法",
            40117: "分组名字不合法",
            40118: "media_id大小不合法",
            40119: "button类型错误",
            40120: "button类型错误",
            40121: "不合法的media_id类型",
            40132: "微信号不合法",
            40137: "不支持的图片格式",
            41001: "缺少access_token参数",
            41002: "缺少appid参数",
            41003: "缺少refresh_token参数",
            41004: "缺少secret参数",
            41005: "缺少多媒体文件数据",
            41006: "缺少media_id参数",
            41007: "缺少子菜单数据",
            41008: "缺少oauth code",
            41009: "缺少openid",
            42001: "access_token超时",
            42002: "refresh_token超时",
            42003: "oauth_code超时",
            43001: "需要GET请求",
            43002: "需要POST请求",
            43003: "需要HTTPS请求",
            43004: "需要接收者关注",
            43005: "需要好友关系",
            44001: "多媒体文件为空",
            44002: "POST的数据包为空",
            44003: "图文消息内容为空",
            44004: "文本消息内容为空",
            45001: "多媒体文件大小超过限制",
            45002: "消息内容超过限制",
            45003: "标题字段超过限制",
            45004: "描述字段超过限制",
            45005: "链接字段超过限制",
            45006: "图片链接字段超过限制",
            45007: "语音播放时间超过限制",
            45008: "图文消息超过限制",
            45009: "接口调用超过限制",
            45010: "创建菜单个数超过限制",
            45015: "回复时间超过限制",
            45016: "系统分组，不允许修改",
            45017: "分组名字过长",
            45018: "分组数量超过上限",
            45106: "API已废弃，请使用新版接口",
            46001: "不存在媒体数据",
            46002: "不存在的菜单版本",
            46003: "不存在的菜单数据",
            46004: "不存在的用户",
            47001: "解析JSON/XML内容错误",
            48001: "api功能未授权",
            50001: "用户未授权该api",
            85023: "草稿箱已满，请清理后重试",
            85024: "草稿不存在"
        }
        return error_codes.get(errcode, f"未知错误码: {errcode}")

    async def upload_thumb_image(self, image_path: str) -> str:
        """上传封面图片并返回media_id（临时素材）"""
        if not self.access_token:
            await self._get_access_token()
            if not self.access_token:
                return ""

        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type=thumb"

        try:
            with open(image_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('media', f, filename='thumb.jpg', content_type='image/jpeg')

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=data) as response:
                        response_text = await response.text()

                        try:
                            result = json.loads(response_text)
                        except json.JSONDecodeError:
                            self.logger.error(f"无法解析上传响应: {response_text}")
                            return ""

                if 'media_id' in result:
                    self.logger.info(f"封面图片上传成功: {result['media_id']}")
                    return result['media_id']
                else:
                    self.logger.error(f"封面图片上传失败: {result}")
                    return ""

        except Exception as e:
            self.logger.error(f"上传封面图片异常: {e}")
            return ""

    async def upload_permanent_thumb_image(self, image_path: str) -> str:
        """上传永久封面图片并返回media_id"""
        if not self.access_token:
            await self._get_access_token()
            if not self.access_token:
                return ""

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=thumb"

        try:
            with open(image_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('media', f, filename='thumb.jpg', content_type='image/jpeg')

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=data) as response:
                        response_text = await response.text()

                        try:
                            result = json.loads(response_text)
                        except json.JSONDecodeError:
                            self.logger.error(f"无法解析上传响应: {response_text}")
                            return ""

                if 'media_id' in result:
                    self.logger.info(f"永久封面图片上传成功: {result['media_id']}")
                    return result['media_id']
                else:
                    self.logger.error(f"永久封面图片上传失败: {result}")
                    return ""

        except Exception as e:
            self.logger.error(f"上传永久封面图片异常: {e}")
            return ""

    async def publish(self, articles: List[Article]) -> bool:
        """发布文章到微信公众号"""
        if not articles:
            self.logger.warning("没有文章需要发布")
            return False

        # 检查是否启用汇总模式
        digest_mode = self.config.get('digest_mode', False)
        
        if digest_mode:
            return await self._publish_digest(articles)
        else:
            # 原有的单篇发布逻辑
            return await self._publish_individual_articles(articles)

    async def _publish_digest(self, articles: List[Article]) -> bool:
        """汇总发布模式：将所有文章汇总成一篇草稿"""
        try:
            # 获取访问令牌
            await self._get_access_token()
            if not self.access_token:
                self.logger.error("无法获取访问令牌")
                return False

            # 创建汇总文章
            digest_article = await self._create_digest_article(articles)
            
            # 添加到草稿箱
            result = await self.add_draft([digest_article])
            
            if result and 'media_id' in result:
                self.logger.info(f"汇总文章已添加到草稿箱，media_id: {result['media_id']}")
                self.logger.info(f"共汇总了 {len(articles)} 篇文章")
                
                # 更新文章状态为已发布（实际是已添加到草稿箱）
                for article in articles:
                    article.published = True
                    # 修复：保持 publish_time 为 datetime 对象
                    article.publish_time = datetime.now()
                
                return True
            else:
                self.logger.error("添加汇总文章到草稿箱失败")
                return False
                
        except Exception as e:
            self.logger.error(f"汇总发布异常: {e}")
            return False

    async def _create_digest_article(self, articles: List[Article]) -> WechatArticle:
        """创建汇总文章"""
        from datetime import datetime
        from collections import Counter, defaultdict
        
        # 统计信息
        current_time = datetime.now().strftime('%Y年%m月%d日')
        article_count = len(articles)
        
        # 按平台分组文章
        platform_articles = defaultdict(list)
        for article in articles:
            platform_articles[article.source].append(article)
        
        platform_count = len(platform_articles)
        
        # 生成汇总标题
        title_template = self.config.get('digest_title_template', '🔥 {{ date }} 热门资讯 ({{ count }}篇)')
        title = title_template.replace('{{ date }}', datetime.now().strftime('%m月%d日')).replace('{{ count }}', str(article_count))
        
        # 生成各平台内容区块
        platform_sections = ""
        platform_icons = {
            'NowHots': '🔥',
            '知乎': '🤔', 
            '微博': '📱',
            '今日头条': '📰',
            '百度': '🔍',
            '36氪': '💼',
            'TechCrunch': '💻'
        }
        
        platform_index = 0
        for platform, platform_articles_list in platform_articles.items():
            platform_index += 1
            icon = platform_icons.get(platform, '📌')
            
            # 不同来源间隔放大
            margin_top = '40px' if platform_index > 1 else '0px'
            
            # 为不同平台设置不同的渐变色
            platform_colors = [
                'linear-gradient(135deg, #ff6b6b, #ee5a24)',  # 红橙渐变
                'linear-gradient(135deg, #4ecdc4, #44a08d)',  # 青绿渐变
                'linear-gradient(135deg, #a8edea, #fed6e3)',  # 薄荷粉渐变
                'linear-gradient(135deg, #ffecd2, #fcb69f)',  # 橙黄渐变
                'linear-gradient(135deg, #667eea, #764ba2)',  # 蓝紫渐变
                'linear-gradient(135deg, #f093fb, #f5576c)',  # 粉红渐变
                'linear-gradient(135deg, #4facfe, #00f2fe)'   # 蓝青渐变
            ]
            color_gradient = platform_colors[(platform_index - 1) % len(platform_colors)]
            
            platform_sections += f"""<div style='background: #fff; border-radius: 12px; padding: 24px; margin-top: {margin_top}; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);'>
                <h2 style='margin: 0 0 20px 0; background: {color_gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 22px; font-weight: 800; border-bottom: 3px solid transparent; border-image: {color_gradient} 1; padding-bottom: 12px; text-align: center; text-shadow: 0 1px 3px rgba(0,0,0,0.1);'>{icon} {platform} TOP{len(platform_articles_list)}</h2>
                <div>"""
            
            # 为每个平台的文章生成内容
            for i, article in enumerate(platform_articles_list, 1):
                # 使用digest模板渲染每篇文章
                template_name = 'digest'
                template_html = self.template_config.get(template_name, '')
                
                # 单个来源内用分割线分割（除了第一篇）
                separator = "<hr style='border: none; border-top: 1px solid #eee; margin: 16px 0;'>" if i > 1 else ""
                
                if template_html:
                    from jinja2 import Template
                    template = Template(template_html)
                    article_data = article.to_dict()
                    article_data['index'] = i
                    article_html = template.render(**article_data)
                    platform_sections += separator + article_html
                else:
                    # 极简的备用格式，只显示标题
                    platform_sections += f"""{separator}<div style='background: #fff; border-radius: 6px; padding: 16px; margin: 8px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 3px solid transparent; border-image: {color_gradient} 1;'>
                        <h4 style='margin: 0; background: linear-gradient(135deg, #2c3e50, #34495e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 16px; font-weight: 600; line-height: 1.4;'>{article.title}</h4>
                    </div>\n"""
            
            platform_sections += "</div></div>\n"
        
        # 使用汇总模板
        template_name = self.config.get('template', 'digest_summary')
        template_html = self.template_config.get(template_name, '')
        
        if template_html:
            from jinja2 import Template
            template = Template(template_html)
            content = template.render(
                current_time=current_time,
                article_count=article_count,
                platform_count=platform_count,
                platform_sections=platform_sections,
                articles=articles
            )
        else:
            # 优化的备用内容格式
            content = f"""<div style='max-width: 100%; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; background: #fafafa; padding: 20px; border-radius: 12px;'>
                <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 32px;'>
                    <h1 style='margin: 0; font-size: 28px; font-weight: bold;'>🔥 今日热门资讯</h1>
                    <p style='margin: 12px 0 0 0; opacity: 0.9; font-size: 16px;'>{current_time}</p>
                </div>
                
                <div style='background: #fff; padding: 20px; border-radius: 12px; margin-bottom: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);'>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; text-align: center;'>
                        <div style='background: linear-gradient(135deg, #1890ff, #36cfc9); color: white; padding: 16px; border-radius: 8px;'>
                            <div style='font-size: 32px; font-weight: bold; margin-bottom: 4px;'>{article_count}</div>
                            <div style='font-size: 14px; opacity: 0.9;'>📊 热门文章</div>
                        </div>
                        <div style='background: linear-gradient(135deg, #52c41a, #73d13d); color: white; padding: 16px; border-radius: 8px;'>
                            <div style='font-size: 16px; font-weight: bold; margin-bottom: 4px;'>{platform_count}</div>
                            <div style='font-size: 14px; opacity: 0.9;'>🏷️ 覆盖平台</div>
                        </div>
                    </div>
                </div>
                
                {platform_sections}
                
                <div style='background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 8px; padding: 20px; text-align: center; margin-top: 32px;'>
                    <h3 style='margin: 0 0 12px 0; color: #1890ff; font-size: 18px;'>💡 精选说明</h3>
                    <p style='margin: 0; color: #666; line-height: 1.6;'>本期汇总了各大平台的热门资讯，为您精选最有价值的内容</p>
                </div>
            </div>"""
        
        # 生成简洁的摘要
        digest = f"本期精选{article_count}篇热门资讯，覆盖{platform_count}个主流平台，为您呈现最新热点！"
        
        # 获取封面图片media_id
        thumb_media_id = self.config.get('thumb_media_id', '')
        if not thumb_media_id:
            thumb_media_id = await self._get_default_thumb_media_id()
        
        # 不设置查看原文链接
        content_source_url = ""
        
        return WechatArticle(
            title=title,
            content=content,
            thumb_media_id=thumb_media_id,
            author=self.config.get('default_author', '编辑'),
            digest=digest,
            content_source_url=content_source_url,
            show_cover_pic=self.config.get('show_cover_pic', 1)
        )

    async def _publish_individual_articles(self, articles: List[Article]) -> bool:
        """原有的单篇发布逻辑"""
        success_count = 0
        
        for article in articles:
            try:
                # 获取访问令牌
                await self._get_access_token()
                if not self.access_token:
                    self.logger.error("无法获取访问令牌")
                    continue

                # 准备文章
                wechat_article = await self._prepare_article(article)
                
                # 添加草稿
                result = await self.add_draft([wechat_article])
                
                if result and 'media_id' in result:
                    self.logger.info(f"文章已添加到草稿箱: {article.title}")
                    article.published = True
                    # 修复：保持 publish_time 为 datetime 对象
                    article.publish_time = datetime.now()
                    success_count += 1
                else:
                    self.logger.error(f"添加文章到草稿箱失败: {article.title}")
                    
            except Exception as e:
                self.logger.error(f"发布文章异常: {article.title}, 错误: {e}")
                continue
        
        self.logger.info(f"发布完成，成功: {success_count}/{len(articles)}")
        return success_count > 0

    async def add_draft(self, articles_data) -> Dict[str, Any]:
        """添加草稿的公有方法"""
        if not articles_data:
            return {}
            
        # 如果传入的是WechatArticle对象列表，直接使用第一个
        if hasattr(articles_data[0], 'title'):
            wechat_article = articles_data[0]
            # 创建一个临时的Article对象用于兼容
            temp_article = type('TempArticle', (), {
                'title': wechat_article.title,
                'url': wechat_article.content_source_url or '',
                'source': '汇总'
            })()
            
            media_id = await self._add_draft(wechat_article, temp_article)
            if media_id:
                return {'media_id': media_id}
            else:
                return {}
        else:
            # 如果是其他格式，返回空字典
            return {}