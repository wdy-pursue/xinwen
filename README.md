# 新闻热点聚合系统 - 重构版本

智能新闻资讯聚合平台，支持多平台热点新闻的抓取、分类和可视化展示。

## 🌟 功能特色

### 📰 多平台支持
- **微信读书** - 热门书籍和阅读趋势
- **知乎** - 热门问题和话题讨论
- **豆瓣** - 影视书籍评分和小组动态
- **小红书** - 生活方式和潮流资讯
- **今日热榜** - 全网热点聚合

### 🔍 智能筛选
- **全文搜索** - 支持标题、内容、摘要搜索
- **厂商筛选** - 按平台快速筛选内容
- **排行榜显示** - 显示各平台内容热度排名
- **分组展示** - 按厂商智能分组，清晰展示

### 🎨 现代界面
- **响应式设计** - 支持桌面端和移动端
- **美观布局** - 卡片式设计，视觉效果佳
- **厂商导航** - 左侧快速导航栏
- **实时统计** - 文章数量和厂商统计

## 🏗️ 系统架构

```
📁 项目根目录/
├── 📁 src/                    # 源代码目录
│   ├── 📁 api/                # 后端API
│   │   ├── 📁 controllers/    # 控制器
│   │   └── 📁 routes/         # 路由
│   ├── 📁 web/                # Web应用
│   │   ├── 📁 static/         # 静态资源
│   │   │   ├── 📁 css/        # 样式文件
│   │   │   └── 📁 js/         # JavaScript文件
│   │   └── 📁 templates/      # HTML模板
│   ├── 📁 crawlers/           # 爬虫模块
│   ├── 📁 services/           # 业务服务
│   └── 📁 storage/            # 数据存储
├── 📁 data/                   # 数据文件
├── 📁 logs/                   # 日志文件
├── 📄 config.ini              # 配置文件
├── 📄 requirements.txt        # 依赖文件
├── 📄 start_web_refactored.sh # Web服务管理脚本
└── 📄 run_once.sh             # 手动执行脚本
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 确保已安装Python 3.8+
python3 --version

# 安装依赖
pip install -r requirements.txt

# 安装浏览器依赖（用于爬虫）
playwright install chromium
playwright install-deps
```

### 2. 启动Web服务

```bash
# 启动Web服务器
./start_web_refactored.sh start

# 查看服务状态
./start_web_refactored.sh status

# 停止服务
./start_web_refactored.sh stop

# 重启服务
./start_web_refactored.sh restart
```

### 3. 访问系统

- **直接访问**: http://localhost:8080
- **Nginx代理**: http://localhost (需配置Nginx)

### 4. 数据抓取

```bash
# 手动执行一次抓取
./run_once.sh

# 或通过crontab定时执行
# 编辑crontab
crontab -e

# 添加定时任务（每6小时执行一次）
0 */6 * * * cd /path/to/project && ./run_once.sh
```

## 📖 API接口

### 获取新闻列表
```
GET /api/news?search=关键字&source=厂商&page=1&per_page=20
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "articles": [...],
    "vendors": ["微信读书", "知乎", "豆瓣"],
    "vendor_stats": {...},
    "pagination": {...}
  }
}
```

### 获取新闻详情
```
GET /api/news/{filename}
```

### 获取统计信息
```
GET /api/stats
```

## 🔧 配置说明

### config.ini 主要配置项

```ini
{
  "crawlers": {
    "enabled": ["nowhots"],
    "interval": 6,
    "description": "启用的爬虫和抓取间隔(小时)"
  },
  "email": {
    "enabled": false,
    "description": "邮件推送配置"
  },
  "wechat": {
    "enabled": false,
    "description": "微信公众号推送配置"
  },
  "data_management": {
    "cleanup_enabled": true,
    "keep_count": 200,
    "keep_days": 7,
    "description": "数据管理配置"
  }
}
```

## 📁 文件命名规范

新闻数据文件命名格式：
```
YYYY_MM_DD_HH_厂商_排名_标题_ID.txt

例如：
2025_08_11_14_weread_1_我在监狱服刑的日子_ecc99523.txt
└─年─月─日─时─厂商─排名─────标题────────唯一ID
```

## 🎯 使用说明

### 前端功能

1. **搜索功能**
   - 在搜索框输入关键字
   - 支持实时搜索，自动过滤结果

2. **厂商筛选**
   - 下拉选择特定厂商
   - 显示该厂商的所有新闻

3. **厂商导航**
   - 点击"厂商导航"按钮
   - 左侧显示所有厂商列表
   - 点击厂商名称快速跳转

4. **排行榜显示**
   - 按厂商分组展示
   - 显示每条新闻在该厂商的排名
   - 按排名正序排列（#1在前）

### 数据管理

- **自动清理**: 保留最新200篇文章或7天内数据
- **手动清理**: 可在配置文件中调整
- **数据备份**: 定期备份data目录

## 🔧 高级配置

### Nginx代理配置

```nginx
server {
    listen 80;
    server_name _;

    # 静态文件
    location /static/ {
        alias /path/to/project/src/web/static/;
        expires 7d;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 主页
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 性能优化

1. **缓存配置**
   - 静态资源长期缓存
   - API响应短期缓存

2. **数据库优化**
   - 定期清理过期数据
   - 建立合适的索引

3. **网络优化**
   - 启用Gzip压缩
   - 使用CDN加速

## 🐛 故障排除

### 常见问题

1. **Web服务无法启动**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep :8080
   
   # 查看日志
   tail -f logs/web_server.log
   ```

2. **前端无法加载**
   ```bash
   # 检查静态文件路径
   ls -la src/web/static/
   
   # 检查浏览器Console错误
   ```

3. **数据无法显示**
   ```bash
   # 检查数据文件
   ls -la data/
   
   # 检查API响应
   curl http://localhost:8080/api/news
   ```

### 日志查看

```bash
# Web服务器日志
tail -f logs/web_server.log

# 爬虫日志
tail -f crawler.log

# 系统日志
journalctl -u your-service-name
```

## 📞 技术支持

如遇问题，请检查：

1. ✅ Python环境是否正确安装
2. ✅ 依赖包是否完整安装  
3. ✅ 配置文件是否正确
4. ✅ 网络连接是否正常
5. ✅ 文件权限是否正确

## 📝 更新日志

### v2.0 (重构版本)
- ✨ 重构前后端代码架构
- 🔧 修复厂商筛选功能
- 🎨 优化前端界面和交互
- 📊 改进数据排序和分组
- 🧹 清理无用代码和文件
- 📁 规范文件夹和文件命名

### v1.0 (初始版本)
- 🎉 基础功能实现
- 📰 多平台新闻抓取
- 🌐 Web界面展示
- 📧 邮件推送功能
