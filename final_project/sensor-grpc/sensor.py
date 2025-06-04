import grpc
import sensors_pb2
import sensors_pb2_grpc
import random
import time
from datetime import datetime

VEHICLE_ID = "car001"
SENSOR_ID = "fuel001"

def sensor():
    while True:
        try:
            channel = grpc.insecure_channel('gateway:50051')
            stub = sensors_pb2_grpc.FuelSensorServiceStub(channel)
            
            while True:  
                try:
                    fuel_level = round(random.uniform(0, 100), 2)
                    timestamp = datetime.utcnow().isoformat()
                    unit = "percent"
                    
                    response = stub.SendFuelData(
                        sensors_pb2.FuelSensorData(
                            sensor_id=SENSOR_ID,
                            vehicle_id=VEHICLE_ID,
                            timestamp=timestamp,
                            fuel_level=fuel_level,
                            unit=unit
                        ),
                        timeout=10
                    )

                    time.sleep(30)
                    
                except grpc.RpcError as e:
                    print(f"gRPC Error: {e.code()}. Reconnecting...")
                    channel.close()
                    break
                    
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            time.sleep(5)

if __name__ == '__main__':
    sensor()

