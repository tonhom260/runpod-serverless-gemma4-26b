import runpod
# import requests
# import subprocess
# import time
# import os

# ใช้ชื่อ Model และ Path จากที่คุณแจ้งมา
# OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1")
# OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", "11434"))
# BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

# MODEL_NAME = os.environ.get("MODEL_NAME", "gemma4:26b-a4b-it-q8_0")
# OLLAMA_MODELS_DIR = "/runpod-volume/workspace/models"
# OLLAMA_API = "http://127.0.0.1:11434/api"

# def start_ollama():
#     """Starts the Ollama server in the background and waits for it to be ready."""
#     env = os.environ.copy()
#     # กำหนดที่เก็บ Model เป็น Network Volume
#     env["OLLAMA_MODELS"] = OLLAMA_MODELS_DIR
    
#     print("[Ollama] Starting Ollama server...")
#     # รัน Ollama ใน background
#     p = subprocess.Popen(
#         ["ollama", "serve"],
#         env=env,
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL
#     )
#     print("[Ollama] PID:", p.pid)
#     # รอให้ Server รันสำเร็จ (Timeout 30 วินาที)
#     retries = 30
#     server_ready = False
#     for _ in range(retries):
#         try:
#             res = requests.get("http://127.0.0.1:11434/", timeout=2)
#             if res.status_code == 200:
#                 print("[Ollama] Server is up and running.")
#                 server_ready = True
#                 break
#         except requests.exceptions.ConnectionError:
#             pass
#         time.sleep(1)
        
#     if not server_ready:
#         raise RuntimeError("[Ollama] Failed to start server.")
        
#     # พรีโหลดโมเดลเข้า VRAM เพื่อลดเวลา Cold Start ครั้งแรก
#     print(f"[Ollama] Preloading model: {MODEL_NAME} ...")
#     try:
#         payload = {
#             "model": MODEL_NAME,
#             "keep_alive": -1  # เก็บโมเดลไว้ในหน่วยความจำตลอด
#         }
#         # Preload จะแค่ส่ง prompt เปล่าๆ ไปเพื่อโหลดเข้า memory
#         res = requests.post(f"{OLLAMA_API}/generate", json=payload, timeout=120)
#         if res.status_code == 200:
#             print("[Ollama] Model preloaded successfully.")
#         else:
#             print(f"[Ollama] Warning: Preload returned status {res.status_code}: {res.text}")
#     except Exception as e:
#         print(f"[Ollama] Warning: Failed to preload model: {e}")


import os, time, subprocess, requests, pathlib, sys

# รับค่า MODEL_NAME จาก Container Start Command (sys.argv) หรือ Environment Variable
if len(sys.argv) > 1:
    MODEL_NAME = sys.argv[1]
else:
    MODEL_NAME = os.environ.get("MODEL_NAME", "gemma4:26b-a4b-it-q8_0")

# ใช้ OLLAMA_MODELS โดยตรงให้สอดคล้องกับภาพหน้าจอ (ค่าเริ่มต้นอิงตาม Volume เดิมของคุณ)
OLLAMA_MODELS_DIR = os.environ.get("OLLAMA_MODELS", "/runpod-volume/workspace/models")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
OLLAMA_API = f"http://{OLLAMA_HOST}/api"

def start_ollama():
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = OLLAMA_MODELS_DIR
    env["OLLAMA_HOST"] = OLLAMA_HOST

    # Hard fail early if the volume path isn't there
    models_path = pathlib.Path(OLLAMA_MODELS_DIR)
    if not models_path.exists():
        raise RuntimeError(
            f"[Ollama] OLLAMA_MODELS_DIR does not exist: {OLLAMA_MODELS_DIR}. "
            f"Is your network volume mounted to /runpod-volume?"
        )

    print(f"[Ollama] Using models dir: {OLLAMA_MODELS_DIR}", flush=True)
    print("[Ollama] Starting Ollama server...", flush=True)

    # IMPORTANT: do NOT redirect logs to DEVNULL, or you'll never see the real error
    p = subprocess.Popen(
        ["/usr/local/bin/ollama", "serve"],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    print("[Ollama] PID:", p.pid, flush=True)

    # Wait for readiness (use tags endpoint)
    for i in range(60):
        # If ollama crashes immediately, fail fast with a clear message
        if p.poll() is not None:
            raise RuntimeError(f"[Ollama] ollama process exited early with code {p.returncode}")

        try:
            r = requests.get(f"{OLLAMA_API}/tags", timeout=2)
            if r.status_code == 200:
                print("[Ollama] Server is ready.", flush=True)
                break
        except requests.exceptions.RequestException:
            pass

        time.sleep(1)
    else:
        raise RuntimeError("[Ollama] Server did not become ready in time.")

    # Verify model is visible to Ollama from the volume before preload
    tags = requests.get(f"{OLLAMA_API}/tags", timeout=10).json()
    available = [m.get("name") for m in tags.get("models", [])]
    if MODEL_NAME not in available:
        raise RuntimeError(
            f"[Ollama] Model '{MODEL_NAME}' not found in Ollama tags. "
            f"Available: {available[:20]}... "
            f"Check that the model files are in {OLLAMA_MODELS_DIR} and are in Ollama's expected layout."
        )

    # Preload (optional; may be too heavy for serverless cold start)
    print(f"[Ollama] Preloading model: {MODEL_NAME} ...", flush=True)
    try:
        payload = {"model": MODEL_NAME, "prompt": "", "keep_alive": -1, "stream": False}
        res = requests.post(f"{OLLAMA_API}/generate", json=payload, timeout=600)
        print(f"[Ollama] Preload status: {res.status_code}", flush=True)
        if res.status_code != 200:
            print(f"[Ollama] Preload response: {res.text[:1000]}", flush=True)
    except Exception as e:
        print(f"[Ollama] Warning: preload failed: {e}", flush=True)


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

# 1. เริ่มระบบ Ollama เป็น Background Process
try:
    start_ollama()
except Exception as e:
    print("[Startup] Failed:", repr(e))
    raise
# 2. เริ่มระบบ RunPod Serverless รับ Request จากข้างนอก
runpod.serverless.start({"handler": handler})
