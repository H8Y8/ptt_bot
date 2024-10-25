import schedule
import time
import subprocess
import os
from dotenv import load_dotenv
from line_notify import send_line_notify
import logging

load_dotenv()

# 測試用變數，之後應移除或替換為環境變數
PTT_BOARD = os.getenv('PTT_BOARD')
PTT_USER = os.getenv('PTT_USER')
SEC = int(os.getenv('SEC', '300'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_ptt_crawler():
    logger.info("執行 PTT 爬蟲")
    subprocess.run(["python", "ptt_crawler.py"])

def run_gemini_summary():
    subprocess.run(["python", "gemini_ptt_summary.py"])

def main():
    logger.info("啟動排程器")
    
    # 立即執行一次爬蟲程序
    logger.info("立即執行第一次爬蟲")
    run_ptt_crawler()
    
    # 定期執行爬蟲程序
    schedule.every(SEC).seconds.do(run_ptt_crawler)
    
    # 每天晚上 23:00 執行摘要
    schedule.every().day.at("00:00").do(run_gemini_summary)
    
    while True:
        logger.info("檢查待執行的任務")
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()