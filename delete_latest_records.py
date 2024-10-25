import sqlite3
import os
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 資料庫路徑
db_path = os.path.join(os.getcwd(), 'ptt_articles.db')

def delete_latest_records():
    try:
        # 連接到資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 獲取最新的10筆資料的ID
        cursor.execute("SELECT id FROM articles ORDER BY id DESC LIMIT 10")
        latest_ids = [row[0] for row in cursor.fetchall()]

        if not latest_ids:
            logger.info("資料庫中沒有資料可以刪除。")
            return

        # 刪除這些資料
        placeholders = ','.join(['?' for _ in latest_ids])
        cursor.execute(f"DELETE FROM articles WHERE id IN ({placeholders})", latest_ids)

        # 提交更改
        conn.commit()

        logger.info(f"已刪除最新的 {len(latest_ids)} 筆資料。")

        # 顯示剩餘的資料數量
        cursor.execute("SELECT COUNT(*) FROM articles")
        remaining_count = cursor.fetchone()[0]
        logger.info(f"資料庫中剩餘 {remaining_count} 筆資料。")

    except sqlite3.Error as e:
        logger.error(f"資料庫錯誤: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    delete_latest_records()