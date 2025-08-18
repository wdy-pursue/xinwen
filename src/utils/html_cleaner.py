import re
from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """清理HTML内容"""
    if not html_content:
        return ""

    # 如果输入是HTML，使用BeautifulSoup清理
    if '<' in html_content and '>' in html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除不需要的标签
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()
        
        # 转换为纯文本但保留一些格式
        text = soup.get_text(separator='\n', strip=True)
    else:
        text = html_content
    
    # 清理多余的空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 清理多余的空格
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text