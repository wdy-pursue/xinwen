import asyncio
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from models.article import Article
from crawlers.base_crawler import BaseCrawler
from utils.html_cleaner import clean_html

class ZhihuColumnCrawler(BaseCrawler):
    """知乎专栏爬虫"""

    async def crawl(self) -> List[Article]:
        """爬取知乎专栏文章"""
        articles = []
        column_url = self.config.get('url')
        if not column_url:
            self.logger.error("知乎专栏URL未配置")
            return articles

        try:
            # 初始页面请求
            async with self.session.get(column_url, headers=self._get_headers()) as response:
                html = await response.text()
                print(html)
                soup = BeautifulSoup(html, 'html.parser')

                # 提取文章列表 (基于搜索结果中的XPath转换为CSS选择器)
                article_elements = soup.select('div[class*="ColumnPage-articles"] > div')
                self.logger.info(f"找到{len(article_elements)}篇文章")

                for idx, article in enumerate(article_elements):
                    # 提取文章链接
                    link_tag = article.select_one('a[class*="ContentItem-title"]')
                    if not link_tag:
                        continue
                    article_url = link_tag['href']
                    if not article_url.startswith('http'):
                        article_url = f"https://zhihu.com{article_url}"

                    # 提取标题
                    title = link_tag.get_text(strip=True)

                    # 提取发布时间
                    time_tag = article.select_one('time')
                    publish_time = datetime.now()
                    if time_tag and 'datetime' in time_tag.attrs:
                        try:
                            publish_time = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
                        except ValueError:
                            pass

                    # 获取文章详情
                    content = await self._get_article_content(article_url)

                    # 创建文章对象
                    articles.append(Article(
                        title=title,
                        content=content,
                        source=self.name,
                        url=article_url,
                        publish_time=publish_time,
                        author=self._extract_author(article),
                        summary=self._extract_summary(article)
                    ))

                    # 控制爬取数量
                    if len(articles) >= self.config.get('max_articles', 10):
                        break

        except Exception as e:
            self.logger.error(f"知乎专栏爬虫出错: {str(e)}")

        return articles

    async def _get_article_content(self, url: str) -> str:
        """获取文章详细内容"""
        try:
            async with self.session.get(url, headers=self._get_headers()) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                content_div = soup.select_one('div[class*="ArticleContent"]')
                if content_div:
                    return clean_html(content_div.get_text())
        except Exception as e:
            self.logger.error(f"获取文章内容失败 {url}: {str(e)}")
        return ""

    def _get_headers(self):
        """构建请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://www.zhihu.com/'
        }

    def _extract_author(self, article_element) -> str:
        """提取作者信息"""
        author_tag = article_element.select_one('a[class*="UserLink"]')
        return author_tag.get_text(strip=True) if author_tag else ""

    def _extract_summary(self, article_element) -> str:
        """提取文章摘要"""
        summary_tag = article_element.select_one('div[class*="ContentItem-summary"]')
        return summary_tag.get_text(strip=True) if summary_tag else ""