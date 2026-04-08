FROM python:3.11-slim

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# ตั้งค่าให้ Container มองเห็น GPU บน RunPod ได้เต็มประสิทธิภาพ (เหมือนใน Image ปกติ)
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64

# Install system deps Ollama commonly needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash tini tar zstd \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama binary & libraries from official ZST release
RUN curl -f -L https://ollama.com/download/ollama-linux-amd64.tar.zst | tar --zstd -x -C /usr

# Python deps (make sure runpod is included)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "import runpod; print('runpod import ok')"

COPY handler.py .

# Tini helps avoid zombie processes
ENTRYPOINT ["/usr/bin/tini", "-s", "--", "python", "-u", "handler.py"]

# รับชื่อโมเดลผ่าน Container Start Command ได้ (ตามภาพตัวอย่าง)
CMD ["gemma4:26b-a4b-it-q8_0"]