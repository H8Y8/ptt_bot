import sqlite3
import os
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 資料庫路徑
db_path = os.path.join(os.getcwd(), 'ptt_articles.db')

def check_database():
    try:
        # 連接到資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 獲取資料表的欄位名稱
        cursor.execute("PRAGMA table_info(articles)")
        columns = [column[1] for column in cursor.fetchall()]

        # 獲取最後 20 筆資料
        cursor.execute(f"SELECT * FROM articles ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()

        # 輸出欄位名稱
        print(" | ".join(columns))
        print("-" * (len(" | ".join(columns))))

        # 輸出資料
        for row in rows:
            print(" | ".join(str(item) for item in row))

        # 獲取總記錄數
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_records = cursor.fetchone()[0]
        logger.info(f"資料庫中共有 {total_records} 筆記錄")

    except sqlite3.Error as e:
        logger.error(f"資料庫錯誤: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database()