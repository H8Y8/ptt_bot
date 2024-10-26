from flask import Flask, render_template, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime
import logging
import time
from contextlib import contextmanager

app = Flask(__name__)

# 修改資料庫路徑和連接埠的獲取方式
db_path = os.environ.get('PTT_DB_PATH', '/app/data/ptt_articles.db')
port = int(os.environ.get('PORT', 5000))

logging.basicConfig(level=logging.DEBUG)

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30)  # 增加到30秒
        yield conn
    finally:
        if conn:
            conn.close()

def get_random_comment():
    start_time = time.time()
    try:
        logging.debug(f"嘗試連接數據庫：{db_path}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, comment, date FROM articles ORDER BY RANDOM() LIMIT 1")
            result = cursor.fetchone()
        
        if result:
            title, comment, date = result
            # 移除評論中的冒號
            comment = comment.replace(':', '')
            title=title.replace(' ', '')
            title=title.replace('　', '')
            # 轉換日期格式
            try:
                
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%m/%d")
            except ValueError:
                formatted_date = date  # 如果日期格式不正確，保留原始格式
            logging.debug(f"成功獲取數據：{title[:20]}...")
        else:
            title, comment, formatted_date = "", "", "N/A"
            logging.warning("沒有找到數據")
        
        end_time = time.time()
        logging.debug(f"查詢耗時：{end_time - start_time:.2f} 秒")
        return title, comment, formatted_date
    except sqlite3.Error as e:
        logging.error(f"SQLite錯誤: {e}")
        return "SQLite錯誤", str(e), "N/A"
    except Exception as e:
        logging.error(f"發生未知錯誤: {e}")
        return "未知錯誤", str(e), "N/A"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_random_comment')
def random_comment():
    logging.debug("開始處理 /get_random_comment 請求")
    title, comment, date = get_random_comment()
    logging.debug(f"獲取到的數據：標題={title[:20]}..., 日期={date}")
    return jsonify({"title": title, "comment": comment, "date": date})

# 添加這個路由來處理靜態文件
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

def test_db_connection():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 獲取資料表名稱
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                logging.info("成功連接到數據庫")
                for table in tables:
                    table_name = table[0]
                    logging.info(f"資料表: {table_name}")
                    
                    # 獲取每個資料表的欄位名稱
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_names = [column[1] for column in columns]
                    logging.info(f"欄位: {', '.join(column_names)}")
            else:
                logging.warning("數據庫中沒有資料表")
    except Exception as e:
        logging.error(f"數據庫連接測試失敗: {e}")

if __name__ == '__main__':
    test_db_connection()
    app.run(host='0.0.0.0', port=port, debug=True)