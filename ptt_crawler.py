import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import sqlite3
from line_notify import send_line_notify
import logging
from datetime import datetime
import psycopg2
from urllib.parse import urlparse

# 在文件開頭添加以下代碼
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入 .env 檔案
load_dotenv()

# 現在您可以使用 os.getenv 來獲取環境變數
PTT_BOARD = os.getenv('PTT_BOARD')
PTT_USER = os.getenv('PTT_USER')
LINE_NOTIFY_TOKEN = os.getenv('LINE_NOTIFY_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# 替換 SQLite 連接代碼
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # 使用 PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
else:
    # 使用 SQLite
    conn = sqlite3.connect('ptt_articles.db')

c = conn.cursor()

# 建立文章資料表（如果不存在）
c.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT,
        url TEXT,
        comment TEXT,
        date TEXT
    )
''')
conn.commit()

# LINE Notify 權杖，從 LINE Notify 官網取得
#LINE_NOTIFY_TOKEN = os.getenv('LINE_NOTIFY_TOKEN')
#PTT_BOARD = os.getenv('PTT_BOARD')
#PTT_BOARD = ''
# PTT 用戶

#PTT_USER = os.getenv('PTT_USER')
#PTT_USER = 'jose50203'
# 測試用變數，之後應移除或替換為環境變數
#LINE_NOTIFY_TOKEN = "8XV2F5mqv9Bzlm0M6jVrKXwsaKaP5SvOWI3qXRxSICQ"  # 測試用，之後應移除
#PTT_board = ""  # 測試用，之後應填入適當的版面名稱
#PTT_USER = "jose50203"  # 測試用，之後應移除

# 定義抓取文章資訊的函數
def get_articles():
    url = f"https://www.pttweb.cc/user/{PTT_USER}/{PTT_BOARD}?t=message"
    logger.info(f"文章網址: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 抓取所有包含文章的 div，class="thread-item"
    articles = soup.find_all("div", class_="thread-item")

    article_data = []
    for article in articles:
        # 抓取文章主旨
        title_tag = article.find("span", class_="thread-title")
        title = title_tag.text if title_tag else "無標題"

        # 抓取文章網址
        link_tag = article.find("a", href=True)
        url = f"https://www.pttweb.cc{link_tag['href']}" if link_tag else "無連結"
        logger.info(f"文章網址: {url}")
        # 抓取所有推文內容
        comments = []
        comment_tags = article.find_all("span", class_="yellow--text text--darken-2")
        for comment_tag in comment_tags:
            comment = comment_tag.text.strip() if comment_tag else "無推文"
            comments.append(comment)

        # 將推文合併為一個字串
        comments_str = "\n".join(comments)
        # 生成文章的唯一 ID（可使用 URL 當作 ID）
        article_id = url.split('/')[-1]

        # 獲取文章日期
        date = get_article_date(url)

        # 將文章資訊加入列表
        article_data.append((article_id, title, url, comments_str, date))

    return article_data

# 新增 get_article_date 函數
def get_article_date(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('meta', {'itemprop': 'datePublished'})
        if date_element and 'content' in date_element.attrs:
            date_str = date_element['content']
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date.strftime('%Y-%m-%d')
    except Exception as e:
        logger.error(f"獲取文章日期時出錯: {e}")
    return None

# 檢查是否有新文章
def check_for_new_articles():
    logger.info("開始檢查新文章")
    current_articles = get_articles()
    logger.info(f"獲取到 {len(current_articles)} 篇文章")

    # 從資料庫中提取已有的文章 ID
    c.execute("SELECT id FROM articles")
    existing_articles = set(row[0] for row in c.fetchall())

    # 新文章 = 當前抓取到的文章 - 資料庫中的文章
    new_articles = [(article_id, title, url, comments_str, date) for article_id, title, url, comments_str, date in current_articles if article_id not in existing_articles]

    if new_articles:
        logger.info(f"發現 {len(new_articles)} 篇新文章")
        for article in new_articles:
            logger.info(f"發送通知: {article[1]}")
            message = f"\n主旨: {article[1]}\n網址: {article[2]}\n日期: {article[4]}\n推文 {article[3]}"
            #print(message)
            send_line_notify(message)
    else:
        logger.info("沒有發現新文章")

    # 將新文章插入資料庫
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        c.executemany("INSERT INTO articles (id, title, url, comment, date) VALUES (%s, %s, %s, %s, %s)", new_articles)
    else:
        c.executemany("INSERT INTO articles (id, title, url, comment, date) VALUES (?, ?, ?, ?, ?)", new_articles)
    conn.commit()

# 測試 LINE Notify
def test_line_notify():
    logger.info("測試 LINE Notify")
    message = "這是一條測試訊息"
    send_line_notify(message)

# 將主循環改為單次執行
def main():
    #test_line_notify()
    check_for_new_articles()

if __name__ == "__main__":
    main()
