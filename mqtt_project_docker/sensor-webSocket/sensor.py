import asyncio
import websockets
import json
import random
from datetime import datetime

async def sensor():
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            async with websockets.connect('ws://gateway:8765',ping_interval=20,ping_timeout=20) as websocket:
                print("[Sensor] Connected to Gateway")
                
                async def send_data():
                    while True:
                        data = {
                            "patient_id": "003",
                            "sensor_id": "02",
                            "timestamp": datetime.utcnow().isoformat(),
                            "temperature": round(random.uniform(35.0, 39.5), 1),
                            "heart_rate": random.randint(50, 120),
                            "blood_pressure": {
                                "systolic": random.randint(100, 160),
                                "diastolic": random.randint(60, 100)
                            },
                            "location": {
                                "site": "south",
                                "floor": "1",      
                                "room": "1"
                            }
                        }
                        await websocket.send(json.dumps(data))
                        await asyncio.sleep(3)
                        print("[Sensor] Data sent")
                
                await send_data()
                
        except Exception as e:
            print(f"[Sensor] Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise

if __name__ == "__main__":
    asyncio.run(sensor())

