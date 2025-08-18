"""
数据分析控制器
处理数据分析相关的业务逻辑
"""

import os
import re
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AnalyticsController:
    def __init__(self):
        self.data_dir = "data"
        self.common_words = {
            # 基础停用词
            '的', '了', '和', '是', '在', '有', '个', '不', '我', '你', '他', '她', '它', '们', 
            '都', '被', '把', '让', '使', '对', '为', '从', '到', '与', '及', '或', '但', '而', 
            '却', '只', '就', '还', '也', '又', '再', '更', '最', '很', '非常', '特别', '尤其',
            '如果', '因为', '所以', '虽然', '然而', '不过', '可是', '但是', '于是', '然后',
            '接着', '后来', '最后', '首先', '其次', '再次', '最终', '年', '月', '日', '时',
            '今天', '明天', '昨天', '今年', '去年', '明年', '现在', '目前', '已经', '正在',
            
            # 扩展停用词
            '来了', '出来', '进来', '过来', '起来', '下来', '上来', '回来', '出去', '进去',
            '过去', '起去', '下去', '上去', '回去', '这个', '那个', '这些', '那些', '这样',
            '那样', '如此', '这里', '那里', '这边', '那边', '这时', '那时', '现在', '当时',
            '一个', '一些', '一样', '一直', '一起', '一下', '一次', '一般', '一点', '一种',
            '可以', '应该', '能够', '必须', '需要', '想要', '希望', '觉得', '认为', '知道',
            '看到', '听到', '感到', '发现', '遇到', '碰到', '找到', '得到', '拿到', '收到',
            '什么', '怎么', '为什么', '哪里', '哪个', '哪些', '多少', '几个', '怎样', '如何',
            '关于', '由于', '根据', '按照', '通过', '经过', '依据', '基于', '鉴于', '考虑',
            '表示', '显示', '说明', '证明', '反映', '体现', '代表', '意味', '标志', '象征',
            '进行', '实施', '执行', '开展', '推进', '促进', '加强', '提高', '增加', '减少',
            '会有', '将有', '已有', '还有', '只有', '没有', '所有', '全部', '整个', '各种',
            '包括', '除了', '除此', '另外', '此外', '而且', '并且', '同时', '还是', '或者'
        }
        
        # 情感词典
        self.positive_words = {
            '成功', '增长', '上涨', '突破', '创新', '发展', '获得', '提升', '优秀', '领先',
            '胜利', '赢得', '进步', '改善', '积极', '正面', '好', '棒', '赞', '优',
            '喜欢', '爱', '美好', '精彩', '完美', '出色', '卓越', '杰出', '优异', '辉煌'
        }
        
        self.negative_words = {
            '下跌', '失败', '问题', '危机', '风险', '下降', '困难', '挑战', '损失', '争议',
            '错误', '故障', '事故', '灾难', '冲突', '矛盾', '担心', '忧虑', '恐慌', '焦虑',
            '悲伤', '愤怒', '失望', '沮丧', '糟糕', '差', '坏', '恶', '恨', '讨厌'
        }

    def load_articles_from_files(self) -> List[Dict[str, Any]]:
        """从文件加载所有文章"""
        articles = []
        
        if not os.path.exists(self.data_dir):
            logger.warning(f"数据目录不存在: {self.data_dir}")
            return articles
        
        try:
            files = os.listdir(self.data_dir)
            txt_files = [f for f in files if f.endswith('.txt')]
            
            logger.info(f"找到 {len(txt_files)} 个文章文件")
            
            for filename in txt_files:
                try:
                    article = self.parse_article_file(filename)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"解析文件失败 {filename}: {e}")
                    continue
            
            logger.info(f"成功加载 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"加载文章文件失败: {e}")
            return []

    def parse_article_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """解析单个文章文件"""
        file_path = os.path.join(self.data_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read().strip()
            
            if not file_content:
                return None
            
            # 尝试解析JSON格式的文章文件
            article_data = None
            try:
                article_data = json.loads(file_content)
                logger.debug(f"文件 {filename} 为JSON格式")
            except json.JSONDecodeError:
                logger.debug(f"文件 {filename} 为纯文本格式")
            
            # 解析文件名: YYYY_MM_DD_HH_vendor_rank_title_id.txt
            name_parts = filename.replace('.txt', '').split('_')
            if len(name_parts) >= 6:
                try:
                    year, month, day, hour = name_parts[:4]
                    vendor = name_parts[4]
                    rank = int(name_parts[5]) if name_parts[5].isdigit() else 999
                    title_parts = name_parts[6:-1]
                    article_id = name_parts[-1]
                    
                    # 厂商显示名称映射
                    vendor_display_map = {
                        'weread': '微信读书',
                        'zhihu': '知乎',
                        'douban-group': '豆瓣小组',
                        'xiaohongshu': '小红书',
                        'toutiao': '今日头条',
                        'bilibili': 'Bilibili',
                        '36kr': '36氪',
                        'smzdm': '什么值得买',
                        'geekpark': 'Geekpark',
                        'ithome': 'Ithome',
                        'sspai': 'Sspai'
                    }
                    
                    vendor_display = vendor_display_map.get(vendor, vendor)
                    timestamp = f"{year}-{month}-{day} {hour}:00:00"
                    
                    # 如果是JSON格式，使用JSON中的数据
                    if article_data:
                        title = article_data.get('title', '_'.join(title_parts) if title_parts else '无标题')
                        content = article_data.get('content', '')
                        summary = article_data.get('summary', content[:200] + '...' if len(content) > 200 else content)
                    else:
                        # 纯文本格式
                        title = '_'.join(title_parts) if title_parts else '无标题'
                        content = file_content
                        summary = content[:200] + '...' if len(content) > 200 else content
                    
                    return {
                        'id': article_id,
                        'title': title,
                        'content': content[:500] if content else '',  # 只保留前500字符
                        'summary': summary,
                        'source': vendor,
                        'vendor_display': vendor_display,
                        'rank': rank,
                        'timestamp': timestamp,
                        'file_name': filename,
                        'publish_time': timestamp
                    }
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"文件名格式不正确: {filename}, 错误: {e}")
                    return None
            else:
                logger.warning(f"文件名格式不正确: {filename}")
                return None
                
        except Exception as e:
            logger.error(f"读取文件失败 {filename}: {e}")
            return None

    def extract_keywords(self, articles: List[Dict[str, Any]], limit: int = 50) -> List[Dict[str, Any]]:
        """提取关键词 - 使用与搜索相同的字符串匹配逻辑，确保统计数字一致"""
        # 先生成候选关键词列表（使用分词）
        candidate_keywords = set()
        
        logger.info(f"开始从 {len(articles)} 篇文章中提取关键词")
        
        for article in articles:
            title = str(article.get('title', ''))
            content = str(article.get('content', ''))
            summary = str(article.get('summary', ''))
            
            # 获取文章中的所有有效关键词（仅用于生成候选列表）
            title_words = self.simple_tokenize(title)
            content_words = self.simple_tokenize(content)
            summary_words = self.simple_tokenize(summary)
            
            for word in title_words + content_words + summary_words:
                if self.is_valid_keyword(word):
                    candidate_keywords.add(word)
        
        logger.info(f"生成了 {len(candidate_keywords)} 个候选关键词")
        
        # 使用字符串匹配逻辑统计每个关键词的文章数（与搜索逻辑一致）
        keyword_stats = []
        
        for keyword in candidate_keywords:
            keyword_lower = keyword.lower()
            matching_articles = []
            
            for article in articles:
                title = str(article.get('title', ''))
                content = str(article.get('content', ''))
                summary = str(article.get('summary', ''))
                
                # 使用与 filter_articles 相同的字符串匹配逻辑
                if (keyword_lower in title.lower() or 
                    keyword_lower in content.lower() or 
                    keyword_lower in summary.lower()):
                    matching_articles.append(article)
            
            article_count = len(matching_articles)
            if article_count >= 1:  # 至少出现在1篇文章中
                keyword_stats.append((keyword, article_count))
                logger.debug(f"关键词 '{keyword}': {article_count} 篇文章")
        
        # 按文章数降序排序
        keyword_stats.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个关键词
        top_keywords = keyword_stats[:limit]
        
        logger.info(f"提取完成，找到 {len(keyword_stats)} 个关键词，返回前 {len(top_keywords)} 个")
        
        return [
            {
                'name': word,
                'value': article_count,  # 这里的value是包含该关键词的文章数量
                'frequency': article_count / len(articles) if articles else 0
            }
            for word, article_count in top_keywords
        ]
    
    def get_articles_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """根据关键词获取对应的文章列表（使用缓存的映射关系）"""
        if not hasattr(self, '_keyword_articles_cache') or not self._keyword_articles_cache:
            logger.warning("关键词文章缓存为空，需要先调用 extract_keywords")
            return []
        
        articles = self._keyword_articles_cache.get(keyword, [])
        logger.info(f"从缓存中获取关键词 '{keyword}' 的文章: {len(articles)} 篇")
        
        return articles
    
    def is_valid_keyword(self, word: str) -> bool:
        """判断是否为有效关键词"""
        if not word or word is None:
            return False
        
        # 转换为字符串并去除空白
        word = str(word).strip()
        
        # 使用新的有意义词汇判断逻辑
        if not self.is_meaningful_word(word):
            return False
        
        # 过滤停用词
        if word in self.common_words:
            return False
        
        # 过滤None、空字符串等无效值
        if word in ['None', 'null', 'undefined', '']:
            return False
        
        return True

    def simple_tokenize(self, text: str) -> List[str]:
        """简化的中文分词 - 专注于有意义的关键词提取"""
        if not text:
            return []
        
        # 保存原始文本用于调试
        original_text = text
        logger.debug(f"分词输入: {original_text}")
        
        result = []
        
        # 预定义的重要关键词模式 - 优先匹配
        important_patterns = [
            # 完整词汇优先匹配
            r'人工智能|机器学习|深度学习|神经网络|大模型|云计算|区块链|物联网',
            r'直播乱象|网络暴力|虚假宣传|数据泄露|隐私保护|网络诈骗|电信诈骗',
            r'网警|执法|监管|治理|整治|规范|净网|清朗|专项行动|双管齐下|严厉打击',
            r'联合声明|经贸会谈|会议|会谈|峰会|论坛|发布会|外交|国际合作',
            r'中美|中欧|中日|中韩|斯德哥尔摩|贸易|关税|制裁|协议|谈判',
            r'政策|法规|管理|服务|教育|医疗|就业|住房|交通|环保|安全',
            r'科技|金融|地产|汽车|医药|零售|制造|能源|通信|媒体|文化|体育',
            r'GPT-?\d*|ChatGPT|AI|VR|AR|5G|6G|NFT|Web3|DeFi|DAO',
            r'北京|上海|广州|深圳|杭州|成都|重庆|武汉|西安|南京|天津'
        ]
        
        # 使用预定义模式提取关键词
        matched_keywords = set()
        for pattern in important_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if 2 <= len(match) <= 8 and match not in matched_keywords:
                    result.append(match)
                    matched_keywords.add(match)
                    logger.debug(f"匹配到关键词: {match}")
        
        # 简单的中文分词：按标点和空格分割
        # 只处理标点符号，保留中文和英文
        clean_text = re.sub(r'[。，！？：；、""''（）【】《》〈〉\[\]().,!?:;"\'\-_=+|\\/@#$%^&*~`]+', ' ', text)
        words = re.split(r'\s+', clean_text)
        
        # 处理分割后的词汇
        for word in words:
            word = word.strip()
            if not word or len(word) < 2:
                continue
                
            # 跳过已匹配的关键词
            if word in matched_keywords:
                continue
                
            # 纯中文词汇
            if re.match(r'^[\u4e00-\u9fff]+$', word):
                if 2 <= len(word) <= 6:  # 中文词汇长度限制
                    result.append(word)
                    logger.debug(f"中文词汇: {word}")
                elif len(word) > 6:
                    # 长中文词汇只添加原词，不进行切分
                    # 避免产生"警双"、"管齐"等无意义组合
                    logger.debug(f"长中文词汇保持原样: {word}")
                    # 不进行切分，已通过预定义模式匹配的关键词已经足够
            
            # 纯英文词汇
            elif re.match(r'^[a-zA-Z]+$', word):
                if 2 <= len(word) <= 8:
                    result.append(word)
                    logger.debug(f"英文词汇: {word}")
            
            # 混合内容（跳过，避免产生无意义片段）
            else:
                logger.debug(f"跳过混合内容: {word}")
        
        # 过滤和去重
        final_result = []
        seen = set()
        
        for word in result:
            word = word.strip()
            if (self.is_meaningful_word(word) and 
                word not in seen and 
                word not in self.common_words):
                final_result.append(word)
                seen.add(word)
        
        logger.debug(f"最终关键词: {final_result}")
        return final_result
    

    
    def is_meaningful_word(self, word: str) -> bool:
        """判断是否为有意义的词汇"""
        if not word or len(word) < 2:
            return False
        
        # 过滤过长的词
        if len(word) > 8:
            return False
        
        # 过滤纯数字
        if re.match(r'^[\d\s\-\.]+$', word):
            return False
        
        # 过滤无意义的单字重复
        if len(set(word)) == 1:
            return False
        
        # 过滤常见的无意义词（减少过滤，保留更多有意义词汇）
        meaningless_words = {
            '的了', '是的', '这个', '那个', '如果', '因为', '所以', '然后', 
            '接着', '首先', '其次', '最终', '时候', '什么', '怎么', '哪里'
        }
        
        if word in meaningless_words:
            return False
        
        # 对于纯英文词，过滤一些技术名词的无意义组合
        if re.match(r'^[a-zA-Z]+$', word):
            meaningless_english = {
                'com', 'www', 'http', 'https', 'html', 'json', 'null', 'true', 'false',
                'url', 'src', 'img', 'div', 'span', 'css', 'js'
            }
            if word.lower() in meaningless_english:
                return False
        
        return True

    def analyze_vendor_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析厂商分布"""
        vendor_stats = defaultdict(lambda: {'count': 0, 'articles': []})
        
        for article in articles:
            vendor = article.get('vendor_display', '未知来源')
            vendor_stats[vendor]['count'] += 1
            vendor_stats[vendor]['articles'].append(article)
        
        # 转换为普通字典并排序
        sorted_vendors = sorted(
            vendor_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        return {
            'total_vendors': len(vendor_stats),
            'vendors': [
                {
                    'name': vendor,
                    'count': stats['count'],
                    'percentage': round(stats['count'] / len(articles) * 100, 2) if articles else 0
                }
                for vendor, stats in sorted_vendors
            ]
        }

    def analyze_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析情感倾向"""
        sentiment_stats = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            text = title + ' ' + content
            
            positive_score = sum(1 for word in self.positive_words if word in text)
            negative_score = sum(1 for word in self.negative_words if word in text)
            
            if positive_score > negative_score:
                sentiment_stats['positive'] += 1
            elif negative_score > positive_score:
                sentiment_stats['negative'] += 1
            else:
                sentiment_stats['neutral'] += 1
        
        total = len(articles) if articles else 1
        
        return {
            'positive': {
                'count': sentiment_stats['positive'],
                'percentage': round(sentiment_stats['positive'] / total * 100, 2)
            },
            'negative': {
                'count': sentiment_stats['negative'],
                'percentage': round(sentiment_stats['negative'] / total * 100, 2)
            },
            'neutral': {
                'count': sentiment_stats['neutral'],
                'percentage': round(sentiment_stats['neutral'] / total * 100, 2)
            }
        }

    def analyze_time_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析时间分布"""
        hour_stats = defaultdict(int)
        date_stats = defaultdict(int)
        
        for article in articles:
            timestamp = article.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    hour_stats[dt.hour] += 1
                    date_key = dt.strftime('%Y-%m-%d')
                    date_stats[date_key] += 1
                except ValueError:
                    continue
        
        return {
            'hourly_distribution': dict(hour_stats),
            'daily_distribution': dict(date_stats)
        }

    def get_analytics_data(self) -> Dict[str, Any]:
        """获取完整的分析数据"""
        try:
            articles = self.load_articles_from_files()
            
            if not articles:
                return {
                    'success': True,
                    'data': {
                        'total_articles': 0,
                        'keywords': [],
                        'vendor_distribution': {'total_vendors': 0, 'vendors': []},
                        'sentiment_analysis': {
                            'positive': {'count': 0, 'percentage': 0},
                            'negative': {'count': 0, 'percentage': 0},
                            'neutral': {'count': 0, 'percentage': 0}
                        },
                        'time_distribution': {
                            'hourly_distribution': {},
                            'daily_distribution': {}
                        },
                        'last_updated': datetime.now().isoformat()
                    }
                }
            
            # 执行各种分析
            keywords = self.extract_keywords(articles, 50)
            vendor_dist = self.analyze_vendor_distribution(articles)
            sentiment = self.analyze_sentiment(articles)
            time_dist = self.analyze_time_distribution(articles)
            
            return {
                'success': True,
                'data': {
                    'total_articles': len(articles),
                    'keywords': keywords,
                    'vendor_distribution': vendor_dist,
                    'sentiment_analysis': sentiment,
                    'time_distribution': time_dist,
                    'last_updated': datetime.now().isoformat(),
                    'analysis_summary': {
                        'top_keywords': [kw['name'] for kw in keywords[:5]],
                        'dominant_sentiment': max(sentiment.items(), key=lambda x: x[1]['count'])[0],
                        'most_active_vendor': vendor_dist['vendors'][0]['name'] if vendor_dist['vendors'] else '无',
                        'peak_hour': max(time_dist['hourly_distribution'].items(), key=lambda x: x[1])[0] if time_dist['hourly_distribution'] else 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"获取分析数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_keywords_analysis(self, limit: int = 50) -> Dict[str, Any]:
        """获取关键词分析"""
        try:
            articles = self.load_articles_from_files()
            keywords = self.extract_keywords(articles, limit)
            
            return {
                'success': True,
                'data': {
                    'keywords': keywords,
                    'total_articles': len(articles),
                    'analysis_time': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"关键词分析失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_trends_analysis(self) -> Dict[str, Any]:
        """获取趋势分析"""
        try:
            articles = self.load_articles_from_files()
            
            # 按厂商和时间分析趋势
            vendor_trends = defaultdict(lambda: defaultdict(int))
            
            for article in articles:
                vendor = article.get('vendor_display', '未知来源')
                timestamp = article.get('timestamp', '')
                
                if timestamp:
                    try:
                        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                        date_key = dt.strftime('%Y-%m-%d')
                        vendor_trends[vendor][date_key] += 1
                    except ValueError:
                        continue
            
            # 转换为前端友好的格式
            trends_data = []
            for vendor, dates in vendor_trends.items():
                trend_points = [
                    {'date': date, 'count': count}
                    for date, count in sorted(dates.items())
                ]
                trends_data.append({
                    'vendor': vendor,
                    'data': trend_points,
                    'total': sum(dates.values())
                })
            
            # 按总数排序
            trends_data.sort(key=lambda x: x['total'], reverse=True)
            
            return {
                'success': True,
                'data': {
                    'trends': trends_data,
                    'total_articles': len(articles),
                    'analysis_time': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
