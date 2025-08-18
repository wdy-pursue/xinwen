import logging
from typing import Dict, Any

from publishers.wechat_publisher import WechatPublisher
from publishers.xiaohongshu_publisher import XiaohongshuPublisher
from publishers.email_sender import EmailSender
# from publishers.browser_wechat_publisher import BrowserWechatPublisher

logger = logging.getLogger(__name__)

class PublisherManager:
    """发布器管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.publishers = {}
        self._initialize_publishers()
    
    def _initialize_publishers(self):
        """初始化发布器"""
        # 微信发布器
        if "wechat" in self.config:
            wechat_config = self.config.get('wechat', {})
            if wechat_config.get('use_browser', False):
                browser_config = {
                    'headless': wechat_config.get('headless', False),
                    'user_data_dir': wechat_config.get('user_data_dir', None)
                }
                # self.publishers["wechat"] = BrowserWechatPublisher(browser_config)
            else:
                self.publishers["wechat"] = WechatPublisher(
                    wechat_config,
                    self.config.get('templates', {})
                )
        
        # 小红书发布器
        if "xiaohongshu" in self.config:
            self.publishers["xiaohongshu"] = XiaohongshuPublisher(
                self.config.get('xiaohongshu', {}),
                self.config.get('templates', {})
            )
        
        # 邮件发送器
        if "email" in self.config:
            self.publishers["email"] = EmailSender(
                self.config.get('email', {}),
                self.config.get('templates', {})
            )
    
    def get_publisher(self, name: str):
        """获取发布器"""
        return self.publishers.get(name)
    
    def get_all_publishers(self) -> Dict[str, Any]:
        """获取所有发布器"""
        return self.publishers