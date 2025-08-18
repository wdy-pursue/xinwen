/**
 * 数据分析模块
 * 负责词云图、统计图表等数据可视化功能
 */

class AnalyticsManager {
    constructor() {
        this.charts = {};
        this.data = {
            articles: [],
            vendors: [],
            keywords: [],
            stats: {}
        };
        this.colors = [
            '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
            '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#ff9f7f'
        ];
        this.navigationBound = false; // 标记导航事件是否已绑定
        
        this.init();
    }

    /**
     * 初始化分析模块
     */
    async init() {
        console.log('📊 初始化数据分析模块...');
        
        // 初始化时检查移动端状态并隐藏厂商导航
        this.initMobileState();
        
        // 绑定页面切换事件
        this.bindNavigation();
        
        // 当切换到分析页面时加载数据
        document.addEventListener('sectionChanged', (e) => {
            console.log('📊 收到页面切换事件:', e.detail);
            const mainContent = document.querySelector('.main-content');
            
            if (e.detail.section === 'analytics') {
                console.log('📊 切换到数据分析页面，开始加载数据...');
                // 隐藏左侧导航栏（数据分析页面不需要）
                this.hideSidebar();
                // 主内容区域占满全宽
                if (mainContent) {
                    mainContent.classList.add('full-width');
                }
                // 强制清除之前的加载状态
                this.hideLoadingStateForced();
                // 延迟一点再加载，确保页面切换完成
                setTimeout(() => {
                    this.loadAnalyticsData();
                }, 100);
            } else if (e.detail.section === 'home') {
                // 首页：移动端始终隐藏，桌面端显示左侧导航栏
                const isMobile = window.innerWidth <= 768;
                if (isMobile) {
                    this.hideSidebar();
                    if (mainContent) {
                        mainContent.classList.add('full-width');
                    }
                    console.log('📱 首页移动端 - 强制保持隐藏厂商导航');
                } else {
                    this.showSidebar();
                    if (mainContent) {
                        mainContent.classList.remove('full-width');
                    }
                    console.log('📱 首页桌面端 - 显示厂商导航，恢复正常布局');
                }
            }
            // 关于页面的处理在上面的页面切换逻辑中已经处理了
        });
        
        console.log('✅ 数据分析模块初始化完成');
    }
    
    /**
     * 初始化移动端状态
     */
    initMobileState() {
        const isMobile = window.innerWidth <= 768;
        const mainContent = document.querySelector('.main-content');
        
        if (isMobile && mainContent) {
            // 移动端确保主内容全宽
            mainContent.classList.add('full-width');
            mainContent.style.marginLeft = '0';
            console.log('📱 页面初始化 - 移动端主内容全宽');
        }
    }

