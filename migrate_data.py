import sqlite3
import psycopg2
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite 連接
sqlite_conn = sqlite3.connect('ptt_articles.db')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL 連接
DATABASE_URL = os.getenv('DATABASE_URL')
url = urlparse(DATABASE_URL)
pg_conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
pg_cursor = pg_conn.cursor()

# 創建 PostgreSQL 表
pg_cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT,
        url TEXT,
        comment TEXT,
        date TEXT
    )
''')

# 從 SQLite 讀取數據
sqlite_cursor.execute("SELECT * FROM articles")
articles = sqlite_cursor.fetchall()

# 插入數據到 PostgreSQL
for article in articles:
    pg_cursor.execute('''
        INSERT INTO articles (id, title, url, comment, date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    ''', article)

# 提交更改並關閉連接
pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

print("數據遷移完成")
