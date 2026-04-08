import runpod
import requests
import subprocess
import time
import os

# ใช้ชื่อ Model และ Path จากที่คุณแจ้งมา
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma4:26b-a4b-it-q8_0")
OLLAMA_MODELS_DIR = "/workspace/models"
OLLAMA_API = "http://127.0.0.1:11434/api"

def start_ollama():
    """Starts the Ollama server in the background and waits for it to be ready."""
    env = os.environ.copy()
    # กำหนดที่เก็บ Model เป็น Network Volume
    env["OLLAMA_MODELS"] = OLLAMA_MODELS_DIR
    
    print("[Ollama] Starting Ollama server...")
    # รัน Ollama ใน background
    subprocess.Popen(
        ["ollama", "serve"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # รอให้ Server รันสำเร็จ (Timeout 30 วินาที)
    retries = 30
    server_ready = False
    for _ in range(retries):
        try:
            res = requests.get("http://127.0.0.1:11434/", timeout=2)
            if res.status_code == 200:
                print("[Ollama] Server is up and running.")
                server_ready = True
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
        
    if not server_ready:
        raise RuntimeError("[Ollama] Failed to start server.")
        
    # พรีโหลดโมเดลเข้า VRAM เพื่อลดเวลา Cold Start ครั้งแรก
    print(f"[Ollama] Preloading model: {MODEL_NAME} ...")
    try:
        payload = {
            "model": MODEL_NAME,
            "keep_alive": -1  # เก็บโมเดลไว้ในหน่วยความจำตลอด
        }
        # Preload จะแค่ส่ง prompt เปล่าๆ ไปเพื่อโหลดเข้า memory
        res = requests.post(f"{OLLAMA_API}/generate", json=payload, timeout=120)
        if res.status_code == 200:
            print("[Ollama] Model preloaded successfully.")
        else:
            print(f"[Ollama] Warning: Preload returned status {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[Ollama] Warning: Failed to preload model: {e}")

def handler(job):
    """
    Handler function processes incoming requests to Serverless endpoint.
    Sends inference requests to the local Ollama server.
    """
    job_input = job.get("input", {})
    prompt = job_input.get("prompt", "")
    
    is_chat = "messages" in job_input
    
    # จัดเตรียม Options ตามที่ส่งมารับ (เช่น max_tokens, temperature)
    options = {}
    if "temperature" in job_input:
        options["temperature"] = float(job_input["temperature"])
    if "max_tokens" in job_input:
        options["num_predict"] = int(job_input["max_tokens"])
    # เพิ่ม options อื่นๆ ของ Ollama ได้ที่นี่
        
    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "keep_alive": -1 # เก็บค้างในหน่วยความจำหลังจากรันเสร็จ
    }
    
    if options:
        payload["options"] = options

    try:
        if is_chat:
            # ใช้ Chat API หากส่ง parameter 'messages' มาใน input
            payload["messages"] = job_input["messages"]
            response = requests.post(f"{OLLAMA_API}/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "status": "success",
                "output": result.get("message", {}).get("content", "")
            }
        else:
            # ใช้ Generate API มาตรฐาน หากส่ง parameter 'prompt' มา
            payload["prompt"] = prompt
            response = requests.post(f"{OLLAMA_API}/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "status": "success",
                "output": result.get("response", "")
            }
            
    except requests.exceptions.RequestException as e:
        print(f"[Handler] Request Error: {e}")
        return {
            "status": "error",
            "error": f"Failed to communicate with Ollama: {str(e)}"
        }
    except Exception as e:
        print(f"[Handler] Error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    # 1. เริ่มระบบ Ollama เป็น Background Process
    start_ollama()
    # 2. เริ่มระบบ RunPod Serverless รับ Request จากข้างนอก
    runpod.serverless.start({"handler": handler})