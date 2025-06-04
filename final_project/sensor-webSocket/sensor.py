import asyncio
import websockets
import json
import random
from datetime import datetime

VEHICLE_ID = "car001"
SENSOR_ID = "airbag001"

async def airbag_sensor():
    while True:
        try:
            async with websockets.connect('ws://gateway:8765') as websocket:
                while True:
                    activated = random.random() < 0.01
                    latitude = round(random.uniform(-90, 90), 6) 
                    longitude = round(random.uniform(-180, 180), 6)

                    data = {
                        "sensor_id": SENSOR_ID,
                        "vehicle_id": VEHICLE_ID,
                        "activated": activated,
                        "location": {
                            "latitude": latitude,
                            "longitude": longitude
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    await websocket.send(json.dumps(data))
                    response = await websocket.recv()
                    await asyncio.sleep(1 if activated else 5)
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(airbag_sensor())
