from datetime import datetime
import asyncio
import json
import signal
import grpc
import websockets
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sensors_pb2
import sensors_pb2_grpc
import paho.mqtt.client as mqtt

app = FastAPI()

class MQTTClient:
    def __init__(self, host="mosquitto", port=1883, keepalive=60):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.connect(host, port, keepalive)
        self.client.loop_start()
    
    def publish(self, topic, data):
        try:
            self.client.publish(topic, json.dumps(data))
            print(f"[MQTT] Published to {topic}: {data}")
        except Exception as e:
            print(f"[MQTT Error] {str(e)}")

mqtt_client = MQTTClient()

def validate_sensor_data(data):
    required_fields = {
        'patient_id': str,
        'sensor_id': str,
        'temperature': (int, float),
        'heart_rate': (int, float),
        'blood_pressure': dict
    }
    
    for field, field_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], field_type):
            raise TypeError(f"Invalid type for {field}. Expected {field_type}")

async def publish_sensor_data(sensor_info, location_info):
    try:
        validate_sensor_data(sensor_info)
        
        site_id = location_info.get("site")
        floor_id = location_info.get("floor") 
        room_id = location_info.get("room")
        sensor_id = sensor_info.get("sensor_id")

        if not all([site_id, floor_id, room_id, sensor_id]):
            raise ValueError("Incomplete location information")

        topic = f"data/health/{site_id}/{floor_id}/{room_id}/{sensor_id}/vitals"
        
        payload = {
            "patient_id": sensor_info["patient_id"],
            "sensor_id": sensor_id,
            "timestamp": sensor_info.get("timestamp") or datetime.utcnow().isoformat(),
            "vitals": {
                "temperature": sensor_info["temperature"],
                "heart_rate": sensor_info["heart_rate"],
                "blood_pressure": sensor_info["blood_pressure"]
            },
            "location": location_info
        }
        
        mqtt_client.publish(topic, payload)
        return True
        
    except Exception as e:
        print(f"[Publish Error] {str(e)}")
        raise

# REST API Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/health-data")
async def receive_health_data(data: dict):
    try:
        if "location" not in data:
            raise ValueError("Missing location data")
        await publish_sensor_data(data, data["location"])
        return {"status": "success", "message": "Data forwarded to MQTT"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

# WebSocket Implementation
async def health_handler(websocket):
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if "location" not in data:
                    await websocket.send(json.dumps({"error": "Missing location data"}))
                    continue
                    
                await publish_sensor_data(data, data["location"])
                await websocket.send(json.dumps({"status": "processed"}))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON format"}))
            except Exception as e:
                await websocket.send(json.dumps({"error": str(e)}))
                
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"[WebSocket Error] {str(e)}")

# gRPC Service Implementation
class HealthService(sensors_pb2_grpc.HealthServiceServicer):
    async def SendHealthData(self, request, context):
        try:
            data = {
                "patient_id": request.patient_id,
                "sensor_id": request.sensor_id,
                "temperature": request.temperature,
                "heart_rate": request.heart_rate,
                "blood_pressure": {
                    "systolic": request.blood_pressure.systolic,
                    "diastolic": request.blood_pressure.diastolic
                },
                "timestamp": request.timestamp or datetime.utcnow().isoformat()
            }
            
            location = {
                "site": request.location.site,
                "floor": request.location.floor,
                "room": request.location.room
            }
            
            await publish_sensor_data(data, location)
            return sensors_pb2.HealthResponse(success=True,message="Data processed successfully")
            
        except Exception as e:
            return sensors_pb2.HealthResponse(
                success=False,
                message=str(e)
            )

async def run_servers():
    # Configure shutdown event
    stop_event = asyncio.Event()
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    # Start servers
    servers = await asyncio.gather(
        start_grpc_server(),
        uvicorn.Server(config=uvicorn.Config(app, host="0.0.0.0", port=5000, log_level="info")).serve(),
        websockets.serve(health_handler, "0.0.0.0", 8765),
        return_exceptions=True
    )
    
    await stop_event.wait()
    print("Shutting down servers gracefully...")

async def start_grpc_server():
    server = grpc.aio.server()
    sensors_pb2_grpc.add_HealthServiceServicer_to_server(HealthService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("[gRPC] Server running on [::]:50051")
    await server.wait_for_termination()

if __name__ == "__main__":
    try:
        asyncio.run(run_servers())
    except KeyboardInterrupt:
        print("Servers stopped by user")
    except Exception as e:
        print(f"[Fatal Error] {str(e)}")

