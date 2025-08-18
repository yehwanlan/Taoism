# 🚀 安裝和部署指南

## 📋 系統需求

- Python 3.7+
- Git（用於 GitHub Pages 部署）
- Docker（可選，用於容器化部署）

## 🎯 快速開始

### 方法一：一鍵安裝（推薦）

```bash
# 1. 克隆專案
git clone https://github.com/your-username/taoism-translation-system.git
cd taoism-translation-system

# 2. 執行安裝腳本
python setup.py

# 3. 啟動系統
python main.py
```

### 方法二：手動安裝

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 複製配置檔案
cp config/settings.example.json config/settings.json

# 3. 啟動系統
python main.py info
```

### 方法三：使用 pip 安裝（開發中）

```bash
# 從 PyPI 安裝（未來版本）
pip install taoism-translation-system

# 或從源碼安裝
pip install -e .
```

## 🌐 部署選項

### 1. GitHub Pages 部署（推薦）

```bash
# 一鍵部署到 GitHub Pages
python deploy.py github
```

**特點：**
- ✅ 免費託管
- ✅ 自動 HTTPS
- ✅ 全球 CDN
- ✅ 自動更新

**訪問地址：** `https://your-username.github.io/taoism-translation-system/`

### 2. Docker 部署

```bash
# 使用 Docker Compose（推薦）
python deploy.py docker

# 或手動 Docker 部署
docker build -t taoism-translation .
docker run -p 8000:8000 taoism-translation
```

**特點：**
- ✅ 環境隔離
- ✅ 易於擴展
- ✅ 跨平台一致性

**訪問地址：** `http://localhost:8000`

### 3. 本地服務

```bash
# 啟動本地服務（預設端口 8000）
python deploy.py local

# 指定端口
python deploy.py local 3000
```

**特點：**
- ✅ 快速測試
- ✅ 開發友好
- ✅ 無需額外配置

### 4. 完整部署流程

```bash
# 執行完整部署（包含打包和 GitHub Pages）
python deploy.py all
```

## 📦 打包和分發

### 創建發布包

```bash
# 創建可分發的 ZIP 包
python deploy.py package
```

生成的包包含：
- 完整的應用程式碼
- 所有必要的配置檔案
- 使用說明文檔
- 安裝腳本

### 構建 Python 包

```bash
# 構建 wheel 包
pip install build
python -m build

# 上傳到 PyPI（維護者使用）
pip install twine
twine upload dist/*
```

## ⚙️ 配置說明

### 基本配置

編輯 `config/settings.json`：

```json
{
  "translation": {
    "auto_translate": true,
    "batch_size": 10,
    "output_format": "markdown"
  },
  "tracking": {
    "enable_monitoring": true,
    "log_level": "INFO"
  },
  "web": {
    "port": 8000,
    "host": "0.0.0.0"
  }
}
```

### 環境變數

```bash
# 可選的環境變數
export TAOISM_CONFIG_PATH="/path/to/config"
export TAOISM_DATA_PATH="/path/to/data"
export TAOISM_LOG_LEVEL="DEBUG"
```

## 🔧 開發環境設置

### 1. 開發安裝

```bash
# 克隆專案
git clone https://github.com/your-username/taoism-translation-system.git
cd taoism-translation-system

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安裝開發依賴
pip install -e ".[dev]"
```

### 2. 運行測試

```bash
# 運行所有測試
pytest

# 運行測試並生成覆蓋率報告
pytest --cov=core --cov=tools
```

### 3. 代碼格式化

```bash
# 格式化代碼
black .

# 檢查代碼風格
flake8 .
```

## 🐳 Docker 詳細配置

### 自定義 Docker 配置

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  taoism-app:
    ports:
      - "3000:8000"  # 自定義端口
    environment:
      - TAOISM_LOG_LEVEL=DEBUG
    volumes:
      - ./custom-config:/app/config
```

### 生產環境部署

```bash
# 生產環境配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🌐 網頁服務配置

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Apache 配置

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
</VirtualHost>
```

## 🔍 故障排除

### 常見問題

1. **Python 版本錯誤**
   ```bash
   # 檢查 Python 版本
   python --version
   # 使用特定版本
   python3.9 main.py
   ```

2. **依賴安裝失敗**
   ```bash
   # 升級 pip
   pip install --upgrade pip
   # 清除快取
   pip cache purge
   ```

3. **端口被佔用**
   ```bash
   # 查找佔用端口的程序
   netstat -tulpn | grep 8000
   # 使用其他端口
   python deploy.py local 3000
   ```

4. **權限問題**
   ```bash
   # Linux/Mac 設置權限
   chmod +x deploy.py
   chmod +x main.py
   ```

### 日誌檢查

```bash
# 查看應用日誌
tail -f data/logs/activity_report.md

# Docker 日誌
docker-compose logs -f taoism-app
```

## 📊 性能優化

### 生產環境建議

1. **使用 CDN** - 加速靜態資源載入
2. **啟用 Gzip** - 壓縮傳輸內容
3. **設置快取** - 減少重複請求
4. **監控資源** - 定期檢查系統狀態

### 資料庫優化

```bash
# 清理舊日誌
python tools/temp/clear_cache_and_test.py

# 壓縮資料檔案
gzip data/logs/*.log
```

## 🔄 更新和維護

### 更新系統

```bash
# 拉取最新代碼
git pull origin main

# 更新依賴
pip install -r requirements.txt --upgrade

# 重新部署
python deploy.py github
```

### 備份資料

```bash
# 備份重要資料
cp -r data/ backup/data_$(date +%Y%m%d)
cp -r docs/translations/ backup/translations_$(date +%Y%m%d)
```

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 創建 Pull Request

詳細說明請參考 [README.md](README.md)

---

**需要幫助？** 請查看 [使用指南](docs/system/工具使用指南.md) 或提交 [Issue](https://github.com/your-username/taoism-translation-system/issues)