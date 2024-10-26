import os
from dotenv import load_dotenv

load_dotenv()

LINE_NOTIFY_TOKEN = os.getenv('LINE_NOTIFY_TOKEN')

# 測試用變數，之後應移除或替換為環境變數
#LINE_NOTIFY_TOKEN = "8XV2F5mqv9Bzlm0M6jVrKXwsaKaP5SvOWI3qXRxSICQ"  # 測試用，之後應移除

def send_line_notify(message):
    headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
    data = {'message': message}
    requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data)
