/**
 * 现代化主题管理器
 * 支持亮色/暗色/自动模式，完美适配各种设备
 */

class ThemeManager {
    constructor() {
        this.themes = {
            light: 'light',
            dark: 'dark',
            auto: 'auto'
        };
        
        this.currentTheme = this.getStoredTheme() || this.themes.auto;
        this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        this.init();
    }

    init() {
        console.log('🎨 初始化主题管理器...');
        
        // 应用初始主题
        this.applyTheme(this.currentTheme);
        
        // 监听系统主题变化
        this.mediaQuery.addEventListener('change', () => {
            if (this.currentTheme === this.themes.auto) {
                this.applyTheme(this.themes.auto);
            }
        });
        
        // 创建主题切换按钮
        this.createThemeToggle();
        
        // 监听存储变化（多标签页同步）
        window.addEventListener('storage', (e) => {
            if (e.key === 'theme-preference') {
                this.currentTheme = e.newValue || this.themes.auto;
                this.applyTheme(this.currentTheme);
                this.updateToggleButton();
            }
        });
        
        console.log('✅ 主题管理器初始化完成');
    }

    /**
     * 获取存储的主题偏好
     */
    getStoredTheme() {
        try {
            return localStorage.getItem('theme-preference');
        } catch (e) {
            console.warn('无法访问localStorage，使用默认主题');
            return null;
        }
    }

    /**
     * 存储主题偏好
     */
    storeTheme(theme) {
        try {
            localStorage.setItem('theme-preference', theme);
        } catch (e) {
            console.warn('无法保存主题偏好到localStorage');
        }
    }

    /**
     * 应用主题
     */
    applyTheme(theme) {
        const root = document.documentElement;
        const body = document.body;
        
        // 移除所有主题类
        root.classList.remove('theme-light', 'theme-dark', 'theme-auto');
        body.classList.remove('theme-light', 'theme-dark', 'theme-auto');
        
        // 应用新主题
        if (theme === this.themes.auto) {
            const prefersDark = this.mediaQuery.matches;
            root.classList.add('theme-auto');
            body.classList.add('theme-auto');
            
            if (prefersDark) {
                root.classList.add('theme-dark');
                body.classList.add('theme-dark');
            } else {
                root.classList.add('theme-light');
                body.classList.add('theme-light');
            }
        } else {
            root.classList.add(`theme-${theme}`);
            body.classList.add(`theme-${theme}`);
        }
        
        // 更新CSS自定义属性
        this.updateCSSVariables(theme);
        
        // 触发主题变化事件
        this.dispatchThemeChangeEvent(theme);
        
        console.log(`🎨 应用主题: ${theme}`);
    }

    /**
     * 更新CSS自定义属性
     */
    updateCSSVariables(theme) {
        const root = document.documentElement;
        const isDark = theme === this.themes.dark || 
                      (theme === this.themes.auto && this.mediaQuery.matches);
        
        if (isDark) {
            // 暗色主题变量
            root.style.setProperty('--primary-color', '#818cf8');
            root.style.setProperty('--primary-gradient', 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)');
            root.style.setProperty('--secondary-color', '#1e293b');
            root.style.setProperty('--accent-color', '#60a5fa');
            root.style.setProperty('--text-color', '#f1f5f9');
            root.style.setProperty('--text-muted', '#94a3b8');
            root.style.setProperty('--text-light', '#64748b');
            root.style.setProperty('--border-color', '#334155');
            root.style.setProperty('--bg-color', '#0f172a');
            root.style.setProperty('--bg-surface', '#1e293b');
            root.style.setProperty('--success-color', '#34d399');
            root.style.setProperty('--warning-color', '#fbbf24');
            root.style.setProperty('--error-color', '#f87171');
        } else {
            // 亮色主题变量
            root.style.setProperty('--primary-color', '#667eea');
            root.style.setProperty('--primary-gradient', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)');
            root.style.setProperty('--secondary-color', '#f8fafc');
            root.style.setProperty('--accent-color', '#3b82f6');
            root.style.setProperty('--text-color', '#1e293b');
            root.style.setProperty('--text-muted', '#64748b');
            root.style.setProperty('--text-light', '#94a3b8');
            root.style.setProperty('--border-color', '#e2e8f0');
            root.style.setProperty('--bg-color', '#ffffff');
            root.style.setProperty('--bg-surface', '#f8fafc');
            root.style.setProperty('--success-color', '#10b981');
            root.style.setProperty('--warning-color', '#f59e0b');
            root.style.setProperty('--error-color', '#ef4444');
        }
    }

    /**
     * 创建主题切换按钮
     */
    createThemeToggle() {
        const navMenu = document.querySelector('.nav-menu');
        if (!navMenu) return;
        
        // 创建主题切换按钮
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle nav-link';
        themeToggle.setAttribute('aria-label', '切换主题');
        themeToggle.setAttribute('title', '切换主题');
        
        // 添加图标和文本
        themeToggle.innerHTML = `
            <i class="fas fa-palette theme-icon"></i>
            <span class="theme-text">主题</span>
        `;
        
        // 添加点击事件
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleTheme();
        });
        
        // 插入到导航菜单中
        navMenu.appendChild(themeToggle);
        
        // 更新按钮状态
        this.updateToggleButton();
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        const themes = Object.values(this.themes);
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        
        this.setTheme(themes[nextIndex]);
    }

    /**
     * 设置主题
     */
    setTheme(theme) {
        if (!Object.values(this.themes).includes(theme)) {
            console.warn(`未知主题: ${theme}`);
            return;
        }
        
        this.currentTheme = theme;
        this.storeTheme(theme);
        this.applyTheme(theme);
        this.updateToggleButton();
    }

    /**
     * 更新切换按钮状态
     */
    updateToggleButton() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (!themeToggle) return;
        
        const icon = themeToggle.querySelector('.theme-icon');
        const text = themeToggle.querySelector('.theme-text');
        
        if (!icon || !text) return;
        
        // 更新图标和文本
        switch (this.currentTheme) {
            case this.themes.light:
                icon.className = 'fas fa-sun theme-icon';
                text.textContent = '亮色';
                themeToggle.setAttribute('title', '当前: 亮色主题');
                break;
            case this.themes.dark:
                icon.className = 'fas fa-moon theme-icon';
                text.textContent = '暗色';
                themeToggle.setAttribute('title', '当前: 暗色主题');
                break;
            case this.themes.auto:
                icon.className = 'fas fa-adjust theme-icon';
                text.textContent = '自动';
                themeToggle.setAttribute('title', '当前: 跟随系统');
                break;
        }
        
        // 添加切换动画
        icon.style.transform = 'scale(0.8)';
        setTimeout(() => {
            icon.style.transform = 'scale(1)';
        }, 150);
    }

    /**
     * 触发主题变化事件
     */
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: {
                theme: theme,
                isDark: theme === this.themes.dark || 
                       (theme === this.themes.auto && this.mediaQuery.matches)
            }
        });
        
        document.dispatchEvent(event);
    }

    /**
     * 获取当前主题
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * 判断当前是否为暗色主题
     */
    isDarkTheme() {
        return this.currentTheme === this.themes.dark || 
               (this.currentTheme === this.themes.auto && this.mediaQuery.matches);
    }
}

// 全局实例
let themeManager;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    themeManager = new ThemeManager();
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}

// 全局访问
window.ThemeManager = ThemeManager;
window.getThemeManager = () => themeManager;