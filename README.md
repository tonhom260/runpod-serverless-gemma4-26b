# runpod-serverless-gemma4-26b
เวลาเราต้องการใช้ Serverless Endpoint สำหรับ Model ที่โหลดผ่าน Ollama และดึง Model ที่ Caching ไว้จาก Network Volume แบบไม่ต้องโหลดใหม่ทุกครั้ง

## วิธีตั้งค่าบน RunPod:
1. **Container Image**: แนะนำใช้ `pooyaharatian/runpod-ollama:0.0.8` (สำเร็จรูปและเสถียร)
2. **Container Start Command**: พิมพ์ชื่อโมเดล เช่น `gemma4:26b-a4b-it-q8_0`
3. **Environment Variables**:
   * `OLLAMA_MODELS` -> `/runpod-volume/workspace/models` (สำคัญมาก! ต้องขึ้นต้นด้วย `/runpod-volume` เนื่องจากระบบ Serverless ของ RunPod จะเมาท์ Volume มาไว้ที่นี่)
