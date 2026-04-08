# FROM python:3.11-slim

# WORKDIR /app

# # ตั้งค่าไม่ให้ apt-get ถามโต้ตอบ (ป้องกัน Build ค้างที่หน้าเลือก Timezone)
# ENV DEBIAN_FRONTEND=noninteractive

# # ติดตั้ง Curl และดาวน์โหลด Ollama Binary สำหรับรันบน Linux/AMD64 โดยตรง
# RUN apt-get update && \
#     apt-get install -y curl && \
#     curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama && \
#     chmod +x /usr/bin/ollama && \
#     rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY handler.py .

# # รันด้วย Python ปกติ
# CMD ["python", "-u", "handler.py"]


FROM python:3.11-slim

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system deps Ollama commonly needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash tini \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama binary
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama \
    && chmod +x /usr/local/bin/ollama

# Python deps (make sure runpod is included)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "import runpod; print('runpod import ok')"

COPY handler.py .

# Tini helps avoid zombie processes (ollama runs as a background server)
ENTRYPOINT ["/usr/bin/tini", "--", "python", "-u", "handler.py"]

# รับชื่อโมเดลผ่าน Container Start Command ได้ (ตามภาพตัวอย่าง)
CMD ["gemma4:26b-a4b-it-q8_0"]