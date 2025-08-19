/**
 * 无障碍访问管理器
 * 提供键盘导航、屏幕阅读器支持和焦点管理
 */
class AccessibilityManager {
    constructor() {
        this.focusableElements = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"])'
        ].join(', ');
        
        this.trapFocus = null;
        this.lastFocusedElement = null;
        
        this.init();
    }
    
    init() {
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupAriaLabels();
        this.setupSkipLinks();
        this.setupReducedMotion();
        this.setupHighContrast();
        this.announcePageChanges();
    }
    
    /**
     * 设置键盘导航
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'Tab':
                    this.handleTabNavigation(e);
                    break;
                case 'Escape':
                    this.handleEscapeKey(e);
                    break;
                case 'Enter':
                case ' ':
                    this.handleActivation(e);
                    break;
                case 'ArrowUp':
                case 'ArrowDown':
                case 'ArrowLeft':
                case 'ArrowRight':
                    this.handleArrowNavigation(e);
                    break;
            }
        });
        
        // 为所有可聚焦元素添加焦点指示器
        document.addEventListener('focusin', (e) => {
            this.showFocusIndicator(e.target);
        });
        
        document.addEventListener('focusout', (e) => {
            this.hideFocusIndicator(e.target);
        });
    }
    
    /**
     * Tab键导航处理
     */
    handleTabNavigation(e) {
        if (this.trapFocus) {
            const focusableElements = this.trapFocus.querySelectorAll(this.focusableElements);
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
    
    /**
     * Escape键处理
     */
    handleEscapeKey(e) {
        // 关闭模态框
        const modal = document.querySelector('.modal.active');
        if (modal) {
            this.closeModal(modal);
            return;
        }
        
        // 关闭下拉菜单
        const dropdown = document.querySelector('.dropdown.active');
        if (dropdown) {
            dropdown.classList.remove('active');
            return;
        }
        
        // 清除搜索
        const searchInput = document.querySelector('.search-input:focus');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
        }
    }
    
    /**
     * 激活键处理（Enter/Space）
     */
    handleActivation(e) {
        const target = e.target;
        
        // 处理自定义按钮
        if (target.hasAttribute('role') && target.getAttribute('role') === 'button') {
            e.preventDefault();
            target.click();
        }
        
        // 处理卡片点击
        if (target.classList.contains('news-item') || target.closest('.news-item')) {
            e.preventDefault();
            const newsItem = target.classList.contains('news-item') ? target : target.closest('.news-item');
            const link = newsItem.querySelector('a');
            if (link) {
                link.click();
            }
        }
    }
    
    /**
     * 箭头键导航处理
     */
    handleArrowNavigation(e) {
        const target = e.target;
        
        // 处理新闻列表导航
        if (target.closest('.news-grid')) {
            e.preventDefault();
            this.navigateNewsGrid(e.key, target);
        }
        
        // 处理菜单导航
        if (target.closest('.nav-menu')) {
            e.preventDefault();
            this.navigateMenu(e.key, target);
        }
    }
    
    /**
     * 新闻网格导航
     */
    navigateNewsGrid(key, currentElement) {
        const newsItems = Array.from(document.querySelectorAll('.news-item'));
        const currentIndex = newsItems.findIndex(item => 
            item === currentElement || item.contains(currentElement)
        );
        
        if (currentIndex === -1) return;
        
        let nextIndex;
        const itemsPerRow = this.getItemsPerRow();
        
        switch(key) {
            case 'ArrowUp':
                nextIndex = currentIndex - itemsPerRow;
                break;
            case 'ArrowDown':
                nextIndex = currentIndex + itemsPerRow;
                break;
            case 'ArrowLeft':
                nextIndex = currentIndex - 1;
                break;
            case 'ArrowRight':
                nextIndex = currentIndex + 1;
                break;
        }
        
        if (nextIndex >= 0 && nextIndex < newsItems.length) {
            newsItems[nextIndex].focus();
            newsItems[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
    
    /**
     * 菜单导航
     */
    navigateMenu(key, currentElement) {
        const menuItems = Array.from(document.querySelectorAll('.nav-link'));
        const currentIndex = menuItems.indexOf(currentElement);
        
        if (currentIndex === -1) return;
        
        let nextIndex;
        switch(key) {
            case 'ArrowUp':
            case 'ArrowLeft':
                nextIndex = currentIndex - 1;
                if (nextIndex < 0) nextIndex = menuItems.length - 1;
                break;
            case 'ArrowDown':
            case 'ArrowRight':
                nextIndex = currentIndex + 1;
                if (nextIndex >= menuItems.length) nextIndex = 0;
                break;
        }
        
        menuItems[nextIndex].focus();
    }
    
    /**
     * 获取每行项目数
     */
    getItemsPerRow() {
        const container = document.querySelector('.news-grid');
        if (!container) return 1;
        
        const containerWidth = container.offsetWidth;
        const itemWidth = 300; // 假设每个新闻项目宽度
        return Math.floor(containerWidth / itemWidth) || 1;
    }
    
    /**
     * 焦点管理
     */
    setupFocusManagement() {
        // 为所有新闻项目添加tabindex
        document.querySelectorAll('.news-item').forEach((item, index) => {
            item.setAttribute('tabindex', index === 0 ? '0' : '-1');
            item.setAttribute('role', 'article');
        });
        
        // 为按钮添加适当的属性
        document.querySelectorAll('.theme-toggle').forEach(button => {
            button.setAttribute('aria-label', '切换主题');
            button.setAttribute('role', 'button');
        });
    }
    
    /**
     * 设置ARIA标签
     */
    setupAriaLabels() {
        // 主要区域标签
        const header = document.querySelector('header');
        if (header) header.setAttribute('role', 'banner');
        
        const main = document.querySelector('main');
        if (main) main.setAttribute('role', 'main');
        
        const nav = document.querySelector('nav');
        if (nav) nav.setAttribute('role', 'navigation');
        
        // 搜索区域
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.setAttribute('aria-label', '搜索新闻');
            searchInput.setAttribute('role', 'searchbox');
        }
        
        // 新闻列表
        const newsList = document.querySelector('.news-list');
        if (newsList) {
            newsList.setAttribute('role', 'feed');
            newsList.setAttribute('aria-label', '新闻列表');
        }
        
        // 加载状态
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(element => {
            element.setAttribute('aria-live', 'polite');
            element.setAttribute('aria-label', '正在加载');
        });
    }
    
    /**
     * 设置跳转链接
     */
    setupSkipLinks() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = '跳转到主要内容';
        skipLink.className = 'skip-link';
        skipLink.setAttribute('aria-label', '跳转到主要内容');
        
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // 确保主要内容有ID
        const mainContent = document.querySelector('main') || document.querySelector('.main-content');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }
    }
    
    /**
     * 设置减少动画偏好
     */
    setupReducedMotion() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.classList.add('reduce-motion');
        }
        
        // 监听偏好变化
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            if (e.matches) {
                document.documentElement.classList.add('reduce-motion');
            } else {
                document.documentElement.classList.remove('reduce-motion');
            }
        });
    }
    
    /**
     * 设置高对比度支持
     */
    setupHighContrast() {
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.documentElement.classList.add('high-contrast');
        }
        
        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            if (e.matches) {
                document.documentElement.classList.add('high-contrast');
            } else {
                document.documentElement.classList.remove('high-contrast');
            }
        });
    }
    
    /**
     * 显示焦点指示器
     */
    showFocusIndicator(element) {
        element.classList.add('focus-visible');
    }
    
    /**
     * 隐藏焦点指示器
     */
    hideFocusIndicator(element) {
        element.classList.remove('focus-visible');
    }
    
    /**
     * 焦点陷阱
     */
    trapFocusIn(container) {
        this.lastFocusedElement = document.activeElement;
        this.trapFocus = container;
        
        const focusableElements = container.querySelectorAll(this.focusableElements);
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
    
    /**
     * 释放焦点陷阱
     */
    releaseFocusTrap() {
        this.trapFocus = null;
        if (this.lastFocusedElement) {
            this.lastFocusedElement.focus();
            this.lastFocusedElement = null;
        }
    }
    
    /**
     * 关闭模态框
     */
    closeModal(modal) {
        modal.classList.remove('active');
        this.releaseFocusTrap();
        this.announce('模态框已关闭');
    }
    
    /**
     * 页面变化通知
     */
    announcePageChanges() {
        // 监听路由变化
        window.addEventListener('popstate', () => {
            this.announce('页面已更新');
        });
        
        // 监听内容更新
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    const hasNewContent = Array.from(mutation.addedNodes).some(node => 
                        node.nodeType === Node.ELEMENT_NODE && 
                        (node.classList.contains('news-item') || node.querySelector('.news-item'))
                    );
                    
                    if (hasNewContent) {
                        this.announce('新内容已加载');
                    }
                }
            });
        });
        
        const newsContainer = document.querySelector('.news-list');
        if (newsContainer) {
            observer.observe(newsContainer, { childList: true, subtree: true });
        }
    }
    
    /**
     * 屏幕阅读器通知
     */
    announce(message, priority = 'polite') {
        const announcer = document.getElementById('aria-announcer') || this.createAnnouncer();
        announcer.setAttribute('aria-live', priority);
        announcer.textContent = message;
        
        // 清除消息以便下次通知
        setTimeout(() => {
            announcer.textContent = '';
        }, 1000);
    }
    
    /**
     * 创建通知元素
     */
    createAnnouncer() {
        const announcer = document.createElement('div');
        announcer.id = 'aria-announcer';
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(announcer);
        return announcer;
    }
    
    /**
     * 更新新闻项目的无障碍属性
     */
    updateNewsItemAccessibility(newsItem, index, total) {
        newsItem.setAttribute('aria-setsize', total);
        newsItem.setAttribute('aria-posinset', index + 1);
        
        const title = newsItem.querySelector('.news-title');
        if (title) {
            newsItem.setAttribute('aria-labelledby', title.id || `news-title-${index}`);
            if (!title.id) title.id = `news-title-${index}`;
        }
        
        const summary = newsItem.querySelector('.news-summary');
        if (summary) {
            newsItem.setAttribute('aria-describedby', summary.id || `news-summary-${index}`);
            if (!summary.id) summary.id = `news-summary-${index}`;
        }
    }
    
    /**
     * 初始化新闻项目的无障碍功能
     */
    initNewsAccessibility() {
        const newsItems = document.querySelectorAll('.news-item');
        newsItems.forEach((item, index) => {
            this.updateNewsItemAccessibility(item, index, newsItems.length);
        });
    }
}

// 初始化无障碍管理器
document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityManager = new AccessibilityManager();
    
    // 初始化新闻项目的无障碍功能
    setTimeout(() => {
        window.accessibilityManager.initNewsAccessibility();
    }, 100);
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityManager;
}