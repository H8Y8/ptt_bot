# PTT 爬蟲專案

這是一個用於爬取 PTT 特定用戶文章的 Python 專案。

## 功能

- 爬取指定 PTT 用戶在特定版面的文章
- 將文章資訊儲存到 SQLite 資料庫
- 使用 LINE Notify 發送新文章通知

## 安裝

1. 克隆此儲存庫
2. 安裝依賴：`pip install -r requirements.txt`
3. 設置環境變數（參見 `.env.example`）

## 使用方法

運行 `python ptt_crawler.py`

## 注意事項

請確保遵守 PTT 的使用條款和爬蟲禮儀。
