import requests
import random
import time
from datetime import datetime

GATEWAY_URL = "http://gateway:5000/api/vehicle/battery"
VEHICLE_ID = "car001"
SENSOR_ID = "battery001"

def battery_sensor():
    while True:
        try:
            voltage = round(random.uniform(11.5, 14.5), 2)
            charge_level = random.randint(0, 100)
            temperature = round(random.uniform(15, 45), 1)
            
            data = {
                "sensor_id": SENSOR_ID,
                "vehicle_id": VEHICLE_ID,
                "voltage": voltage,
                "charge_level": charge_level,
                "temperature": temperature,
                "status": "Good" if voltage > 12.2 and temperature < 40 else "Warning",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(GATEWAY_URL, json=data)
            if response.status_code != 200:
                print(f"Error sending data: {response.text}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        time.sleep(30)

if __name__ == '__main__':
    battery_sensor()
