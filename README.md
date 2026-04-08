# runpod-serverless-gemma4-26b
เวลาเราต้องการใช้ Serverless Endpoint สำหรับ Model ที่โหลดผ่าน Ollama และดึง Model ที่ Caching ไว้จาก Network Volume แบบไม่ต้องโหลดใหม่ทุกครั้ง

## วิธีตั้งค่าบน RunPod:
1. **Container Image**: แนะนำใช้ `pooyaharatian/runpod-ollama:0.0.8` (สำเร็จรูปและเสถียร)
2. **Container Start Command**: พิมพ์ชื่อโมเดล เช่น `gemma4:26b-a4b-it-q8_0`
3. **Environment Variables**:
   * `OLLAMA_MODELS` -> `/runpod-volume/workspace/models` (สำคัญมาก! ต้องขึ้นต้นด้วย `/runpod-volume` เนื่องจากระบบ Serverless ของ RunPod จะเมาท์ Volume มาไว้ที่นี่)
   หมายเหตุ แทน /workspace ด้วย /runpod-volume => /runpod-volume/models/...
   
OLLAMA_MODELS
/runpod-volume/models



log



[WARN  tini (19)] Tini is not running as PID 1 and isn't registered as a child subreaper.
Zombie processes will not be re-parented to Tini, so zombie reaping won't work.
To fix the problem, use the -s option or set the environment variable TINI_SUBREAPER to register Tini as a child subreaper, or run Tini as PID 1.
[Debug] pwd=/app
[Debug] exists(/runpod-volume)=True
[Debug] listdir(/runpod-volume)=['Modelfile', '.cache', 'huggingface-cache', 'models', 'logs', 'ollama', 'openwebui', 'hf_home', '.huggingface', 'id_ed25519.pub', 'id_ed25519']
[Debug] exists(/runpod-volume/models)=True
[Debug] listdir(/runpod-volume/models)=['manifests', 'blobs']
[Debug] exists(/runpod-volume/workspace)=False
[Debug] exists(/runpod-volume/workspace/models)=False
[Debug] pwd=/app
[Debug] exists(/runpod-volume)=True
[Debug] listdir(/runpod-volume)=['Modelfile', '.cache', 'huggingface-cache', 'models', 'logs', 'ollama', 'openwebui', 'hf_home', '.huggingface', 'id_ed25519.pub', 'id_ed25519']
[Debug] exists(/runpod-volume/models)=True
[Debug] listdir(/runpod-volume/models)=['manifests', 'blobs']
[Debug] exists(/runpod-volume/workspace)=False
[Debug] exists(/runpod-volume/workspace/models)=False
[Ollama] Using models dir: /runpod-volume/models
[Ollama] Starting Ollama server...
[Startup] Failed: OSError(8, 'Exec format error')
Traceback (most recent call last):
  File "/app/handler.py", line 158, in <module>
    start_ollama()
  File "/app/handler.py", line 32, in start_ollama
    p = subprocess.Popen(
        ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/usr/local/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
OSError: [Errno 8] Exec format error: '/usr/local/bin/ollama'
[WARN  tini (18)] Tini is not running as PID 1 and isn't registered as a child subreaper.
Zombie processes will not be re-parented to Tini, so zombie reaping won't work.
To fix the problem, use the -s option or set the environment variable TINI_SUBREAPER to register Tini as a child subreaper, or run Tini as PID 1.
