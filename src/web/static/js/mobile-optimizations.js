/**
 * 移动端优化脚本
 * 提供丝滑的移动端体验
 */

class MobileOptimizer {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.isScrolling = false;
        this.lastScrollTop = 0;
        this.init();
    }

    init() {
        console.log('📱 初始化移动端优化...');
        
        // 移动端汉堡菜单
        this.initMobileMenu();
        
        // 移动端优化主内容布局
        this.initMobileLayout();
        
        // 滚动优化
        this.initScrollOptimizations();
        
        // 触摸手势
        this.initTouchGestures();
        
        // 窗口大小变化监听
        this.initResponsiveHandlers();
        
        // 性能优化
        this.initPerformanceOptimizations();
        
        console.log('✅ 移动端优化初始化完成');
    }

    /**
     * 移动端布局优化
     */
    initMobileLayout() {
        if (!this.isMobile) return;
        
        // 确保主内容区域占满全宽
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.classList.add('full-width');
            mainContent.style.marginLeft = '0';
            console.log('📱 初始化 - 移动端主内容全宽');
        }
        
        // 移除任何可能存在的厂商导航元素
        const sidebar = document.getElementById('vendor-sidebar');
        if (sidebar) {
            sidebar.remove();
            console.log('📱 初始化 - 移除厂商导航元素');
        }
    }

    /**
     * 移动端菜单
     */
    initMobileMenu() {
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const navMenu = document.getElementById('nav-menu');
        
        if (mobileMenuBtn && navMenu) {
            // 汉堡菜单点击事件
            mobileMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleMobileMenu();
            });
            
            // 点击菜单项后关闭菜单
            navMenu.addEventListener('click', (e) => {
                if (e.target.classList.contains('nav-link')) {
                    this.closeMobileMenu();
                }
            });
            
            // 点击外部关闭菜单
            document.addEventListener('click', (e) => {
                if (!mobileMenuBtn.contains(e.target) && !navMenu.contains(e.target)) {
                    this.closeMobileMenu();
                }
            });
            
            // ESC键关闭菜单
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeMobileMenu();
                }
            });
        }
    }

    toggleMobileMenu() {
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const navMenu = document.getElementById('nav-menu');
        
        if (mobileMenuBtn && navMenu) {
            const isActive = mobileMenuBtn.classList.contains('active');
            
            if (isActive) {
                this.closeMobileMenu();
            } else {
                this.openMobileMenu();
            }
        }
    }

    openMobileMenu() {
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const navMenu = document.getElementById('nav-menu');
        
        if (mobileMenuBtn && navMenu) {
            mobileMenuBtn.classList.add('active');
            navMenu.classList.add('show');
            
            // 防止背景滚动
            document.body.style.overflow = 'hidden';
            
            // 添加动画类
            navMenu.style.animation = 'slideDown 0.3s ease-out';
        }
    }

    closeMobileMenu() {
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const navMenu = document.getElementById('nav-menu');
        
        if (mobileMenuBtn && navMenu) {
            mobileMenuBtn.classList.remove('active');
            navMenu.classList.remove('show');
            
            // 恢复背景滚动
            document.body.style.overflow = '';
            
            // 清除动画
            navMenu.style.animation = '';
        }
    }



    /**
     * 滚动优化
     */
    initScrollOptimizations() {
        let ticking = false;
        let scrollTimeout;
        
        const handleScroll = () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const header = document.getElementById('header');
            const sidebar = document.getElementById('vendor-sidebar');
            
            // 添加滚动阴影效果
            if (scrollTop > 10) {
                header?.classList.add('scrolled');
            } else {
                header?.classList.remove('scrolled');
            }
            
            // 移动端不自动隐藏厂商导航栏，因为它是水平布局，不影响阅读
            // 注释掉原来的自动隐藏逻辑
            /*
            if (this.isMobile && sidebar) {
                const scrollDirection = scrollTop > this.lastScrollTop ? 'down' : 'up';
                
                if (scrollDirection === 'down' && scrollTop > 100) {
                    sidebar.classList.add('hidden');
                }
            }
            */
            
            this.lastScrollTop = scrollTop;
            this.isScrolling = true;
            
            // 滚动结束检测
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.isScrolling = false;
            }, 150);
        };
        
        // 使用 requestAnimationFrame 优化滚动性能
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    /**
     * 触摸手势支持 - 特别优化iOS Safari
     */
    initTouchGestures() {
        // iOS Safari特殊处理
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        this.isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        
        if (this.isIOS) {
            this.initIOSOptimizations();
        }
        
        // 通用触摸手势
        if (!this.isMobile) return;
        
        this.initSwipeGestures();
        this.initPullToRefresh();
        this.initTouchFeedback();
    }
    
    /**
     * iOS特殊优化
     */
    initIOSOptimizations() {
        // 禁用iOS Safari的双击缩放
        document.addEventListener('touchstart', (e) => {
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });
        
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, { passive: false });
        
        // 修复iOS Safari的100vh问题
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', () => {
            setTimeout(setVH, 100);
        });
        
        // iOS Safari滚动优化
        document.body.style.webkitOverflowScrolling = 'touch';
        
        // 防止iOS Safari的橡皮筋效果影响体验
        document.body.addEventListener('touchmove', (e) => {
            if (e.target === document.body) {
                e.preventDefault();
            }
        }, { passive: false });
    }
    
    /**
     * 滑动手势
     */
    initSwipeGestures() {
        let startX, startY, startTime;
        let isSwipeGesture = false;
        
        document.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startTime = Date.now();
            isSwipeGesture = false;
            
            // 添加触摸反馈
            this.addTouchFeedback(e.target);
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            const touch = e.touches[0];
            const diffX = Math.abs(startX - touch.clientX);
            const diffY = Math.abs(startY - touch.clientY);
            
            // 判断是否为水平滑动手势
            if (diffX > diffY && diffX > 20) {
                isSwipeGesture = true;
            }
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY || !isSwipeGesture) {
                startX = startY = null;
                this.removeTouchFeedback();
                return;
            }
            
            const touch = e.changedTouches[0];
            const diffX = startX - touch.clientX;
            const diffY = startY - touch.clientY;
            const diffTime = Date.now() - startTime;
            
            // 检测滑动手势（快速滑动，时间短于500ms，水平距离大于50px）
            if (diffTime < 500 && Math.abs(diffX) > 50 && Math.abs(diffY) < 100) {
                const sidebar = document.getElementById('vendor-sidebar');
                const modal = document.querySelector('.modal.show');
                
                // 如果有模态框打开，优先处理模态框手势
                if (modal) {
                    if (diffX > 0) {
                        // 向左滑动关闭模态框
                        this.closeModal();
                    }
                } else if (sidebar) {
                    // 处理侧边栏手势
                    if (diffX > 0) {
                        // 向左滑动 - 隐藏侧边栏
                        sidebar.classList.add('hidden');
                    } else {
                        // 向右滑动 - 显示侧边栏
                        sidebar.classList.remove('hidden');
                    }
                    
                    // 添加触觉反馈（如果支持）
                    if (navigator.vibrate) {
                        navigator.vibrate(50);
                    }
                }
            }
            
            // 重置
            startX = startY = null;
            isSwipeGesture = false;
            this.removeTouchFeedback();
        }, { passive: true });
        
        // 阻止双指缩放以外的手势
        document.addEventListener('gesturestart', (e) => {
            e.preventDefault();
        });
    }
    
    /**
     * 下拉刷新
     */
    initPullToRefresh() {
        let startY = 0;
        let pullDistance = 0;
        let isPulling = false;
        const threshold = 80;
        
        const mainContent = document.querySelector('.main-content');
        if (!mainContent) return;
        
        mainContent.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        }, { passive: true });
        
        mainContent.addEventListener('touchmove', (e) => {
            if (!isPulling || window.scrollY > 0) return;
            
            const currentY = e.touches[0].clientY;
            pullDistance = Math.max(0, currentY - startY);
            
            if (pullDistance > 0) {
                e.preventDefault();
                const opacity = Math.min(pullDistance / threshold, 1);
                this.showPullToRefreshIndicator(opacity);
            }
        }, { passive: false });
        
        mainContent.addEventListener('touchend', () => {
            if (isPulling && pullDistance > threshold) {
                this.triggerRefresh();
            }
            
            isPulling = false;
            pullDistance = 0;
            this.hidePullToRefreshIndicator();
        }, { passive: true });
    }
    
    /**
     * 触摸反馈
     */
    initTouchFeedback() {
        // 为所有可点击元素添加触摸反馈
        const clickableElements = document.querySelectorAll('button, .nav-link, .news-item, .vendor-item');
        
        clickableElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                this.addTouchFeedback(element);
            }, { passive: true });
            
            element.addEventListener('touchend', () => {
                setTimeout(() => this.removeTouchFeedback(element), 150);
            }, { passive: true });
            
            element.addEventListener('touchcancel', () => {
                this.removeTouchFeedback(element);
            }, { passive: true });
        });
    }
    
    /**
     * 添加触摸反馈效果
     */
    addTouchFeedback(element) {
        if (!element) return;
        
        element.classList.add('touch-active');
        
        // 触觉反馈（如果支持）
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
    }
    
    /**
     * 移除触摸反馈效果
     */
    removeTouchFeedback(element) {
        if (element) {
            element.classList.remove('touch-active');
        } else {
            // 移除所有触摸反馈
            document.querySelectorAll('.touch-active').forEach(el => {
                el.classList.remove('touch-active');
            });
        }
    }
    
    /**
     * 显示下拉刷新指示器
     */
    showPullToRefreshIndicator(opacity) {
        let indicator = document.querySelector('.pull-refresh-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'pull-refresh-indicator';
            indicator.innerHTML = '<i class="fas fa-sync-alt"></i> 下拉刷新';
            document.body.appendChild(indicator);
        }
        
        indicator.style.opacity = opacity;
        indicator.style.transform = `translateY(${opacity * 50}px)`;
    }
    
    /**
     * 隐藏下拉刷新指示器
     */
    hidePullToRefreshIndicator() {
        const indicator = document.querySelector('.pull-refresh-indicator');
        if (indicator) {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateY(-50px)';
        }
    }
    
    /**
     * 触发刷新
     */
    triggerRefresh() {
        console.log('🔄 触发下拉刷新');
        
        // 显示刷新动画
        const indicator = document.querySelector('.pull-refresh-indicator');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> 刷新中...';
        }
        
        // 模拟刷新延迟
        setTimeout(() => {
            if (window.newsManager && typeof window.newsManager.loadNews === 'function') {
                window.newsManager.loadNews();
            } else {
                window.location.reload();
            }
        }, 1000);
    }

    /**
     * 响应式处理
     */
    initResponsiveHandlers() {
        let resizeTimer;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const newIsMobile = window.innerWidth <= 768;
                
                if (this.isMobile !== newIsMobile) {
                    this.isMobile = newIsMobile;
                    
                    // 重置菜单状态
                    this.closeMobileMenu();
                    
                    // 重置布局状态
                    const mainContent = document.querySelector('.main-content');
                    
                    if (newIsMobile) {
                        // 切换到移动端
                        if (mainContent) {
                            mainContent.classList.add('full-width');
                            mainContent.style.marginLeft = '0';
                        }
                        
                        // 移除任何厂商导航元素
                        const sidebar = document.getElementById('vendor-sidebar');
                        if (sidebar) {
                            sidebar.remove();
                        }
                        console.log('📱 响应式切换 - 移动端布局');
                    } else {
                        // 切换到桌面端 - 由NewsManager处理厂商导航创建
                        console.log('📱 响应式切换 - 桌面端布局');
                    }
                    
                    console.log(`📱 响应式切换: ${newIsMobile ? '移动端' : '桌面端'}`);
                }
            }, 250);
        });
        
        // 屏幕方向变化
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                // 强制重新计算viewport
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
                
                this.closeMobileMenu();
            }, 100);
        });
    }

    /**
     * 性能优化
     */
    initPerformanceOptimizations() {
        // 设置CSS自定义属性用于准确的viewport高度
        const setVh = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVh();
        window.addEventListener('resize', setVh);
        
        // 图片懒加载
        this.initLazyLoading();
        
        // 预加载关键资源
        this.preloadCriticalResources();
        
        // 减少重绘和回流
        this.optimizeAnimations();
    }

    /**
     * 图片懒加载
     */
    initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            observer.unobserve(img);
                        }
                    }
                });
            });
            
            // 观察所有懒加载图片
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    /**
     * 预加载关键资源
     */
    preloadCriticalResources() {
        // 预加载关键图标
        const criticalIcons = [
            'fas fa-home',
            'fas fa-chart-bar',
            'fas fa-search',
            'fas fa-sync-alt'
        ];
        
        // 预加载字体
        if ('fonts' in document) {
            document.fonts.ready.then(() => {
                console.log('🔤 字体加载完成');
            });
        }
    }

    /**
     * 动画优化
     */
    optimizeAnimations() {
        // 检查用户是否偏好减少动画
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        if (prefersReducedMotion.matches) {
            document.documentElement.classList.add('reduce-motion');
        }
        
        // 监听偏好变化
        prefersReducedMotion.addEventListener('change', (e) => {
            if (e.matches) {
                document.documentElement.classList.add('reduce-motion');
            } else {
                document.documentElement.classList.remove('reduce-motion');
            }
        });
    }

    /**
     * 关闭模态框
     */
    closeModal() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block' || modal.classList.contains('show')) {
                modal.style.display = 'none';
                modal.classList.remove('show');
            }
        });
    }

    /**
     * 添加触摸涟漪效果
     */
    addRippleEffect(element, event) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * 初始化触摸涟漪
     */
    initTouchRipples() {
        const rippleElements = document.querySelectorAll('.btn-primary, .btn-secondary, .nav-link, .news-item');
        
        rippleElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    this.addRippleEffect(element, e.touches[0]);
                }
            }, { passive: true });
        });
    }
    

}

// 等待DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 DOM加载完成，初始化移动端优化...');
    window.mobileOptimizer = new MobileOptimizer();
});

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileOptimizer;
}
