FROM python:3.11-slim

WORKDIR /app

# ตั้งค่าไม่ให้ apt-get ถามโต้ตอบ (ป้องกัน Build ค้างที่หน้าเลือก Timezone)
ENV DEBIAN_FRONTEND=noninteractive

# ติดตั้ง Curl และดาวน์โหลด Ollama Binary สำหรับรันบน Linux/AMD64 โดยตรง
RUN apt-get update && \
    apt-get install -y curl && \
    curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama && \
    chmod +x /usr/bin/ollama && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py .

# รันด้วย Python ปกติ
CMD ["python", "-u", "handler.py"]