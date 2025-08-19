/**
 * 现代化动画管理器
 * 提供加载动画、微交互效果和页面转场动画
 */
class AnimationManager {
    constructor() {
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.observers = new Map();
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupLoadingAnimations();
        this.setupMicroInteractions();
        this.setupPageTransitions();
        this.setupSkeletonLoading();
    }

    /**
     * 设置交叉观察器用于滚动动画
     */
    setupIntersectionObserver() {
        if (this.isReducedMotion) return;

        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // 观察所有需要动画的元素
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });

        this.observers.set('scroll', observer);
    }

    /**
     * 设置加载动画
     */
    setupLoadingAnimations() {
        // 创建全局加载指示器
        this.createGlobalLoader();
        
        // 为异步操作添加加载状态
        this.setupAsyncLoadingStates();
    }

    /**
     * 创建全局加载指示器
     */
    createGlobalLoader() {
        const loader = document.createElement('div');
        loader.className = 'global-loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="loader-spinner"></div>
                <div class="loader-text">加载中...</div>
            </div>
        `;
        document.body.appendChild(loader);
    }

    /**
     * 显示全局加载器
     */
    showGlobalLoader(text = '加载中...') {
        const loader = document.querySelector('.global-loader');
        const loaderText = loader.querySelector('.loader-text');
        if (loaderText) loaderText.textContent = text;
        loader.classList.add('active');
    }

    /**
     * 隐藏全局加载器
     */
    hideGlobalLoader() {
        const loader = document.querySelector('.global-loader');
        loader.classList.remove('active');
    }

    /**
     * 设置异步加载状态
     */
    setupAsyncLoadingStates() {
        // 为搜索按钮添加加载状态
        const searchBtn = document.querySelector('.search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.addLoadingState(searchBtn, '搜索中...');
            });
        }

        // 为刷新按钮添加加载状态
        const refreshBtns = document.querySelectorAll('.refresh-btn');
        refreshBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.addLoadingState(btn, '刷新中...');
            });
        });
    }

    /**
     * 为元素添加加载状态
     */
    addLoadingState(element, text = '加载中...') {
        if (element.classList.contains('loading')) return;
        
        element.classList.add('loading');
        const originalText = element.textContent;
        element.setAttribute('data-original-text', originalText);
        element.textContent = text;
        
        // 添加加载图标
        const spinner = document.createElement('span');
        spinner.className = 'loading-spinner';
        element.prepend(spinner);
    }

    /**
     * 移除元素加载状态
     */
    removeLoadingState(element) {
        element.classList.remove('loading');
        const originalText = element.getAttribute('data-original-text');
        if (originalText) {
            element.textContent = originalText;
            element.removeAttribute('data-original-text');
        }
        
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) spinner.remove();
    }

    /**
     * 设置微交互效果
     */
    setupMicroInteractions() {
        if (this.isReducedMotion) return;

        // 按钮悬停效果
        this.setupButtonHoverEffects();
        
        // 卡片悬停效果
        this.setupCardHoverEffects();
        
        // 输入框焦点效果
        this.setupInputFocusEffects();
        
        // 点击涟漪效果
        this.setupRippleEffects();
    }

    /**
     * 设置按钮悬停效果
     */
    setupButtonHoverEffects() {
        const buttons = document.querySelectorAll('button, .btn');
        buttons.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.classList.add('hover-scale');
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.classList.remove('hover-scale');
            });
        });
    }

    /**
     * 设置卡片悬停效果
     */
    setupCardHoverEffects() {
        const cards = document.querySelectorAll('.news-item, .vendor-item');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('hover-lift');
            });
            
            card.addEventListener('mouseleave', () => {
                card.classList.remove('hover-lift');
            });
        });
    }

    /**
     * 设置输入框焦点效果
     */
    setupInputFocusEffects() {
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.classList.add('focus-glow');
            });
            
            input.addEventListener('blur', () => {
                input.classList.remove('focus-glow');
            });
        });
    }

    /**
     * 设置点击涟漪效果
     */
    setupRippleEffects() {
        const rippleElements = document.querySelectorAll('.ripple-effect, button, .btn');
        rippleElements.forEach(el => {
            el.addEventListener('click', (e) => {
                this.createRipple(e, el);
            });
        });
    }

    /**
     * 创建涟漪效果
     */
    createRipple(event, element) {
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * 设置页面转场动画
     */
    setupPageTransitions() {
        if (this.isReducedMotion) return;

        // 页面加载动画
        document.addEventListener('DOMContentLoaded', () => {
            document.body.classList.add('page-loaded');
        });

        // 链接点击转场效果
        const links = document.querySelectorAll('a[href]:not([href^="#"]):not([target="_blank"])');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                if (e.ctrlKey || e.metaKey) return; // 允许在新标签页打开
                
                e.preventDefault();
                const href = link.href;
                
                document.body.classList.add('page-transition');
                
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            });
        });
    }

    /**
     * 设置骨架屏加载
     */
    setupSkeletonLoading() {
        // 为新闻列表添加骨架屏
        this.createNewsSkeleton();
    }

    /**
     * 创建新闻骨架屏
     */
    createNewsSkeleton() {
        const newsContainer = document.querySelector('.news-grid');
        if (!newsContainer) return;

        const skeletonHTML = `
            <div class="news-skeleton">
                <div class="skeleton-header"></div>
                <div class="skeleton-content">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                </div>
                <div class="skeleton-footer"></div>
            </div>
        `;

        // 显示骨架屏
        this.showSkeleton = () => {
            newsContainer.innerHTML = Array(6).fill(skeletonHTML).join('');
        };

        // 隐藏骨架屏
        this.hideSkeleton = () => {
            const skeletons = newsContainer.querySelectorAll('.news-skeleton');
            skeletons.forEach(skeleton => skeleton.remove());
        };
    }

    /**
     * 淡入动画
     */
    fadeIn(element, duration = 300) {
        if (this.isReducedMotion) {
            element.style.opacity = '1';
            return Promise.resolve();
        }

        return new Promise(resolve => {
            element.style.opacity = '0';
            element.style.transition = `opacity ${duration}ms ease`;
            
            requestAnimationFrame(() => {
                element.style.opacity = '1';
                setTimeout(resolve, duration);
            });
        });
    }

    /**
     * 淡出动画
     */
    fadeOut(element, duration = 300) {
        if (this.isReducedMotion) {
            element.style.opacity = '0';
            return Promise.resolve();
        }

        return new Promise(resolve => {
            element.style.transition = `opacity ${duration}ms ease`;
            element.style.opacity = '0';
            setTimeout(resolve, duration);
        });
    }

    /**
     * 滑入动画
     */
    slideIn(element, direction = 'up', duration = 300) {
        if (this.isReducedMotion) return Promise.resolve();

        return new Promise(resolve => {
            const transforms = {
                up: 'translateY(20px)',
                down: 'translateY(-20px)',
                left: 'translateX(20px)',
                right: 'translateX(-20px)'
            };

            element.style.transform = transforms[direction];
            element.style.opacity = '0';
            element.style.transition = `all ${duration}ms ease`;
            
            requestAnimationFrame(() => {
                element.style.transform = 'translate(0)';
                element.style.opacity = '1';
                setTimeout(resolve, duration);
            });
        });
    }

    /**
     * 清理资源
     */
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
    }
}

// 全局实例
window.animationManager = new AnimationManager();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnimationManager;
}