/**
 * 新闻管理器 - 重构版本
 * 统一管理新闻数据的获取、处理和展示
 */

class NewsManager {
    constructor() {
        this.state = {
            articles: [],
            vendors: [],
            vendorStats: {},
            currentVendor: '',
            searchTerm: '',
            isLoading: false
        };
        
        this.elements = {};
        this.isScrolling = false;
        this.lastScrollTop = 0;
        this.isMobile = window.innerWidth <= 768;
        
        this.init();
        this.initResponsiveHandler();
    }

    /**
     * 初始化
     */
    async init() {
        console.log('🚀 初始化新闻管理器...');
        
        // 根据设备类型处理厂商导航（在元素检查之前）
        if (this.isMobile) {
            // 移动端：确保没有厂商导航
            this.removeMobileVendorSidebar();
        } else {
            // 桌面端：动态创建厂商导航
            this.createDesktopVendorSidebar();
        }
        
        // 初始化DOM元素（在厂商导航创建之后）
        this.initElements();
        
        // 绑定事件
        this.bindEvents();
        
        // 移动端优化由独立脚本处理
        console.log('📱 移动端优化由独立脚本处理');
        
        // 加载数据
        await this.loadNews();
        
        // 额外的调试信息
        console.log('📋 初始化后状态:', {
            articles: this.state.articles?.length || 0,
            vendors: this.state.vendors?.length || 0,
            newsList: !!this.elements.newsList,
            isMobile: this.isMobile
        });
        
        console.log('✅ 新闻管理器初始化完成');
    }

    /**
     * 初始化DOM元素
     */
    initElements() {
        console.log('🔧 开始初始化DOM元素...');
        
        this.elements = {
            searchInput: document.getElementById('search-input'),
            vendorFilter: document.getElementById('source-filter'),
            newsList: document.getElementById('news-list'),
            loading: document.getElementById('loading'),
            modal: document.getElementById('news-modal'),
            modalTitle: document.getElementById('modal-title'),
            modalBody: document.getElementById('modal-body'),
            refreshBtn: document.getElementById('refresh-btn')
        };
        
        // 移动端不初始化厂商侧边栏相关元素
        if (!this.isMobile) {
            this.elements.vendorSidebar = document.getElementById('vendor-sidebar');
            this.elements.sidebarVendorList = document.getElementById('sidebar-vendor-list');
        }

        console.log('📋 DOM元素查找结果:', {
            vendorSidebar: !!this.elements.vendorSidebar,
            sidebarVendorList: !!this.elements.sidebarVendorList,
            newsList: !!this.elements.newsList,
            loading: !!this.elements.loading,
            isMobile: this.isMobile
        });

        // 检查关键元素（移动端和桌面端不同）
        const requiredElements = this.isMobile 
            ? ['newsList', 'loading'] 
            : ['newsList', 'loading', 'vendorSidebar', 'sidebarVendorList'];
        const missingElements = requiredElements.filter(key => !this.elements[key]);
        
        if (missingElements.length > 0) {
            console.error('❌ 缺少关键DOM元素:', missingElements);
            console.log('📍 HTML结构检查 - 应该存在的元素ID:');
            if (!this.isMobile) {
                console.log('- vendor-sidebar:', !!document.getElementById('vendor-sidebar'));
                console.log('- sidebar-vendor-list:', !!document.getElementById('sidebar-vendor-list'));
            }
            console.log('- news-list:', !!document.getElementById('news-list'));
            console.log('- loading:', !!document.getElementById('loading'));
            throw new Error(`缺少关键DOM元素: ${missingElements.join(', ')}`);
        }
        
        console.log('✅ DOM元素初始化完成');
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 搜索事件
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('input', this.debounce((e) => {
                this.state.searchTerm = e.target.value.trim();
                console.log('🔍 搜索:', this.state.searchTerm);
                this.loadNews();
            }, 500));
        }

        // 厂商筛选事件
        if (this.elements.vendorFilter) {
            this.elements.vendorFilter.addEventListener('change', (e) => {
                this.state.currentVendor = e.target.value;
                console.log('🏭 厂商筛选:', this.state.currentVendor);
                this.loadNews();
            });
        }

