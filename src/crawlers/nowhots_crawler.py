import time
from datetime import datetime
from typing import List
from models.article import Article
from crawlers.base_crawler import BaseCrawler
from playwright.async_api import async_playwright
import asyncio
import random
class NowHotsCrawler(BaseCrawler):
    """基于 NowHots 多分类热点爬虫（抓取所有 API）"""

    async def crawl(self) -> List[Article]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,  # 使用新的headless模式
                # 移除executable_path，让Playwright使用内置的Chromium
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            context = await browser.new_context()
            page = await context.new_page()
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
            """)
            all_data = {}

            # 注册响应监听器
            async def handle_response(response):
                url = response.url
                if "api.nowhots.com" in url:
                    print(f"捕获URL: {url}")
                    try:
                        json_data = await response.json()
                        category = url.split("?")[0].split("/")[-1]
                        all_data[category] = json_data
                        print(f"成功解析分类 {category} 的数据")
                    except Exception as e:
                        print(f"解析 {url} 出错: {e}")

            page.on("response", handle_response)
            print("开始访问 NowHots 网站")

            # 进入主站
            await page.goto("https://nowhots.com", timeout=60000)
            await page.wait_for_timeout(3000)
            print("页面加载完成")
            await page.evaluate("""
                window.scrollTo(0, Math.floor(Math.random() * 500));
            """)
            await asyncio.sleep(random.uniform(2, 4))
            # 获取所有 Tab 元素
            menu_boxes = await page.query_selector_all("div.main-scope-left-menu-common-box")
            print(f"检测到 {len(menu_boxes)} 个菜单项")

            # 遍历点击每个 tab，触发对应接口加载
            for i, box in enumerate(menu_boxes):
                try:
                    # 获取每个菜单项的文字，便于调试
                    name_span = await box.query_selector("span")
                    name = await name_span.inner_text() if name_span else f"菜单项_{i}"
                    print(f"点击菜单项 {i+1}: {name}")

                    # 创建一个 Promise 来等待特定的 API 响应
                    api_response_future = asyncio.Future()

                    def response_handler(response):
                        if "api.nowhots.com" in response.url and not api_response_future.done():
                            api_response_future.set_result(response)

                    # 临时添加响应监听器
                    page.on("response", response_handler)

                    try:
                        # 点击菜单项
                        await box.click()

                        # 等待 API 响应，超时时间 10 秒
                        response = await asyncio.wait_for(api_response_future, timeout=10.0)

                        url = response.url
                        print(f"成功捕获API响应: {url}")

                        try:
                            json_data = await response.json()
                            category = url.split("?")[0].split("/")[-1]
                            all_data[category] = json_data
                            print(f"成功保存分类 {category} 的数据，包含 {len(json_data.get('data', []))} 条记录")
                        except Exception as e:
                            print(f"解析JSON数据出错: {e}")

                    except asyncio.TimeoutError:
                        print(f"等待 {name} 的API响应超时")
                    except Exception as e:
                        print(f"点击 {name} 时发生错误: {e}")
                    finally:
                        # 移除临时的响应监听器
                        page.remove_listener("response", response_handler)

                    # 稳定一下 DOM 操作
                    await page.wait_for_timeout(1000)

                except Exception as e:
                    print(f"处理菜单项 {i+1} 时发生错误: {e}")
                    continue

            await browser.close()

        # 构造统一的 Article 列表
        articles: List[Article] = []
        print(f"开始处理 {len(all_data)} 个分类的数据")

        for source, data in all_data.items():
            if isinstance(data, dict) and "data" in data:
                items = data.get("data", [])
                print(f"分类 {source} 包含 {len(items)} 条数据")

                for index, item in enumerate(items, 1):  # 从1开始计数排名
                    if isinstance(item, dict) and index <= 10:
                        # 创建标签列表，包含分类信息
                        tags = item.get("tags", []) if isinstance(item.get("tags"), list) else []
                        tags.append(f"分类:{source}")

                        articles.append(Article(
                            title=item.get("title", ""),
                            content=item.get("content", item.get("summary", "")),  # 如果没有content，使用summary
                            source=source,
                            url=item.get("url", ""),
                            publish_time=datetime.now(),
                            author=item.get("author"),
                            summary=item.get("summary"),
                            tags=tags,
                            rank=index  # 直接使用rank字段存储热度排名
                        ))
            else:
                print(data)
                print(f"警告: 分类 {source} 的数据格式不符合预期")

        print(f"总共构造了 {len(articles)} 篇文章")
        return articles