    /**
     * 绑定导航事件
     */
    bindNavigation() {
        // 避免重复绑定，检查是否已经绑定过
        if (this.navigationBound) {
            console.log('📝 导航事件已绑定，跳过重复绑定');
            return;
        }
        
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('.content-section');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const targetSection = link.dataset.section;
                
                // 更新导航状态
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                // 显示对应页面
                sections.forEach(section => {
                    section.classList.remove('active');
                });
                
                const targetElement = document.getElementById(`${targetSection}-section`);
                if (targetElement) {
                    targetElement.classList.add('active');
                    
                    // 根据目标页面控制厂商导航显示/隐藏
                    const sidebar = document.getElementById('vendor-sidebar');
                    const mainContent = document.querySelector('.main-content');
                    const isMobile = window.innerWidth <= 768;
                    
                    if (mainContent) {
                        if (targetSection === 'about' || isMobile) {
                            // 关于页面或移动端：主内容区域占满全宽
                            mainContent.classList.add('full-width');
                            mainContent.style.marginLeft = '0';
                            console.log('📱 页面切换 - 主内容占满全宽');
                        } else if (targetSection === 'home' && !isMobile) {
                            // 桌面端首页：确保厂商导航存在并恢复正常布局
                            if (!sidebar) {
                                // 如果厂商导航不存在，通过NewsManager创建（如果存在）
                                if (window.newsManager && typeof window.newsManager.createDesktopVendorSidebar === 'function') {
                                    window.newsManager.createDesktopVendorSidebar();
                                    sidebar = document.getElementById('vendor-sidebar');
                                }
                            }
                            
                            if (sidebar) {
                                sidebar.removeAttribute('style');
                                sidebar.classList.remove('hidden', 'mobile-hidden');
                                mainContent.classList.remove('full-width');
                                mainContent.style.marginLeft = '';
                                console.log('📱 首页桌面端 - 恢复正常布局');
                            }
                        }
                        
                        // 移动端始终隐藏厂商导航（如果存在）
                        if (isMobile && sidebar) {
                            sidebar.style.display = 'none';
                            sidebar.classList.add('hidden');
                        }
                        
                        // 数据分析页面的导航控制在sectionChanged事件处理中
                    }
                    
                    // 触发页面切换事件
                    console.log('🔀 触发页面切换事件:', targetSection);
                    document.dispatchEvent(new CustomEvent('sectionChanged', {
                        detail: { section: targetSection }
                    }));
                } else {
                    console.warn('❌ 未找到目标页面元素:', `${targetSection}-section`);
                }
            });
        });
        
        this.navigationBound = true; // 标记已绑定导航事件
        console.log('📝 导航事件绑定完成');
    }

    /**
     * 加载分析数据
     */
    async loadAnalyticsData() {
        console.log('📈 开始加载分析数据...');
        
        // 防止重复加载
        if (this.state && this.state.isLoading) {
            console.log('⚠️ 正在加载中，跳过重复请求');
            return;
        }
        
        // 设置加载状态
        if (!this.state) this.state = {};
        this.state.isLoading = true;
        
        try {
            // 显示加载状态
            this.showLoadingState();
            
            // 并行获取数据
            const [newsResponse, keywordsResponse] = await Promise.all([
                fetch('/api/news?per_page=1000'),
                fetch('/api/analytics/keywords?limit=50')
            ]);
            
            const newsData = await newsResponse.json();
            const keywordsData = await keywordsResponse.json();
            
            if (!newsData.success) {
                throw new Error(newsData.message || '获取新闻数据失败');
            }
            
            if (!keywordsData.success) {
                throw new Error(keywordsData.message || '获取关键词数据失败');
            }
            
            this.data.articles = newsData.data.articles || [];
            this.data.vendors = newsData.data.vendors || [];
            this.data.stats = newsData.data.vendor_stats || {};
            
            // 使用后端智能分词的关键词结果
            this.data.keywords = keywordsData.data.keywords || [];
            
            console.log(`✅ 获取分析数据: ${this.data.articles.length}篇文章, ${this.data.keywords.length}个关键词`);
            console.log('🔑 热门关键词:', this.data.keywords.slice(0, 5).map(k => `${k.name}(${k.value}次)`).join(', '));
            
            // 处理数据并生成图表（跳过关键词提取）
            await this.processData();
            await this.renderAllCharts();
            
            console.log('✅ 数据分析页面加载完成');
            
        } catch (error) {
            console.error('❌ 加载分析数据失败:', error);
            this.showErrorState(error.message);
        } finally {
            // 确保清除加载状态
            if (this.state) {
                this.state.isLoading = false;
            }
            console.log('🔚 数据加载流程结束');
        }
    }

    /**
     * 处理数据
     */
    async processData() {
        console.log('🔧 处理分析数据...');
        
        // 关键词已从后端获取，无需前端重新提取
        // this.data.keywords = this.extractKeywords(this.data.articles);
        
        // 计算统计信息
        this.updateStatistics();
        
        console.log('✅ 数据处理完成');
    }

    /**
     * 提取关键词
     */
    extractKeywords(articles) {
        const keywordMap = new Map();
        const commonWords = new Set(['的', '了', '和', '是', '在', '有', '个', '不', '我', '你', '他', '她', '它', '们', '都', '被', '把', '让', '使', '对', '为', '从', '到', '与', '及', '或', '但', '而', '却', '只', '就', '还', '也', '又', '再', '更', '最', '很', '非常', '特别', '尤其', '如果', '因为', '所以', '虽然', '然而', '不过', '可是', '但是', '于是', '然后', '接着', '后来', '最后', '首先', '其次', '再次', '最终']);
        
        articles.forEach(article => {
            const title = article.title || '';
            
            // 简单的中文分词（基于常见分隔符）
            const words = title
                .replace(/[，。！？；：""''（）【】《》〈〉]/g, ' ')
                .split(/\s+/)
                .filter(word => word.length >= 2 && !commonWords.has(word));
            
            words.forEach(word => {
                keywordMap.set(word, (keywordMap.get(word) || 0) + 1);
            });
        });
        
        // 返回前50个高频词
        return Array.from(keywordMap.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 50)
            .map(([word, count]) => ({ name: word, value: count }));
    }

    /**
     * 更新统计信息
     */
    updateStatistics() {
        const topKeywords = this.data.keywords.slice(0, 5);
        const hotKeywords = topKeywords.map(k => k.name).join('、');
        
        // 更新DOM
        const hotKeywordsElement = document.getElementById('hot-keywords-stat');
        hotKeywordsElement.textContent = hotKeywords || '暂无';
        
        // 添加点击事件
        hotKeywordsElement.style.cursor = 'pointer';
        hotKeywordsElement.onclick = () => {
            if (topKeywords.length > 0) {
                this.showTopKeywordsNews(topKeywords);
            }
        };
        
        // 添加hover效果
        hotKeywordsElement.onmouseenter = () => {
            hotKeywordsElement.style.color = 'var(--primary-color)';
            hotKeywordsElement.style.textDecoration = 'underline';
        };
        
        hotKeywordsElement.onmouseleave = () => {
            hotKeywordsElement.style.color = '';
            hotKeywordsElement.style.textDecoration = 'none';
        };
    }

    /**
     * 渲染所有图表
     */
    async renderAllCharts() {
        console.log('🎨 开始渲染图表...');
        
        // 先清理可能存在的旧图表
        this.destroyCharts();
        
        // 并行渲染所有图表
        await Promise.all([
            this.renderWordCloud(),
            this.renderSentimentChart()
        ]);
        
        console.log('✅ 所有图表渲染完成');
    }

    /**
     * 词云图
     */
    async renderWordCloud() {
        const chartDom = document.getElementById('wordcloud-chart');
        if (!chartDom) {
            console.warn('❌ 未找到词云图容器');
            return;
        }
        
        // 如果已存在图表，先销毁
        if (this.charts.wordcloud) {
            try {
                this.charts.wordcloud.dispose();
            } catch (e) {
                console.warn('销毁旧词云图时出错:', e);
            }
        }
        
        const chart = echarts.init(chartDom);
        this.charts.wordcloud = chart;
        
        const option = {
            backgroundColor: '#fff',
            tooltip: {
                show: true,
                formatter: '{b}: 出现{c}次'
            },
            series: [{
                type: 'wordCloud',
                gridSize: 3,
                sizeRange: [14, 60],
                rotationRange: [-45, 45],
                shape: 'circle',
                width: '100%',
                height: '100%',
                drawOutOfBound: false,
                layoutAnimation: true,
                textStyle: {
                    fontFamily: 'Microsoft YaHei, Arial, sans-serif',
                    fontWeight: 'bold',
                    color: () => this.colors[Math.floor(Math.random() * this.colors.length)]
                },
                emphasis: {
                    focus: 'self',
                    textStyle: {
                        shadowBlur: 15,
                        shadowColor: '#333'
                        // 移除fontSize设置，避免悬停时字体变小
                    }
                },
                data: this.data.keywords.filter(k => k.name.length >= 2) // 只显示长度>=2的词
            }]
        };
        
        chart.setOption(option);
        
        // 词云图点击事件：弹出关键词相关新闻窗口
        chart.on('click', (params) => {
            if (params.data && params.data.name) {
                this.showKeywordNews(params.data.name);
            }
        });
        
        this.handleChartResize(chart);
    }

    /**
     * 在首页搜索关键词
     */
    searchKeywordInHomePage(keyword) {
        console.log(`🔍 词云点击搜索: ${keyword}`);
        
        // 切换到首页
        const homeNavLink = document.querySelector('[data-section="home"]');
        const homeSection = document.getElementById('home-section');
        
        if (homeNavLink && homeSection) {
            // 更新导航状态
            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            homeNavLink.classList.add('active');
            
            // 显示首页
            document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
            homeSection.classList.add('active');
            
            // 在搜索框中输入关键词并执行搜索
            setTimeout(() => {
                const searchInput = document.getElementById('search-input');
                if (searchInput && window.newsManager) {
                    searchInput.value = keyword;
                    // 触发搜索
                    window.newsManager.handleSearch();
                    console.log(`✅ 已跳转到首页并搜索: ${keyword}`);
                } else {
                    console.warn('❌ 未找到搜索框或新闻管理器');
                }
            }, 100); // 短暂延迟确保页面切换完成
        } else {
            console.warn('❌ 未找到首页导航或页面元素');
        }
    }

    /**
     * 厂商分布饼图
     */
    async renderVendorPieChart() {
        const chartDom = document.getElementById('vendor-pie-chart');
        const chart = echarts.init(chartDom);
        this.charts.vendorPie = chart;
        
        const vendorData = Object.entries(this.data.stats)
            .map(([vendor, stats]) => ({
                name: vendor,
                value: stats.count
            }))
            .sort((a, b) => b.value - a.value)
            .slice(0, 10);
        
        const option = {
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c}篇 ({d}%)'
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                textStyle: {
                    fontSize: 12
                }
            },
            series: [
                {
                    name: '文章分布',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    center: ['60%', '50%'],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#fff',
                        borderWidth: 2
                    },
                    label: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        label: {
                            show: true,
                            fontSize: 16,
                            fontWeight: 'bold'
                        }
                    },
                    labelLine: {
                        show: false
                    },
                    data: vendorData
                }
            ],
            color: this.colors
        };
        
        chart.setOption(option);
        this.handleChartResize(chart);
    }

    /**
     * 热度趋势图
     */
    async renderTrendChart() {
        const chartDom = document.getElementById('trend-chart');
        const chart = echarts.init(chartDom);
        this.charts.trend = chart;
        
        const vendorData = Object.entries(this.data.stats)
            .sort((a, b) => b[1].count - a[1].count)
            .slice(0, 8);
        
        const option = {
            title: {
                text: '各平台文章数量对比',
                left: 'center',
                textStyle: {
                    fontSize: 16,
                    fontWeight: 'normal'
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: vendorData.map(([vendor]) => vendor),
                axisTick: {
                    alignWithLabel: true
                },
                axisLabel: {
                    rotate: 45
                }
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    name: '文章数',
                    type: 'bar',
                    barWidth: '60%',
                    data: vendorData.map(([vendor, stats]) => ({
                        value: stats.count,
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: this.colors[vendorData.findIndex(([v]) => v === vendor) % this.colors.length] },
                                { offset: 1, color: this.colors[vendorData.findIndex(([v]) => v === vendor) % this.colors.length] + '88' }
                            ])
                        }
                    }))
                }
            ]
        };
        
        chart.setOption(option);
        this.handleChartResize(chart);
    }

    /**
     * 关键词关联网络图
     */
    async renderNetworkChart() {
        const chartDom = document.getElementById('network-chart');
        const chart = echarts.init(chartDom);
        this.charts.network = chart;
        
        // 构建网络数据
        const nodes = this.data.keywords.slice(0, 20).map((keyword, index) => ({
            id: keyword.name,
            name: keyword.name,
            symbolSize: Math.max(keyword.value * 2, 10),
            category: index % 4,
            value: keyword.value
        }));
        
        const links = [];
        // 简单的关联关系（基于共现）
        for (let i = 0; i < nodes.length - 1; i++) {
            for (let j = i + 1; j < Math.min(i + 3, nodes.length); j++) {
                links.push({
                    source: nodes[i].id,
                    target: nodes[j].id,
                    value: Math.random() * 50 + 10
                });
            }
        }
        
        const categories = [
            { name: '高频词汇' },
            { name: '热门话题' },
            { name: '相关概念' },
            { name: '其他词汇' }
        ];
        
        const option = {
            title: {
                text: '关键词关联分析',
                left: 'center',
                textStyle: {
                    fontSize: 16,
                    fontWeight: 'normal'
                }
            },
            tooltip: {
                formatter: '{b}: 出现{c}次'
            },
            legend: {
                data: categories.map(c => c.name),
                bottom: 10
            },
            series: [
                {
                    type: 'graph',
                    layout: 'force',
                    data: nodes,
                    links: links,
                    categories: categories,
                    roam: true,
                    focusNodeAdjacency: true,
                    itemStyle: {
                        borderColor: '#fff',
                        borderWidth: 1,
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.3)'
                    },
                    label: {
                        show: true,
                        position: 'inside',
                        fontSize: 10
                    },
                    lineStyle: {
                        color: 'source',
                        curveness: 0.3,
                        opacity: 0.7
                    },
                    emphasis: {
                        focus: 'adjacency',
                        lineStyle: {
                            width: 10
                        }
                    },
                    force: {
                        repulsion: 100,
                        edgeLength: [10, 50]
                    }
                }
            ],
            color: this.colors
        };
        
        chart.setOption(option);
        this.handleChartResize(chart);
    }

    /**
     * 时间热力图
     */
    async renderHeatmapChart() {
        const chartDom = document.getElementById('heatmap-chart');
        const chart = echarts.init(chartDom);
        this.charts.heatmap = chart;
        
        // 生成模拟的时间分布数据
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
        
        const data = [];
        days.forEach((day, dayIndex) => {
            hours.forEach(hour => {
                const value = Math.floor(Math.random() * 20) + 1;
                data.push([hour, dayIndex, value]);
            });
        });
        
        const option = {
            title: {
                text: '新闻发布时间分布',
                left: 'center',
                textStyle: {
                    fontSize: 16,
                    fontWeight: 'normal'
                }
            },
            tooltip: {
                position: 'top',
                formatter: params => {
                    return `${days[params.value[1]]} ${params.value[0]}:00<br/>发布量: ${params.value[2]}`;
                }
            },
            grid: {
                height: '60%',
                top: '15%'
            },
            xAxis: {
                type: 'category',
                data: hours.map(h => h + ':00'),
                splitArea: {
                    show: true
                }
            },
            yAxis: {
                type: 'category',
                data: days,
                splitArea: {
                    show: true
                }
            },
            visualMap: {
                min: 0,
                max: 20,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '5%',
                inRange: {
                    color: ['#e0f2fe', '#0277bd']
                }
            },
            series: [
                {
                    type: 'heatmap',
                    data: data,
                    label: {
                        show: false
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };
        
        chart.setOption(option);
        this.handleChartResize(chart);
    }

    /**
     * 情感分析图
     */
    async renderSentimentChart() {
        const chartDom = document.getElementById('sentiment-chart');
        if (!chartDom) {
            console.warn('❌ 未找到情感分析图容器');
            return;
        }
        
        // 如果已存在图表，先销毁
        if (this.charts.sentiment) {
            try {
                this.charts.sentiment.dispose();
            } catch (e) {
                console.warn('销毁旧情感分析图时出错:', e);
            }
        }
        
        const chart = echarts.init(chartDom);
        this.charts.sentiment = chart;
        
        // 简单的情感分析（基于关键词）
        const positiveWords = ['成功', '增长', '上涨', '突破', '创新', '发展', '获得', '提升', '优秀', '领先'];
        const negativeWords = ['下跌', '失败', '问题', '危机', '风险', '下降', '困难', '挑战', '损失', '争议'];
        
        let positive = 0, negative = 0, neutral = 0;
        
        this.data.articles.forEach(article => {
            const title = article.title || '';
            const hasPositive = positiveWords.some(word => title.includes(word));
            const hasNegative = negativeWords.some(word => title.includes(word));
            
            if (hasPositive && !hasNegative) {
                positive++;
            } else if (hasNegative && !hasPositive) {
                negative++;
            } else {
                neutral++;
            }
        });
        
        const sentimentData = [
            { name: '积极', value: positive, itemStyle: { color: '#10b981' } },
            { name: '中性', value: neutral, itemStyle: { color: '#6b7280' } },
            { name: '消极', value: negative, itemStyle: { color: '#ef4444' } }
        ];
        
        const option = {
            title: {
                text: '情感倾向分析',
                left: 'center',
                textStyle: {
                    fontSize: 16,
                    fontWeight: 'normal'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c}篇 ({d}%)'
            },
            series: [
                {
                    name: '情感分布',
                    type: 'pie',
                    radius: '65%',
                    center: ['50%', '60%'],
                    data: sentimentData,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    label: {
                        fontSize: 14,
                        fontWeight: 'bold'
                    }
                }
            ]
        };
        
        chart.setOption(option);
        this.handleChartResize(chart);
    }

    /**
     * 显示热门关键词相关新闻
     */
    async showTopKeywordsNews(topKeywords) {
        console.log('🔥 查看热门关键词相关新闻:', topKeywords.map(k => k.name));
        
        const modal = document.getElementById('keyword-modal');
        const title = document.getElementById('keyword-modal-title');
        const body = document.getElementById('keyword-modal-body');
        const closeBtn = document.getElementById('keyword-modal-close');
        
        // 显示弹窗
        modal.classList.add('show');
        title.textContent = '热门关键词相关新闻';
        body.innerHTML = `
            <div class="keyword-news-loading">
                <i class="fas fa-spinner fa-spin"></i> 正在加载热门关键词相关新闻...
            </div>
        `;
        
        try {
            // 为每个关键词获取相关新闻
            const promises = topKeywords.map(async (keyword) => {
                const response = await fetch(`/api/news/by-keyword/${encodeURIComponent(keyword.name)}`);
                const data = await response.json();
                return {
                    keyword: keyword.name,
                    count: keyword.value,
                    articles: data.success ? data.data.articles : []
                };
            });
            
            const results = await Promise.all(promises);
            console.log('🔍 关键词搜索结果:', results.map(r => `${r.keyword}: ${r.articles.length}篇`));
            
            // 合并所有文章并去重
            const allArticles = [];
            const seenIds = new Set();
            
            results.forEach(result => {
                result.articles.forEach(article => {
                    // 使用 file_name 作为唯一标识符进行去重
                    const uniqueId = article.file_name || article.id || `${article.title}-${article.publish_time}`;
                    if (!seenIds.has(uniqueId)) {
                        allArticles.push({
                            ...article,
                            matchedKeyword: result.keyword
                        });
                        seenIds.add(uniqueId);
                    }
                });
            });
            
            // 按排名排序
            allArticles.sort((a, b) => a.rank - b.rank);
            
            if (allArticles.length > 0) {
                // 渲染新闻列表
                const keywordsList = topKeywords.map(k => `<span class="keyword-tag">${k.name}(${k.value}次)</span>`).join('');
                
                const articlesHtml = allArticles.map((article, index) => `
                    <div class="keyword-news-item">
                        <div class="keyword-news-header">
                            <div class="news-number">${index + 1}</div>
                            <div class="news-content">
                                <h4 class="keyword-news-title">${article.title}</h4>
                                <div class="news-meta">
                                    <span class="keyword-news-vendor">
                                        <i class="fas fa-building"></i> ${article.vendor_display}
                                    </span>
                                    <span class="keyword-news-matched">
                                        <i class="fas fa-tag"></i> ${article.matchedKeyword}
                                    </span>
                                    ${article.url ? `
                                        <a href="${article.url}" target="_blank" class="keyword-news-link">
                                            <i class="fas fa-external-link-alt"></i> 原文链接
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                body.innerHTML = `
                    <div class="keyword-news-header-info">
                        <p><strong>热门关键词:</strong> ${keywordsList}</p>
                        <p>找到 <strong>${allArticles.length}</strong> 篇相关新闻</p>
                    </div>
                    <div class="keyword-news-list">
                        ${articlesHtml}
                    </div>
                `;
            } else {
                body.innerHTML = `
                    <div class="keyword-news-empty">
                        <i class="fas fa-search"></i>
                        <p>没有找到与热门关键词相关的新闻</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('加载热门关键词新闻失败:', error);
            body.innerHTML = `
                <div class="keyword-news-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>加载失败，请稍后重试</p>
                </div>
            `;
        }
        
        // 绑定关闭事件
        closeBtn.onclick = () => {
            modal.classList.remove('show');
        };
        
        // 点击背景关闭
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        };
    }

    /**
     * 显示关键词相关新闻（保留原方法以备后用）
     */
    async showKeywordNews(keyword) {
        console.log(`🔍 查看关键词"${keyword}"的相关新闻`);
        
        const modal = document.getElementById('keyword-modal');
        const title = document.getElementById('keyword-modal-title');
        const body = document.getElementById('keyword-modal-body');
        const closeBtn = document.getElementById('keyword-modal-close');
        
        // 显示弹窗
        modal.classList.add('show');
        title.textContent = `"${keyword}" 相关新闻`;
        body.innerHTML = `
            <div class="keyword-news-loading">
                <i class="fas fa-spinner fa-spin"></i> 正在加载相关新闻...
            </div>
        `;
        
        try {
            // 获取相关新闻
            const response = await fetch(`/api/news/by-keyword/${encodeURIComponent(keyword)}`);
            const data = await response.json();
            
            if (data.success && data.data.articles.length > 0) {
                // 渲染新闻列表
                const articlesHtml = data.data.articles.map((article, index) => {
                    // 处理摘要显示
                    const summary = article.summary && article.summary.trim() ? 
                        article.summary : 
                        (article.content && article.content.trim() ? 
                            article.content.substring(0, 120) + '...' : 
                            '暂无详细描述');
                    
                    // 格式化时间 - 使用中文格式
                    const formatTime = (timeStr) => {
                        if (!timeStr) return '未知时间';
                        
                        try {
                            const date = new Date(timeStr);
                            const now = new Date();
                            
                            const [hours, minutes] = [date.getHours(), date.getMinutes()];
                            const formattedMinutes = minutes.toString().padStart(2, '0');
                            
                            // 判断上午下午
                            let period;
                            if (hours < 6) {
                                period = '凌晨';
                            } else if (hours < 12) {
                                period = '上午';
                            } else if (hours < 13) {
                                period = '中午';
                            } else if (hours < 18) {
                                period = '下午';
                            } else {
                                period = '晚上';
                            }
                            
                            // 转换为12小时制显示
                            let displayHour = hours;
                            if (hours === 0) {
                                displayHour = 12;
                            } else if (hours > 12) {
                                displayHour = hours - 12;
                            }
                            
                            // 检查是否是今天
                            const isToday = date.toDateString() === now.toDateString();
                            const isYesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000).toDateString() === date.toDateString();
                            
                            if (isToday) {
                                return `今天${period}${displayHour}:${formattedMinutes}`;
                            } else if (isYesterday) {
                                return `昨天${period}${displayHour}:${formattedMinutes}`;
                            } else {
                                // 超过一天显示完整日期
                                const month = (date.getMonth() + 1).toString().padStart(2, '0');
                                const day = date.getDate().toString().padStart(2, '0');
                                return `${month}-${day} ${period}${displayHour}:${formattedMinutes}`;
                            }
                            
                        } catch (error) {
                            console.warn('时间格式化错误:', error, timeStr);
                            return timeStr || '未知时间';
                        }
                    };
                    
                    return `
                        <div class="keyword-news-item" data-article-id="${article.file_name}">
                            <div class="keyword-news-card">
                                <div class="keyword-news-header">
                                    <div class="news-number">${index + 1}</div>
                                    <div class="news-content-wrapper">
                                        <h4 class="keyword-news-title clickable" onclick="window.newsManager && window.newsManager.showNewsDetail('${article.file_name}')">${article.title}</h4>
                                        <div class="news-meta-top">
                                            <span class="keyword-news-vendor">
                                                <i class="fas fa-building"></i> ${article.vendor_display}
                                            </span>
                                            <span class="keyword-news-rank">
                                                <i class="fas fa-trophy"></i> #${article.rank}
                                            </span>
                                            <span class="keyword-news-time">
                                                <i class="fas fa-clock"></i> ${formatTime(article.timestamp || article.publish_time)}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="keyword-news-summary">
                                    <p>${summary}</p>
                                </div>
                                
                                <div class="keyword-news-actions">
                                    <button class="keyword-news-view-btn" onclick="window.newsManager && window.newsManager.showNewsDetail('${article.file_name}')">
                                        <i class="fas fa-eye"></i> 查看详情
                                    </button>
                                    ${article.url ? `
                                        <a href="${article.url}" target="_blank" class="keyword-news-external-btn">
                                            <i class="fas fa-external-link-alt"></i> 原文链接
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                body.innerHTML = `
                    <div class="keyword-news-header-info">
                        <p>找到 <strong>${data.data.total}</strong> 篇包含关键词 "<strong>${keyword}</strong>" 的新闻</p>
                    </div>
                    <div class="keyword-news-list">
                        ${articlesHtml}
                    </div>
                `;
            } else {
                body.innerHTML = `
                    <div class="keyword-news-empty">
                        <i class="fas fa-search"></i>
                        <p>没有找到包含关键词 "<strong>${keyword}</strong>" 的新闻</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('加载关键词新闻失败:', error);
            body.innerHTML = `
                <div class="keyword-news-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>加载失败，请稍后重试</p>
                </div>
            `;
        }
        
        // 绑定关闭事件
        closeBtn.onclick = () => {
            modal.classList.remove('show');
        };
        
        // 点击背景关闭
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        };
    }

    /**
     * 显示加载状态
     */
    showLoadingState() {
        const chartIds = ['wordcloud-chart', 'sentiment-chart'];
        
        chartIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = `
                    <div class="chart-loading">
                        <i class="fas fa-spinner"></i>
                        <span>加载中...</span>
                    </div>
                `;
            }
        });
    }

    /**
     * 强制清除加载状态
     */
    hideLoadingStateForced() {
        console.log('🧹 强制清除加载状态...');
        const chartIds = ['wordcloud-chart', 'sentiment-chart'];
        
        chartIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                // 清空内容，准备重新加载
                element.innerHTML = '';
            }
        });
    }

    /**
     * 隐藏左侧导航栏
     */
    hideSidebar() {
        const sidebar = document.getElementById('vendor-sidebar');
        if (sidebar) {
            sidebar.style.display = 'none';
            sidebar.classList.add('hidden');
            console.log('📱 隐藏左侧导航栏');
        }
    }

    /**
     * 显示左侧导航栏
     */
    showSidebar() {
        const sidebar = document.getElementById('vendor-sidebar');
        if (sidebar) {
            // 检查是否为移动端，移动端始终不显示
            const isMobile = window.innerWidth <= 768;
            if (!isMobile) {
                sidebar.removeAttribute('style');
                sidebar.classList.remove('hidden', 'mobile-hidden');
                console.log('📱 桌面端显示左侧导航栏，恢复正常布局');
            } else {
                // 移动端强制隐藏
                sidebar.setAttribute('style', 'display: none !important');
                sidebar.classList.add('hidden', 'mobile-hidden');
                console.log('📱 移动端强制保持隐藏左侧导航栏');
            }
        }
    }

    /**
     * 显示错误状态
     */
    showErrorState(message) {
        const chartIds = ['wordcloud-chart', 'sentiment-chart'];
        
        chartIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = `
                    <div class="chart-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>加载失败: ${message}</span>
                    </div>
                `;
            }
        });
    }

    /**
     * 处理图表响应式
     */
    handleChartResize(chart) {
        window.addEventListener('resize', () => {
            chart.resize();
        });
    }

    /**
     * 销毁图表
     */
    destroyCharts() {
        console.log('🧹 开始销毁图表...');
        
        Object.entries(this.charts).forEach(([key, chart]) => {
            try {
                if (chart && typeof chart.dispose === 'function') {
                    console.log(`🗑️ 销毁图表: ${key}`);
                    chart.dispose();
                }
            } catch (error) {
                console.warn(`⚠️ 销毁图表${key}时出错:`, error);
                // 忽略错误，继续处理其他图表
            }
        });
        
        this.charts = {};
        console.log('✅ 图表销毁完成');
    }
}

// 全局变量
let analyticsManager = null;

// 等待ECharts加载完成后初始化
function initAnalyticsWhenReady() {
    if (typeof echarts !== 'undefined') {
        // ECharts已加载，初始化分析管理器
        if (!analyticsManager) {
            analyticsManager = new AnalyticsManager();
            // 导出给其他模块使用
            window.analyticsManager = analyticsManager;
            console.log('📊 全局数据分析管理器已创建（ECharts已加载）');
        }
    } else {
        // ECharts未加载，等待一段时间后重试
        console.log('⏳ 等待ECharts加载完成...');
        setTimeout(initAnalyticsWhenReady, 100);
    }
}

// 页面加载完成后等待ECharts加载
document.addEventListener('DOMContentLoaded', () => {
    initAnalyticsWhenReady();
});
