import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any

from models.article import Article
from publishers.base_publisher import BasePublisher

class EmailSender(BasePublisher):
    """邮件发送器"""

    def __init__(self, config: Dict[str, Any], template_config: Dict[str, str]):
        super().__init__(config)
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.sender = config.get('sender', self.username)
        self.recipients = config.get('recipients', [])
        self.use_ssl = config.get('use_ssl', False)
        self.use_tls = config.get('use_tls', True)
        self.template_config = template_config
        self.template = template_config.get(config.get('template', 'email'), '')
        self.logger = logging.getLogger("publisher.email")

    async def publish(self, article: Article) -> bool:
        """发送邮件（实现BasePublisher接口）"""
        try:
            # 准备邮件内容
            subject = article.title
            body = article.content
            
            # 发送邮件
            return await self._send_email(subject, body)
        except Exception as e:
            self.logger.error(f"发送邮件异常: {e}")
            return False

    async def send_digest(self, articles: List[Article], subject: str = None) -> bool:
        """发送文章汇总邮件"""
        try:
            if not articles:
                self.logger.info("没有文章可发送")
                return False
    
            # 创建汇总内容
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
            subject = subject or f"{date_str} 新闻汇总"
            
            # 按来源分组
            sources = {}
            for article in articles:
                source = article.source
                if source not in sources:
                    sources[source] = []
                sources[source].append(article)
            
                # 在 send_digest 方法中，将现有的 HTML 样式替换为以下移动端优化版本
                html_content = f"""
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
                    <title>{subject}</title>
                    <style>
                        * {{
                            box-sizing: border-box;
                        }}
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
                            line-height: 1.5;
                            color: #333;
                            margin: 0;
                            padding: 8px;
                            background-color: #f5f5f5;
                            font-size: 14px;
                        }}
                        .container {{
                            background-color: #ffffff;
                            border-radius: 8px;
                            overflow: hidden;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                        }}
                        .header {{
                            background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                            color: white;
                            padding: 16px;
                            text-align: center;
                        }}
                        .header h1 {{
                            margin: 0;
                            font-size: 20px;
                            font-weight: 600;
                        }}
                        .header .meta {{
                            margin-top: 6px;
                            opacity: 0.9;
                            font-size: 13px;
                        }}
                        .stats {{
                            background-color: #f8f9fa;
                            padding: 12px;
                            text-align: center;
                            border-bottom: 1px solid #e9ecef;
                        }}
                        .stats .stat-item {{
                            display: inline-block;
                            margin: 0 8px;
                            padding: 8px 12px;
                            background-color: white;
                            border-radius: 6px;
                            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                            min-width: 60px;
                        }}
                        .stats .stat-number {{
                            font-size: 18px;
                            font-weight: bold;
                            color: #4285f4;
                        }}
                        .stats .stat-label {{
                            font-size: 11px;
                            color: #666;
                            margin-top: 2px;
                        }}
                        .content {{
                            padding: 12px;
                        }}
                        .source-section {{
                            margin-bottom: 20px;
                            border: 1px solid #e9ecef;
                            border-radius: 6px;
                            overflow: hidden;
                        }}
                        .source-header {{
                            background-color: #f8f9fa;
                            padding: 10px 12px;
                            border-bottom: 1px solid #e9ecef;
                        }}
                        .source-title {{
                            margin: 0;
                            font-size: 16px;
                            font-weight: 600;
                            color: #333;
                        }}
                        .source-count {{
                            color: #666;
                            font-size: 12px;
                            margin-left: 6px;
                        }}
                        .articles-list {{
                            padding: 0;
                            margin: 0;
                            list-style: none;
                        }}
                        .article-item {{
                            padding: 12px;
                            border-bottom: 1px solid #f1f3f4;
                            background-color: white;
                        }}
                        .article-item:last-child {{
                            border-bottom: none;
                        }}
                        .article-item:active {{
                            background-color: #f8f9fa;
                        }}
                        .article-title {{
                            font-size: 15px;
                            font-weight: 600;
                            color: #212529;
                            margin: 0 0 6px 0;
                            line-height: 1.3;
                            word-break: break-word;
                        }}
                        .article-summary {{
                            color: #666;
                            font-size: 13px;
                            margin: 6px 0;
                            line-height: 1.4;
                            word-break: break-word;
                        }}
                        .article-meta {{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-top: 8px;
                            font-size: 11px;
                            color: #999;
                            flex-wrap: wrap;
                            gap: 6px;
                        }}
                        .article-time {{
                            background-color: #e9ecef;
                            padding: 2px 6px;
                            border-radius: 3px;
                            font-size: 10px;
                        }}
                        .article-link {{
                            color: #4285f4;
                            text-decoration: none;
                            font-weight: 500;
                            padding: 4px 8px;
                            border: 1px solid #4285f4;
                            border-radius: 3px;
                            font-size: 11px;
                            white-space: nowrap;
                        }}
                        .article-link:active {{
                            background-color: #4285f4;
                            color: white;
                        }}
                        .footer {{
                            background-color: #f8f9fa;
                            padding: 12px;
                            text-align: center;
                            color: #666;
                            font-size: 11px;
                            border-top: 1px solid #e9ecef;
                        }}
                        
                        /* 针对小屏幕的进一步优化 */
                        @media (max-width: 480px) {{
                            body {{
                                padding: 4px;
                                font-size: 13px;
                            }}
                            .header {{
                                padding: 12px;
                            }}
                            .header h1 {{
                                font-size: 18px;
                            }}
                            .content {{
                                padding: 8px;
                            }}
                            .stats .stat-item {{
                                margin: 2px 4px;
                                padding: 6px 8px;
                                min-width: 50px;
                            }}
                            .stats .stat-number {{
                                font-size: 16px;
                            }}
                            .article-item {{
                                padding: 10px;
                            }}
                            .article-title {{
                                font-size: 14px;
                            }}
                            .article-summary {{
                                font-size: 12px;
                            }}
                            .article-meta {{
                                flex-direction: column;
                                align-items: flex-start;
                                gap: 4px;
                            }}
                            .article-link {{
                                padding: 3px 6px;
                                font-size: 10px;
                            }}
                        }}
                        
                        /* 针对超小屏幕的优化 */
                        @media (max-width: 320px) {{
                            .header h1 {{
                                font-size: 16px;
                            }}
                            .stats .stat-item {{
                                display: block;
                                margin: 4px auto;
                                width: 80px;
                            }}
                            .article-title {{
                                font-size: 13px;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>📱 新闻汇总</h1>
                            <div class="meta">{date_str}</div>
                        </div>
                        
                        <div class="stats">
                            <div class="stat-item">
                                <div class="stat-number">{len(articles)}</div>
                                <div class="stat-label">篇文章</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{len(sources)}</div>
                                <div class="stat-label">个来源</div>
                            </div>
                        </div>
                        
                        <div class="content">
                """
    
                # 添加来源分组内容
                for source, src_articles in sources.items():
                    html_content += f"""
                    <div class="source-section">
                        <div class="source-header">
                            <h2 class="source-title">{source}<span class="source-count">({len(src_articles)}篇)</span></h2>
                        </div>
                        <ul class="articles-list">
    """
    
                    for article in src_articles:
                        # 处理摘要
                        summary_text = ""
                        if article.summary:
                            summary_text = f'<div class="article-summary">{article.summary[:150]}...</div>'
                    
                        # 处理链接
                        link_html = ""
                        if article.url:
                            link_html = f'<a href="{article.url}" class="article-link">查看原文</a>'
                    
                        html_content += f"""
                        <li class="article-item">
                            <div class="article-title">{article.title}</div>
                            {summary_text}
                            <div class="article-meta">
                                <span class="article-time">📅 {article.publish_time.strftime('%H:%M:%S')}</span>
                                {link_html}
                            </div>
                        </li>
    """
    
                    html_content += """
                        </ul>
                    </div>
    """
    
                html_content += f"""
                </div>
                
                <div class="footer">
                    <p>🤖 本邮件由新闻汇总系统自动生成</p>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
            # 发送邮件
            return await self._send_email(subject, html_content, is_html=True)
            
        except Exception as e:
            self.logger.error(f"发送汇总邮件异常: {e}")
            return False

    async def _send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """发送邮件"""
        if not self.smtp_server or not self.username or not self.password or not self.recipients:
            self.logger.error("邮件配置不完整")
            return False

        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ", ".join(self.recipients)
        msg['Subject'] = subject

        # 添加邮件内容
        content_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, content_type, 'utf-8'))

        # 使用 run_in_executor 替代 to_thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._send_email_sync, msg)

    def _send_email_sync(self, msg) -> bool:
        """同步方式发送邮件（用于在异步函数中调用）"""
        try:
            # 连接SMTP服务器
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            # 登录
            server.login(self.username, self.password)

            # 发送邮件
            server.send_message(msg)

            # 关闭连接
            server.quit()

            self.logger.info(f"邮件发送成功: {msg['Subject']}")
            return True

        except Exception as e:
            self.logger.error(f"邮件发送失败: {e}")
            return False