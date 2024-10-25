import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import logging
from datetime import datetime
import time

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 資料庫路徑
db_path = os.path.join(os.getcwd(), 'ptt_articles.db')

def get_article_date(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('meta', {'itemprop': 'datePublished'})
        if date_element and 'content' in date_element.attrs:
            date_str = date_element['content']
            # 解析 ISO 格式的日期時間
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date.strftime('%Y-%m-%d')
    except Exception as e:
        logger.error(f"獲取文章日期時出錯: {e}")
    return None

def update_article_dates():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 檢查是否已存在 date 欄位
    c.execute("PRAGMA table_info(articles)")
    columns = [column[1] for column in c.fetchall()]
    if 'date' not in columns:
        c.execute('ALTER TABLE articles ADD COLUMN date TEXT')
        conn.commit()
        logger.info("已添加 date 欄位到 articles 表")

    c.execute("SELECT id, url FROM articles WHERE date IS NULL OR date = ''")
    articles = c.fetchall()
    
    for article_id, url in articles:
        date = get_article_date(url)
        if date:
            c.execute("UPDATE articles SET date = ? WHERE id = ?", (date, article_id))
            logger.info(f"更新文章 {article_id} 的日期: {date}")
        else:
            logger.warning(f"無法獲取文章 {article_id} 的日期")
        
        # 添加延遲以避免對網站造成過大壓力
        time.sleep(1)
    
    conn.commit()
    conn.close()
    logger.info("文章日期更新完成")

if __name__ == "__main__":
    update_article_dates()