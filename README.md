# PTT 爬蟲與摘要生成專案

這是一個用於爬取 PTT 特定用戶文章、生成摘要，並提供 Web 介面顯示隨機評論的 Python 專案。

## 功能

- 爬取指定 PTT 用戶在特定版面的文章
- 使用 Gemini AI 生成文章摘要
- 將文章資訊儲存到 PostgreSQL 數據庫
- 使用 LINE Notify 發送新文章通知和摘要
- 提供 Web 介面顯示隨機評論

## 主要文件

- `ptt_crawler.py`: PTT 爬蟲腳本
- `gemini_ptt_summary.py`: 使用 Gemini AI 生成摘要的腳本
- `app.py`: Flask Web 應用，提供隨機評論顯示功能
- `line_notify.py`: LINE Notify 通知功能
- `migrate_data.py`: 數據遷移腳本（SQLite 到 PostgreSQL）
- `scheduler.py`: 排程器，用於定期執行爬蟲和摘要生成

## 安裝

1. 克隆此儲存庫
2. 安裝依賴：`pip install -r requirements.txt`
3. 設置環境變數（參見 `.env.example`）

## 使用方法

- 運行爬蟲：`python ptt_crawler.py`
- 生成摘要：`python gemini_ptt_summary.py`
- 啟動 Web 應用：`gunicorn app:app`
- 運行排程器：`python scheduler.py`

## 部署方式

### 1. Heroku 部署

本專案已配置為可在 Heroku 上部署。主要更改包括：

- 使用 PostgreSQL 替代 SQLite
- 添加 `Procfile` 定義 Heroku 進程
- 更新 `requirements.txt` 以包含所有必要依賴
- 修改數據庫連接邏輯以支持 Heroku PostgreSQL

部署步驟：

1. 創建 Heroku 應用：`heroku create 您的應用名稱`
2. 設置環境變量：`heroku config:set 變量名稱=變量值`
3. 推送代碼到 Heroku：`git push heroku main`
4. 運行數據庫遷移（如需要）`python migrate_data.py`
5. 啟動 worker：`heroku ps:scale worker=1`

### 2. Docker 部署

本專案支持使用 Docker 進行部署，包括 Web 應用、PTT 爬蟲和 Gemini 摘要生成器。

準備工作：

1. 安裝 Docker 和 Docker Compose

部署步驟：

1. 確保專案根目錄中有 `Dockerfile`，內容如下：

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "scheduler.py"]
   ```

2. 創建 `docker-compose.yml` 文件：

   ```yaml
   version: "3"
   services:
     web:
       build: .
       ports:
         - "5000:5000"
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/pttdb
       depends_on:
         - db
       command: gunicorn app:app -b 0.0.0.0:5000

     crawler:
       build: .
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/pttdb
       depends_on:
         - db
       command: python scheduler.py

     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=pttdb
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data

   volumes:
     postgres_data:
   ```

3. 構建和運行 Docker 容器：

   ```
   docker-compose up --build
   ```

4. 訪問 `http://localhost:5000` 查看 Web 應用
5. 爬蟲和摘要生成器將根據 `scheduler.py` 中的設定自動運行

注意：確保將敏感信息（如數據庫密碼和 API 密鑰）替換為安全的值，並使用環境變量或 Docker secrets 進行管理。

## 環境設置

1. 複製 `.env.example` 文件並重命名為 `.env`
2. 在 `.env` 文件中填入您的實際配置值

注意：不要將您的 `.env` 文件提交到版本控制系統中。

## 環境變量

確保設置以下環境變量：

- `DATABASE_URL`: PostgreSQL 數據庫 URL
- `PTT_BOARD`: PTT 版面名稱
- `PTT_USER`: PTT 用戶名
- `LINE_NOTIFY_TOKEN`: LINE Notify 權杖
- `GEMINI_API_KEY`: Gemini AI API 金鑰

## 注意事項

- 請確保遵守 PTT 的使用條款和爬蟲禮儀
- 定期檢查並更新依賴以確保安全性
- 在生產環境中禁用 Flask 的調試模式

## 貢獻

歡迎提交 Pull Requests 或開 Issue 討論新功能和改進建議。

## 授權

[MIT License](LICENSE)
