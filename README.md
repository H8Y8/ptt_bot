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

## 安裝

1. 克隆此儲存庫
2. 安裝依賴：`pip install -r requirements.txt`
3. 設置環境變數（參見 `.env.example`）

## 使用方法

- 運行爬蟲：`python ptt_crawler.py`
- 生成摘要：`python gemini_ptt_summary.py`
- 啟動 Web 應用：`gunicorn app:app`

## Heroku 部署

本專案已配置為可在 Heroku 上部署。主要更改包括：

- 使用 PostgreSQL 替代 SQLite
- 添加 `Procfile` 定義 Heroku 進程
- 更新 `requirements.txt` 以包含所有必要依賴
- 修改數據庫連接邏輯以支持 Heroku PostgreSQL

## 環境變量

確保在 Heroku 上設置以下環境變量：

- `DATABASE_URL`: PostgreSQL 數據庫 URL（Heroku 自動提供）
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
