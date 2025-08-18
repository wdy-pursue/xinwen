import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
from models.article import Article
from crawlers.base_crawler import BaseCrawler
from utils.html_cleaner import clean_html

class RSSCrawler(BaseCrawler):
    """RSS feed爬虫"""

    async def crawl(self) -> List[Article]:
        """爬取RSS feed"""
        articles = []

        try:
            # 获取RSS内容
            feed_url = self.config.get('url')
            headers = self.config.get('headers', {})

            async with self.session.get(feed_url, headers=headers) as response:
                content = await response.text()

            # 解析RSS
            feed = feedparser.parse(content)

            for entry in feed.entries:
                # 提取文章信息
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', '')

                # 处理发布时间
                published_time = entry.get('published_parsed')
                if published_time:
                    publish_time = datetime(*published_time[:6])
                else:
                    publish_time = datetime.now()

                # 获取完整内容
                content = await self.get_full_content(link)

                article = Article(
                    title=title,
                    content=content or summary,
                    source=self.name,
                    url=link,
                    publish_time=publish_time,
                    author=entry.get('author', ''),
                    summary=summary
                )

                articles.append(article)

                # 限制文章数量
                if len(articles) >= self.config.get('max_articles', 10):
                    break

        except Exception as e:
            self.logger.error(f"RSS爬虫 {self.name} 出错: {e}")

        return articles

    async def get_full_content(self, url: str) -> str:
        """获取文章完整内容"""
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # 移除脚本和样式
                for script in soup(["script", "style"]):
                    script.decompose()

                # 尝试找到主要内容区域
                content_selectors = [
                    'article',
                    '.content',
                    '.post-content',
                    '.entry-content',
                    '.article-content'
                ]

                for selector in content_selectors:
                    content_div = soup.select_one(selector)
                    if content_div:
                        return clean_html(content_div.get_text(strip=True))

                # 如果没找到特定区域，返回body内容
                body = soup.find('body')
                if body:
                    return clean_html(body.get_text(strip=True)[:2000])  # 限制长度

        except Exception as e:
            self.logger.error(f"获取完整内容失败 {url}: {e}")

        return ""