import sqlite3
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import json
import random
from line_notify import send_line_notify

# 載入環境變數
load_dotenv()

# 設置 Gemini API 金鑰
api_key = os.getenv("GEMINI_API_KEY")


# 測試用變數，之後應移除或替換為環境變數
#api_key = "AIzaSyBIsMnfyjGmuW0cLAW2E3CuIrBD-oCjYW8"  # 測試用，之後應移除
if not api_key:
    raise ValueError("未找到 GEMINI_API_KEY 環境變數。請確保您的 .env 文件中包含此金鑰。")
genai.configure(api_key=api_key)

def connect_to_db():
    return sqlite3.connect('ptt_articles.db')

def get_recent_articles(cursor, limit=10):
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

def summarize_with_gemini(articles, max_attempts=10):
    model = genai.GenerativeModel('gemini-pro')
    prompt = "你扮演一個資深的ptt網路鄉民，對我等等提供給你的數篇文章中挑出最具有代表性的推文，做個摘要，重點是推文所以你的回覆也要包含以下的格式：\n標題：{{標題}}\n推文：{{推文內容}}\n(重複此結構以包含所有推文)，最後將所有推文做個總結大意並以滿分100分隨機為此鄉民打分數，以下是文章標題與推文：\n\n"
    # 添加安全設置
    safety_settings = {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE"
    }
    for attempt in range(max_attempts):
        selected_articles = articles[-10:]
        
        for article in selected_articles:
            if len(article) > 1:
                processed_comments = process_comments(article[1])
                prompt += f"標題: {article[0]}\n推文:\n{processed_comments}\n\n"
            else:
                prompt += f"標題: {article[0]}\n\n"
        
        try:
            #response = model.generate_content(prompt)
            response = model.generate_content(prompt, safety_settings=safety_settings)
            # 檢查安全評級
            if response.prompt_feedback:
                print(f"提示反饋: {response.prompt_feedback}")
            
            if hasattr(response, 'text'):
                summary = remove_markdown(response.text)
            elif hasattr(response, 'parts'):
                summary = remove_markdown(''.join(part.text for part in response.parts))
            else:
                summary = remove_markdown(str(response))
            
            if summary.strip():
                return summary
            else:
                print(f"第 {attempt + 1} 次嘗試: Gemini 回傳空值")
                print(f"回應對象: {response}")
                print(f"回應屬性: {dir(response)}")
        except Exception as e:
            print(f"第 {attempt + 1} 次嘗試發生錯誤：{e}")
            print(f"錯誤類型: {type(e)}")
            print(f"錯誤詳情: {str(e)}")
    
    return "無法生成有效的摘要。請稍後再試。"

def main():
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        articles = get_recent_articles(cursor, 10)  # 獲取最新的 10 篇文章
        if not articles:
            print("未從資料庫中檢索到任何文章。")
            return
        
        summary = summarize_with_gemini(articles)
        print("\n鄭宇豪的推文摘要和總結：")
        print(summary)
        
        # 使用 LINE Notify 發送摘要
        send_line_notify("\n鄭宇豪最近的推文摘要和總結：\n" + summary)
    except Exception as e:
        error_message = f"發生錯誤：{e}"
        print(error_message)
        send_line_notify(error_message)
    finally:
        conn.close()

if __name__ == "__main__":
    main()