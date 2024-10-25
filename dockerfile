# 使用官方的 Python 3.9 映像作為基礎映像
FROM python:3.9-slim

# 安裝 curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製當前目錄下的所有檔案到容器的 /app 資料夾
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ptt_crawler.py scheduler.py gemini_ptt_summary.py line_notify.py ./

# 設置環境變數，但不給予默認值
ENV LINE_NOTIFY_TOKEN=""
ENV GEMINI_API_KEY=""
ENV PTT_BOARD=""
ENV PTT_USER=""
ENV SEC=""

# 設定環境變數
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 在 CMD 之前添加以下行
RUN echo "LINE_NOTIFY_TOKEN=$LINE_NOTIFY_TOKEN" && \
    echo "GEMINI_API_KEY=$GEMINI_API_KEY" && \
    echo "PTT_BOARD=$PTT_BOARD" && \
    echo "PTT_USER=$PTT_USER" && \
    echo "SEC=$SEC"

# 在 CMD 之前添加以下行
RUN curl -I https://www.pttweb.cc

# 在 CMD 之前添加以下行
RUN ls -l /app

# 執行 Python 程式
CMD ["python", "scheduler.py"]
