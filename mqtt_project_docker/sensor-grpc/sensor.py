import grpc
import sensors_pb2
import sensors_pb2_grpc
import random
import time
from datetime import datetime

def sensor():
    while True:
        try:
            channel = grpc.insecure_channel('gateway:50051')
            stub = sensors_pb2_grpc.HealthServiceStub(channel)
            
            while True:  
                try:
                    response = stub.SendHealthData(
                        sensors_pb2.HealthData(
                            patient_id="001",
                            sensor_id="03",
                            timestamp=datetime.utcnow().isoformat(),
                            temperature=round(random.uniform(35.0, 39.5), 1),
                            heart_rate=random.randint(50, 120),
                            blood_pressure=sensors_pb2.BloodPressure(
                                systolic=random.randint(100, 160),
                                diastolic=random.randint(60, 100)
                            ),
                            location=sensors_pb2.Location(
                                site="south",    
                                floor="2",       
                                room="10"
                            )
                        ),
                        timeout=10
                    )
                    print(f"Data sent at {datetime.now().isoformat()}")
                    time.sleep(3)
                    
                except grpc.RpcError as e:
                    print(f"gRPC Error: {e.code()}. Reconnecting...")
                    channel.close()
                    break
                    
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            time.sleep(5)

if __name__ == '__main__':
    sensor()
