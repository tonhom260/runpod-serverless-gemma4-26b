FROM ollama/ollama:latest

WORKDIR /app

# ollama/ollama is an Ubuntu base but lacks Python. We need to install python3 and pip.
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .
# Use pip3 to match python3
RUN pip3 install --no-cache-dir -r requirements.txt

COPY handler.py .

# Use python3 explicit binary
CMD ["python3", "-u", "handler.py"]