        // 刷新按钮
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => {
                console.log('🔄 手动刷新');
                this.refresh();
            });
        }

        // 模态框关闭事件
        if (this.elements.modal) {
            // 点击背景关闭模态框
            this.elements.modal.addEventListener('click', (e) => {
                if (e.target === this.elements.modal) {
                    this.closeModal();
                }
            });
            
            // 点击右上角关闭按钮关闭模态框
            const closeBtn = this.elements.modal.querySelector('.close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.closeModal();
                });
            }
        }

        // ESC关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.elements.modal?.classList.contains('show')) {
                this.closeModal();
            }
        });

        console.log('✅ 事件绑定完成');
    }

    /**
     * 加载新闻数据
     */
    async loadNews() {
        if (this.state.isLoading) return;
        
        console.log('📰 加载新闻数据...');
        this.showLoading();
        this.showProgressBar();
        this.state.isLoading = true;

        try {
            // 构建查询参数 - 获取全部文章用于完整展示
            const params = new URLSearchParams();
            params.append('per_page', '1000');  // 设置一个足够大的数字获取全部文章
            
            if (this.state.currentVendor) {
                params.append('source', this.state.currentVendor);
            }
            
            if (this.state.searchTerm) {
                params.append('search', this.state.searchTerm);
            }

            const url = '/api/news?' + params.toString();
            console.log('🌐 请求URL:', url);

            const response = await fetch(url);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || '获取新闻失败');
            }

            // 更新状态
            this.state.articles = data.data.articles || [];
            this.state.vendors = data.data.vendors || [];
            this.state.vendorStats = data.data.vendor_stats || {};

            console.log('✅ 获取成功: ' + this.state.articles.length + '篇文章, ' + this.state.vendors.length + '个厂商');

            // 模拟处理时间，让用户看到加载过程
            await new Promise(resolve => setTimeout(resolve, 500));

            // 更新UI
            this.updateVendorFilter();
            this.displayNews();
            this.updateVendorSidebar();

        } catch (error) {
            console.error('❌ 加载新闻失败:', error);
            this.showError('加载新闻失败: ' + error.message);
        } finally {
            this.completeProgressBar();
            this.hideLoading();
            this.state.isLoading = false;
        }
    }



    /**
     * 显示新闻
     */
    displayNews() {
        console.log('🎨 渲染新闻列表...');
        console.log('📊 当前状态:', {
            articlesCount: this.state.articles.length,
            searchTerm: this.state.searchTerm,
            currentVendor: this.state.currentVendor,
            newsListElement: !!this.elements.newsList
        });

        if (!this.elements.newsList) {
            console.error('❌ news-list DOM元素不存在！');
            return;
        }

        if (this.state.articles.length === 0) {
            console.log('⚠️ 无新闻数据，显示空状态');
            this.elements.newsList.innerHTML = 
                '<div class="empty-state">' +
                    '<i class="fas fa-search" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>' +
                    '<h3>暂无数据</h3>' +
                    '<p>没有找到匹配的新闻内容</p>' +
                '</div>';
            return;
        }

        // 如果有搜索或筛选条件，显示列表视图
        if (this.state.searchTerm || this.state.currentVendor) {
            console.log('📋 显示列表视图 (搜索/筛选)');
            this.displayListView();
        } else {
            // 否则显示分组视图
            console.log('📊 显示分组视图 (默认)');
            this.displayGroupedView();
        }
    }

    /**
     * 显示列表视图（搜索/筛选结果）
     */
    displayListView() {
        const newsHTML = this.state.articles.map(article => this.renderNewsItem(article)).join('');
        this.elements.newsList.innerHTML = newsHTML;
        this.bindNewsItemEvents();
        console.log(`✅ 列表视图渲染完成: ${this.state.articles.length}篇文章`);
    }

    /**
     * 显示分组视图（按厂商分组）
     */
    displayGroupedView() {
        console.log('📊 开始分组视图渲染...');
        
        // 按厂商分组并排序
        const groupedNews = this.groupNewsByVendor(this.state.articles);
        console.log('📈 分组结果:', {
            groupCount: Object.keys(groupedNews).length,
            groups: Object.keys(groupedNews)
        });
        
        let groupedHTML = '';
        
        // 🔧 关键修复：直接按当前分组的文章数量排序，与侧边栏保持一致  
        const sortedVendors = Object.keys(groupedNews).sort((a, b) => {
            return groupedNews[b].length - groupedNews[a].length; // 倒序：文章多的在前
        });
        
        for (const vendor of sortedVendors) {
            const articles = groupedNews[vendor];
            // 按排名正序排序（#1在前）
            articles.sort((a, b) => (a.rank || 999) - (b.rank || 999));
            
            groupedHTML += `
                <div class="vendor-section" id="vendor-${this.slugify(vendor)}" data-vendor="${vendor}">
                    <div class="vendor-header">
                        <h3 class="vendor-title">
                            <i class="fas fa-building"></i> 
                            ${this.translatePlatformName(vendor)} 
                            <span class="vendor-count">(${articles.length}篇)</span>
                        </h3>
                    </div>
                    <div class="vendor-news">
                        ${articles.slice(0, 10).map(article => this.renderNewsItem(article, true)).join('')}
                    </div>
                </div>
            `;
        }

        this.elements.newsList.innerHTML = groupedHTML;
        this.bindNewsItemEvents();
        console.log(`✅ 分组视图渲染完成: ${sortedVendors.length}个厂商`);
        console.log('📋 厂商排序:', sortedVendors);
    }

    /**
     * 按厂商分组新闻
     */
    groupNewsByVendor(articles) {
        const grouped = {};
        
        articles.forEach(article => {
            const vendor = article.vendor_display || article.source || '未知来源';
            if (!grouped[vendor]) {
                grouped[vendor] = [];
            }
            grouped[vendor].push(article);
        });

        // 不在这里排序，交给displayGroupedView统一处理
        return grouped;
    }

    /**
     * 翻译平台名称
     */
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

    /**
     * 渲染单个新闻项
     */
    renderNewsItem(article, showRank = false) {
        const rankBadge = showRank && article.rank ? 
            `<span class="news-rank">#${article.rank}</span>` : '';
        
        const timeDisplay = this.formatChineseTime(article.timestamp || article.publish_time);
        const summary = article.summary || 
                       (article.content ? article.content.substring(0, 120) + '...' : '暂无内容');
        
        // 翻译平台名称
        const sourceName = this.translatePlatformName(article.vendor_display || article.source || '未知来源');

        return `
            <div class="news-item ${showRank ? 'vendor-news-item' : ''}" 
                 data-file="${article.file_name || article.id}" 
                 onclick="newsManager.showNewsDetail('${article.file_name || article.id}')">
                <div class="news-header">
                    <div class="news-title-container">
                        ${rankBadge}
                        <div class="news-title">${article.title || '无标题'}</div>
                    </div>
                    <div class="news-meta">
                        <span class="news-source">${sourceName}</span>
                        <span class="news-time">
                            <i class="fas fa-clock"></i> ${timeDisplay}
                        </span>
                    </div>
                </div>
                <div class="news-summary">${summary}</div>
            </div>
        `;
    }

    /**
     * 绑定新闻项点击事件
     */
    bindNewsItemEvents() {
        // 移除内联onclick，使用事件委托
        this.elements.newsList.addEventListener('click', (e) => {
            const newsItem = e.target.closest('.news-item');
            if (newsItem) {
                const fileName = newsItem.dataset.file;
                if (fileName) {
                    this.showNewsDetail(fileName);
                }
            }
        });
    }

    /**
     * 显示新闻详情
     */
    async showNewsDetail(fileName) {
        console.log('📖 显示新闻详情:', fileName);
        
        try {
            // 对文件名进行URL编码以处理中文字符
            const encodedFileName = encodeURIComponent(fileName);
            const response = await fetch('/api/news/' + encodedFileName);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || '获取新闻详情失败');
            }

            const article = data.data;
            this.elements.modalTitle.textContent = article.title || '新闻详情';
            this.elements.modalBody.innerHTML = this.renderNewsDetail(article);
            this.elements.modal.classList.add('show');

        } catch (error) {
            console.error('❌ 获取新闻详情失败:', error);
            alert('获取新闻详情失败: ' + error.message);
        }
    }

    /**
     * 渲染新闻详情
     */
    renderNewsDetail(article) {
        const hasContent = article.content && article.content.trim();
        const hasSummary = article.summary && article.summary.trim();
        const hasUrl = article.url && article.url.trim();
        
        return `
            <div class="news-detail">
                <div class="news-detail-meta">
                    <div class="detail-meta-item">
                        <strong>来源:</strong> ${article.vendor_display || article.source || '未知'}
                    </div>
                    <div class="detail-meta-item">
                        <strong>时间:</strong> ${this.formatTime(article.timestamp || article.publish_time)}
                    </div>
                    ${article.rank ? `<div class="detail-meta-item"><strong>排名:</strong> #${article.rank}</div>` : ''}
                </div>
                
                ${hasSummary ? `
                    <div class="news-detail-summary">
                        <h4><i class="fas fa-file-text"></i> 摘要</h4>
                        <p>${article.summary}</p>
                    </div>
                ` : ''}
                
                ${hasContent ? `
                    <div class="news-detail-content">
                        <h4><i class="fas fa-newspaper"></i> 详细内容</h4>
                        <div class="content-text">
                            ${article.content.replace(/\n/g, '<br>')}
                        </div>
                    </div>
                ` : ''}
                
                ${hasUrl ? `
                    <div class="news-detail-link">
                        <a href="${article.url}" target="_blank" class="external-link">
                            <i class="fas fa-external-link-alt"></i> 查看原文
                        </a>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * 关闭模态框
     */
    closeModal() {
        if (this.elements.modal) {
            this.elements.modal.classList.remove('show');
        }
    }

    /**
     * 更新厂商筛选器
     */
    updateVendorFilter() {
        if (!this.elements.vendorFilter) return;

        const currentValue = this.elements.vendorFilter.value;
        const options = ['<option value="">全部厂商</option>'];
        
        this.state.vendors.forEach(vendor => {
            const selected = vendor === currentValue ? 'selected' : '';
            options.push(`<option value="${vendor}" ${selected}>${this.translatePlatformName(vendor)}</option>`);
        });

        this.elements.vendorFilter.innerHTML = options.join('');
        console.log('✅ 厂商筛选器更新完成');
    }

    /**
     * 更新厂商侧边栏
     */
    updateVendorSidebar() {
        console.log('📋 更新厂商侧边栏...');

        // 移动端跳过厂商侧边栏更新
        if (this.isMobile) {
            console.log('📱 移动端跳过厂商侧边栏更新');
            return;
        }

        if (!this.elements.sidebarVendorList) return;

        // 🔧 关键修复：使用当前页面文章分组，确保与右侧内容完全一致
        const groupedNews = this.groupNewsByVendor(this.state.articles);
        const vendors = Object.keys(groupedNews).sort((a, b) => {
            return groupedNews[b].length - groupedNews[a].length; // 按文章数量倒序
        });
        
        console.log('📊 侧边栏厂商排序:', vendors.map(v => `${v}(${groupedNews[v].length})`));
        
        if (vendors.length === 0) {
            this.elements.sidebarVendorList.innerHTML = `
                <div class="sidebar-loading">
                    <i class="fas fa-exclamation-circle"></i> 暂无数据
                </div>
            `;
            return;
        }

        const sidebarHTML = vendors.map(vendor => `
            <div class="vendor-item" data-vendor="${vendor}">
                <span class="vendor-name">${this.translatePlatformName(vendor)}</span>
                <span class="vendor-count">${groupedNews[vendor].length}</span>
            </div>
        `).join('');

        this.elements.sidebarVendorList.innerHTML = sidebarHTML;
        
        // 绑定侧边栏点击事件
        this.bindSidebarEvents();
        
        console.log('✅ 厂商侧边栏更新完成');
    }

    /**
     * 绑定侧边栏事件
     */
    bindSidebarEvents() {
        // 移动端跳过侧边栏事件绑定
        if (this.isMobile || !this.elements.sidebarVendorList) {
            console.log('📱 移动端跳过侧边栏事件绑定');
            return;
        }
        
        // 为侧边栏厂商项添加活跃状态
        const vendorItems = this.elements.sidebarVendorList.querySelectorAll('.vendor-item');
        vendorItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                console.log('🖱️ 点击厂商:', item.dataset.vendor);
                
                // 移除所有活跃状态
                vendorItems.forEach(v => v.classList.remove('active'));
                
                // 添加当前点击的活跃状态
                item.classList.add('active');
                
                // 滚动到对应厂商
                const vendor = item.dataset.vendor;
                this.scrollToVendor(vendor);
            });
        });
        
        console.log(`✅ 绑定了 ${vendorItems.length} 个厂商项的点击事件`);
    }

    /**
     * 滚动到指定厂商
     */
    scrollToVendor(vendor) {
        console.log(`🎯 尝试滚动到厂商: ${vendor}`);
        
        const targetId = `vendor-${this.slugify(vendor)}`;
        const element = document.getElementById(targetId);
        
        if (element) {
            // 移动端需要考虑固定头部的高度
            const isMobile = window.innerWidth <= 768;
            if (isMobile) {
                const headerHeight = 70; // 头部高度
                const elementTop = element.offsetTop - headerHeight - 20; // 额外留20px边距
                window.scrollTo({
                    top: elementTop,
                    behavior: 'smooth'
                });
                console.log(`✅ 移动端滚动到厂商: ${vendor} (调整后位置: ${elementTop})`);
            } else {
                // 桌面端正常滚动
                element.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
                console.log(`✅ 桌面端滚动到厂商: ${vendor} (ID: ${targetId})`);
            }
        } else {
            console.warn(`⚠️ 未找到厂商元素: ${targetId}`);
            console.log('📋 页面中现有的厂商ID:', 
                Array.from(document.querySelectorAll('[id^="vendor-"]')).map(el => el.id)
            );
            
            // 如果找不到目标元素，尝试滚动到新闻列表顶部
            const newsList = document.getElementById('news-list');
            if (newsList) {
                newsList.scrollIntoView({ behavior: 'smooth', block: 'start' });
                console.log('📍 滚动到新闻列表顶部作为备选');
            }
        }
    }

    /**
     * 刷新所有数据
     */
    async refresh() {
        await Promise.all([
            this.loadNews(),
            this.loadStats()
        ]);
    }

    /**
     * 显示加载状态
     */
    showLoading() {
        if (this.elements.loading) {
            this.elements.loading.classList.remove('hidden');
        }
        this.showGlobalLoading();
        this.showSkeletonLoading();
    }

    /**
     * 隐藏加载状态
     */
    hideLoading() {
        if (this.elements.loading) {
            this.elements.loading.classList.add('hidden');
        }
        this.hideGlobalLoading();
        this.hideSkeletonLoading();
    }

    /**
     * 显示全局加载覆盖层
     */
    showGlobalLoading() {
        let overlay = document.querySelector('.loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = 
                '<div class="loading-spinner">' +
                    '<div class="spinner"></div>' +
                    '<div class="loading-text">正在加载新闻数据...</div>' +
                '</div>';
            document.body.appendChild(overlay);
        }
        overlay.classList.remove('hidden');
    }

    /**
     * 隐藏全局加载覆盖层
     */
    hideGlobalLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
            setTimeout(() => {
                if (overlay.classList.contains('hidden')) {
                    overlay.remove();
                }
            }, 300);
        }
    }

    /**
     * 显示骨架屏加载
     */
    showSkeletonLoading() {
        if (!this.elements.newsList) return;
        
        const skeletonHTML = this.generateSkeletonHTML();
        this.elements.newsList.innerHTML = skeletonHTML;
    }

    /**
     * 隐藏骨架屏加载
     */
    hideSkeletonLoading() {
        // 骨架屏会在实际内容加载后被替换，无需特殊处理
    }

    /**
     * 生成骨架屏HTML
     */
    generateSkeletonHTML() {
        let skeletonItems = '';
        for (let i = 0; i < 5; i++) {
            skeletonItems += 
                '<div class="skeleton-news-item">' +
                    '<div class="skeleton skeleton-title"></div>' +
                    '<div class="skeleton skeleton-meta"></div>' +
                    '<div class="skeleton skeleton-content"></div>' +
                    '<div class="skeleton skeleton-content"></div>' +
                    '<div class="skeleton skeleton-content"></div>' +
                    '<div class="skeleton-tags">' +
                        '<div class="skeleton skeleton-tag"></div>' +
                        '<div class="skeleton skeleton-tag"></div>' +
                        '<div class="skeleton skeleton-tag"></div>' +
                    '</div>' +
                '</div>';
        }
        return skeletonItems;
    }

    /**
     * 显示加载进度条
     */
    showProgressBar() {
        let progressBar = document.querySelector('.loading-progress');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.className = 'loading-progress';
            progressBar.innerHTML = '<div class="loading-progress-bar"></div>';
            document.body.appendChild(progressBar);
        }
        
        const bar = progressBar.querySelector('.loading-progress-bar');
        bar.style.width = '0%';
        
        // 模拟进度
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            bar.style.width = progress + '%';
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
        
        // 保存interval以便完成时清理
        this.progressInterval = interval;
        this.progressBar = progressBar;
    }

    /**
     * 完成进度条
     */
    completeProgressBar() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        if (this.progressBar) {
            const bar = this.progressBar.querySelector('.loading-progress-bar');
            bar.style.width = '100%';
            
            setTimeout(() => {
                if (this.progressBar) {
                    this.progressBar.remove();
                    this.progressBar = null;
                }
            }, 500);
        }
    }

    /**
     * 显示错误信息
     */
    showError(message) {
        this.elements.newsList.innerHTML = 
            '<div class="error-state">' +
                '<i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 16px; color: var(--error-color);"></i>' +
                '<h3>加载失败</h3>' +
                '<p>' + message + '</p>' +
                '<button onclick="newsManager.refresh()" class="btn-primary">重试</button>' +
            '</div>';
    }

    /**
     * 工具函数: 防抖
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 工具函数: 字符串转换为URL友好格式
     */
    slugify(text) {
        // 保留中文字符、英文字符、数字，移除其他特殊字符
        return text.replace(/[^\u4e00-\u9fffa-zA-Z0-9]/g, '');
    }

    /**
     * 工具函数: 格式化时间
     */
    formatTime(dateString) {
        if (!dateString) return '未知时间';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN');
        } catch {
            return dateString;
        }
    }

    /**
     * 工具函数: 格式化为中文时间格式（显示上午/下午）
     */
    formatChineseTime(dateString) {
        if (!dateString) return '未知时间';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            
            // 格式化选项
            const options = {
                year: 'numeric',
                month: '2-digit', 
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false // 使用24小时制
            };
            
            const formatted = date.toLocaleString('zh-CN', options);
            const [datePart, timePart] = formatted.split(' ');
            
            if (!timePart) {
                return formatted;
            }
            
            const [hours, minutes] = timePart.split(':');
            const hour = parseInt(hours);
            
            // 判断上午下午
            let period;
            if (hour < 6) {
                period = '凌晨';
            } else if (hour < 12) {
                period = '上午';
            } else if (hour < 13) {
                period = '中午';
            } else if (hour < 18) {
                period = '下午';
            } else {
                period = '晚上';
            }
            
            // 转换为12小时制显示
            let displayHour = hour;
            if (hour === 0) {
                displayHour = 12;
            } else if (hour > 12) {
                displayHour = hour - 12;
            }
            
            // 检查是否是今天
            const isToday = date.toDateString() === now.toDateString();
            const isYesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000).toDateString() === date.toDateString();
            
            if (isToday) {
                return `今天${period}${displayHour}:${minutes}`;
            } else if (isYesterday) {
                return `昨天${period}${displayHour}:${minutes}`;
            } else {
                // 超过一天显示完整日期
                const [year, month, day] = datePart.split('/');
                return `${month}-${day} ${period}${displayHour}:${minutes}`;
            }
            
        } catch (error) {
            console.warn('时间格式化错误:', error, dateString);
            return dateString;
        }
    }

    /**
     * 工具函数: 格式化相对时间
     */
    formatTimeAgo(dateString) {
        if (!dateString) return '未知时间';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffMins < 1) return '刚刚';
            if (diffMins < 60) return `${diffMins}分钟前`;
            if (diffHours < 24) return `${diffHours}小时前`;
            if (diffDays < 7) return `${diffDays}天前`;
            
            return this.formatTime(dateString);
        } catch {
            return this.formatTime(dateString);
        }
    }
    
    /**
     * 初始化响应式处理
     */
    initResponsiveHandler() {
        let resizeTimer;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const newIsMobile = window.innerWidth <= 768;
                
                if (this.isMobile !== newIsMobile) {
                    console.log(`📱 NewsManager响应式切换: ${newIsMobile ? '移动端' : '桌面端'}`);
                    this.isMobile = newIsMobile;
                    
                    // 重新初始化厂商侧边栏相关元素
                    if (!this.isMobile) {
                        // 切换到桌面端时，动态创建厂商导航
                        this.createDesktopVendorSidebar();
                        
                        // 重新获取元素引用
                        this.elements.vendorSidebar = document.getElementById('vendor-sidebar');
                        this.elements.sidebarVendorList = document.getElementById('sidebar-vendor-list');
                        
                        // 重新更新厂商侧边栏
                        this.updateVendorSidebar();
                    } else {
                        // 切换到移动端时，移除厂商导航
                        this.removeMobileVendorSidebar();
                        this.elements.vendorSidebar = null;
                        this.elements.sidebarVendorList = null;
                    }
                }
            }, 250);
        });
    }
    
    /**
     * 移动端移除厂商导航
     */
    removeMobileVendorSidebar() {
        const sidebar = document.getElementById('vendor-sidebar');
        if (sidebar) {
            sidebar.remove();
            console.log('📱 NewsManager - 移动端移除厂商导航元素');
        }
        
        // 确保主内容区域占满全宽
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.classList.add('full-width');
            mainContent.style.marginLeft = '0';
        }
    }
    
    /**
     * 桌面端动态创建厂商导航
     */
    createDesktopVendorSidebar() {
        // 检查是否已存在
        if (document.getElementById('vendor-sidebar')) {
            console.log('📱 NewsManager - 桌面端厂商导航已存在');
            return;
        }
        
        // 创建厂商导航HTML
        const sidebarHTML = `
            <aside class="vendor-sidebar" id="vendor-sidebar">
                <div class="sidebar-header">
                    <h4><i class="fas fa-building"></i> 厂商导航</h4>
                </div>
                <div class="sidebar-content" id="sidebar-vendor-list">
                    <div class="sidebar-loading">
                        <i class="fas fa-spinner fa-spin"></i> 加载中...
                    </div>
                </div>
            </aside>
        `;
        
        // 插入到main元素的开头
        const main = document.querySelector('.main');
        if (main) {
            main.insertAdjacentHTML('afterbegin', sidebarHTML);
            console.log('📱 NewsManager - 桌面端动态创建厂商导航');
            
            // 重新获取厂商导航元素
            this.elements.vendorSidebar = document.getElementById('vendor-sidebar');
            this.elements.sidebarVendorList = document.getElementById('sidebar-vendor-list');
            
            // 确保主内容区域有左边距
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.classList.remove('full-width');
                mainContent.style.marginLeft = '';
            }
        }
    }
}

// 全局实例
let newsManager;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM加载完成，开始初始化NewsManager...');
    try {
        newsManager = new NewsManager();
        // 导出给全局使用
        window.newsManager = newsManager;
        console.log('✅ NewsManager初始化成功');
    } catch (error) {
        console.error('❌ NewsManager初始化失败:', error);
    }
});
