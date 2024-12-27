import sqlite3
import os
from dotenv import load_dotenv
import re
import json
import random
from line_notify import send_line_notify
from openai import OpenAI

# 載入環境變數
load_dotenv()

# 設置 Gemini API 金鑰
#api_key = os.getenv("GEMINI_API_KEY")

# 設定 OpenAI 客戶端
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    #base_url=os.getenv('OPENAI_API_BASE')
    #api_key='sk-jilY7aYpXWx2ybH1E620406e3a634987876c04654e2bE813',
    base_url='https://free.v36.cm/v1'
)

def connect_to_db():
    return sqlite3.connect('ptt_articles.db')

def get_recent_articles(cursor, limit=5):
    cursor.execute("PRAGMA table_info(articles)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'title' not in columns:
        raise ValueError("資料表缺少必要的欄位 'title'")
    
    select_columns = 'title'
    if 'comment' in columns:
        select_columns += ', comment'
    
    # 假設 'id' 是自增的主鍵
    if 'id' in columns:
        query = f"""
        SELECT {select_columns}
        FROM articles
        WHERE id <= (SELECT MAX(id) FROM articles)
        ORDER BY id DESC
        LIMIT ?
        """
    else:
        # 如果沒有 'id'，我們就直接取最新的 10 筆
        query = f"SELECT {select_columns} FROM articles ORDER BY ROWID DESC LIMIT ?"
    
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def process_comments(comments):
    try:
        comments_list = json.loads(comments)
        if isinstance(comments_list, list):
            processed_comments = []
            for comment in comments_list:
                processed_comment = re.sub(r':\s*', ' ', str(comment))
                processed_comments.append(processed_comment)
            return '\n'.join(processed_comments)
        else:
            return re.sub(r':\s*', ' ', str(comments_list))
    except json.JSONDecodeError:
        return re.sub(r':\s*', ' ', str(comments))

def remove_markdown(text):
    # 移除 Markdown 語法
    text = re.sub(r'#+\s', '', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'`', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*>\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'```[\s\S]*?```', '', text)
    return text.strip()

def generate_summary(article_content):
    try:
        # 格式化文章內容
        formatted_content = ""
        for article in article_content:
            title = article[0]
            comment = article[1] if len(article) > 1 else ""
            formatted_content += f"標題：{title}\n"
            formatted_content += f"內容：{comment}\n\n"

        # 使用 OpenAI API 進行摘要
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
            "你是一位熟悉 PTT 的資深網友，專精於解析推文內容和評估網路社群互動。"
            "我將提供數篇文章的標題與推文，請按照以下格式分析並回覆：\n\n"
            "1. 從每篇文章的推文中挑選出最具代表性的內容（最多3至5則推文）。\n"
            "2. 以清晰的格式呈現，包含以下欄位：\n"
            "- 標題：{{文章標題}}\n"
            "- 推文：{{推文1內容}}\n"
            "- 推文：{{推文2內容}}\n"
            "(重複此結構，直到列出所有挑選的推文)\n"
            "3. 最後，總結所有推文的討論大意，並根據推文的品質（如幽默感、深度、回應主題的相關性）給出滿分100分的評分。\n"
            "4. 解釋評分的標準，說明為何會給出這樣的分數。\n\n"
            "注意：回覆中請避免使用 Markdown 語法，僅使用純文字格式。以下是需要分析的文章標題與推文："
        )},

                {"role": "user", "content": formatted_content}
            ],
            temperature=0.7,
            
        )
        
        # 獲取摘要結果
        summary = response.choices[0].message.content
        return summary
    
    except Exception as e:
        print(f"生成摘要時發生錯誤: {str(e)}")
        return None

def main():
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        articles = get_recent_articles(cursor, 5)
        if not articles:
            print("未從資料庫中檢索到任何文章。")
            return
        
        # 生成摘要
        summary = generate_summary(articles)
        if summary:
            print("\n鄭宇豪的推文摘要和總結：")
            print(summary)
            # 使用 LINE Notify 發送摘要
            send_line_notify("\n鄭宇豪最近的推文摘要和總結：\n" + summary)
        else:
            print("無法生成摘要")
    except Exception as e:
        error_message = f"發生錯誤：{e}"
        print(error_message)
        send_line_notify(error_message)
    finally:
        conn.close()

if __name__ == "__main__":
    main()