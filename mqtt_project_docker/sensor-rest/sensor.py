import requests
import random
import time
from datetime import datetime

GATEWAY_URL = "http://gateway:5000/api/health-data"

def sensor():
    while True:
        try:
            data = {
                "patient_id": "002",
                "sensor_id": "01",
                "timestamp": datetime.utcnow().isoformat(),
                "location": {
                    "site": "north",
                    "floor": "3",       
                    "room": "2"
                },
                "temperature": round(random.uniform(35.0, 39.5), 1),
                "heart_rate": random.randint(50, 120),
                "blood_pressure": {
                    "systolic": random.randint(100, 160),
                    "diastolic": random.randint(60, 100)
                }
            }
            
            response = requests.post(GATEWAY_URL, json=data)
            
        except requests.exceptions.RequestException as e:
            print(f"REST Connection Error: {e}")
        except Exception as e:
            print(f"REST Unexpected Error: {e}")
        
        time.sleep(3)

if __name__ == "__main__":
    sensor()
