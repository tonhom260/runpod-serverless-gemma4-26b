FROM python:3.11-slim

WORKDIR /app

# ตั้งค่าไม่ให้ apt-get ถามโต้ตอบ (ป้องกัน Build ค้างที่หน้าเลือก Timezone)
ENV DEBIAN_FRONTEND=noninteractive

# ติดตั้ง Curl และติดตั้งโปรแกรม Ollama ตัวล่าสุด
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py .

# รันด้วย Python ปกติ
CMD ["python", "-u", "handler.py"]