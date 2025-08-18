class PlatformCards {
    constructor() {
        this.platforms = [];
        this.newsData = [];
        this.init();
    }

    async init() {
        try {
            console.log('开始初始化PlatformCards...');
            console.log('当前设备信息:', {
                userAgent: navigator.userAgent,
                screenWidth: window.screen.width,
                windowWidth: window.innerWidth,
                isMobile: window.innerWidth <= 768
            });
            
            await this.loadNewsData();
            this.processPlatformData();
            this.renderPlatforms();
            this.bindEvents();
            console.log('PlatformCards初始化完成');
        } catch (error) {
            console.error('初始化失败:', error);
            this.showError('加载数据失败，请刷新页面重试');
        }
    }

    async loadNewsData() {
        try {
            const response = await fetch('/api/news?per_page=1000');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (data.success && data.data && data.data.articles) {
                this.newsData = data.data.articles;
                console.log(`成功加载 ${this.newsData.length} 条新闻`);
            } else {
                throw new Error('API返回数据格式错误');
            }
        } catch (error) {
            console.error('加载新闻数据失败:', error);
            throw error;
        }
    }

    processPlatformData() {
        // 按平台分组新闻
        const platformGroups = {};
        
        this.newsData.forEach(news => {
            const platform = news.source || '未知平台';
            if (!platformGroups[platform]) {
                platformGroups[platform] = [];
            }
            platformGroups[platform].push(news);
        });

        // 转换为平台数组并排序
        this.platforms = Object.keys(platformGroups).map(platformName => {
            const platformNews = platformGroups[platformName]
                .sort((a, b) => (b.hot_index || 0) - (a.hot_index || 0))
                .slice(0, 10); // 只取前10条

            return {
                name: this.translatePlatformName(platformName),
                originalName: platformName,
                icon: this.getPlatformIcon(platformName),
                news: platformNews,
                totalCount: platformGroups[platformName].length
            };
        }).sort((a, b) => b.totalCount - a.totalCount); // 按新闻数量排序

        console.log('处理后的平台数据:', this.platforms);
    }

    translatePlatformName(platformName) {
        const nameMap = {
            '36kr': '36氪',
            'baidu': '百度',
            'bilibili': 'B站',
            'douban-group': '豆瓣小组',
            'douyin': '抖音',
            'geekpark': '极客公园',
            'hupu': '虎扑',
            'ithome': 'IT之家',
            'kuaishou': '快手',
            'netease-news': '网易新闻',
            'qq-news': '腾讯新闻',
            'smzdm': '什么值得买',
            'sspai': '少数派',
            'thepaper': '澎湃新闻',
            'tieba': '百度贴吧',
            'toutiao': '今日头条',
            'weibo': '微博',
            'weread': '微信读书',
            'xiaohongshu': '小红书',
            'zhihu': '知乎'
        };
        return nameMap[platformName] || platformName;
    }

    getPlatformIcon(platformName) {
        const iconMap = {
            '36kr': 'fas fa-rocket',
            'baidu': 'fas fa-search',
            'bilibili': 'fas fa-play-circle',
            'douban-group': 'fas fa-users',
            'douyin': 'fas fa-music',
            'geekpark': 'fas fa-microchip',
            'hupu': 'fas fa-basketball-ball',
            'ithome': 'fas fa-laptop',
            'kuaishou': 'fas fa-video',
            'netease-news': 'fas fa-newspaper',
            'qq-news': 'fas fa-comment-dots',
            'smzdm': 'fas fa-shopping-cart',
            'sspai': 'fas fa-mobile-alt',
            'thepaper': 'fas fa-file-alt',
            'tieba': 'fas fa-comments',
            'toutiao': 'fas fa-fire',
            'weibo': 'fas fa-comment',
            'weread': 'fas fa-book',
            'xiaohongshu': 'fas fa-heart',
            'zhihu': 'fas fa-question-circle'
        };
        return iconMap[platformName] || 'fas fa-globe';
    }

    renderPlatforms() {
        console.log('开始渲染平台数据...');
        const container = document.getElementById('platforms-grid');
        const loading = document.getElementById('loading');
        
        console.log('DOM元素检查:', {
            container: !!container,
            loading: !!loading,
            platformsCount: this.platforms.length
        });
        
        if (!container) {
            console.error('未找到platforms-grid容器元素');
            return;
        }

        // 隐藏加载状态
        if (loading) {
            loading.classList.add('hidden');
            console.log('隐藏加载状态');
        }

        if (this.platforms.length === 0) {
            console.log('没有平台数据，显示空状态');
            container.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>暂无平台数据</p>
                </div>
            `;
            return;
        }
        
        console.log('准备渲染', this.platforms.length, '个平台');

        container.innerHTML = this.platforms.map(platform => `
            <div class="platform-card">
                <div class="platform-header">
                    <div class="platform-icon">
                        <i class="${platform.icon}"></i>
                    </div>
                    <div class="platform-name">${platform.name}</div>
                    <div class="platform-count">共 ${platform.totalCount} 条新闻</div>
                </div>
                <div class="platform-content">
                    <div class="news-list">
                        ${platform.news.map((news, index) => `
                            <div class="news-item" data-news-id="${news.id}" data-url="${news.url || '#'}">
                                <div class="news-rank">${index + 1}</div>
                                <div class="news-content">
                                    <div class="news-title">${this.escapeHtml(news.title)}</div>
                                    <div class="news-meta">
                                        <div class="news-time">
                                            <i class="fas fa-clock"></i>
                                            ${this.formatTime(news.publish_time || news.created_time)}
                                        </div>
                                        ${news.hot_index ? `<div class="news-hot">热度: ${news.hot_index}</div>` : ''}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="platform-actions">
                        <a href="/news?source=${encodeURIComponent(platform.name)}" class="btn btn-primary">
                            <i class="fas fa-list"></i>
                            查看全部
                        </a>
                    </div>
                </div>
            </div>
        `).join('');
        
        console.log('平台数据渲染完成，DOM已更新');
    }



    bindEvents() {
        // 新闻项点击事件
        document.addEventListener('click', (e) => {
            const newsItem = e.target.closest('.news-item');
            if (newsItem) {
                const url = newsItem.dataset.url;
                if (url && url !== '#') {
                    window.open(url, '_blank');
                } else {
                    this.showNewsDetail(newsItem.dataset.newsId);
                }
            }
        });

        // 模态框关闭事件
        const modal = document.getElementById('news-modal');
        const closeBtn = document.getElementById('modal-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }

        // ESC键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal && modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        });
    }

    showNewsDetail(newsId) {
        const news = this.newsData.find(item => item.id == newsId);
        if (!news) return;

        const modal = document.getElementById('news-modal');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');

        if (!modal || !title || !body) return;

        title.textContent = news.title;
        body.innerHTML = `
            <div class="news-detail">
                <div class="news-meta-detail">
                    <div class="meta-item">
                        <i class="fas fa-building"></i>
                        <span>来源: ${news.source || '未知'}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-clock"></i>
                        <span>时间: ${this.formatTime(news.publish_time || news.created_time)}</span>
                    </div>
                    ${news.hot_index ? `
                        <div class="meta-item">
                            <i class="fas fa-fire"></i>
                            <span>热度: ${news.hot_index}</span>
                        </div>
                    ` : ''}
                </div>
                ${news.summary ? `
                    <div class="news-summary">
                        <h4>摘要</h4>
                        <p>${this.escapeHtml(news.summary)}</p>
                    </div>
                ` : ''}
                ${news.url ? `
                    <div class="news-actions">
                        <a href="${news.url}" target="_blank" class="btn btn-primary">
                            <i class="fas fa-external-link-alt"></i>
                            查看原文
                        </a>
                    </div>
                ` : ''}
            </div>
        `;

        modal.style.display = 'block';
    }

    formatTime(timeStr) {
        if (!timeStr) return '未知时间';
        
        try {
            const date = new Date(timeStr);
            if (isNaN(date.getTime())) {
                return timeStr;
            }
            
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);
            
            if (minutes < 1) return '刚刚';
            if (minutes < 60) return `${minutes}分钟前`;
            if (hours < 24) return `${hours}小时前`;
            if (days < 7) return `${days}天前`;
            
            return date.toLocaleDateString('zh-CN', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            console.error('时间格式化错误:', error);
            return timeStr;
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        const container = document.getElementById('platforms-grid');
        const loading = document.getElementById('loading');
        
        if (loading) {
            loading.classList.add('hidden');
        }
        
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>${message}</p>
                    <button onclick="location.reload()" class="btn btn-primary">
                        <i class="fas fa-refresh"></i>
                        重新加载
                    </button>
                </div>
            `;
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new PlatformCards();
});