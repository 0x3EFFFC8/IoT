import paho.mqtt.client as mqtt
from db_handler import save_to_db
import json
import time

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "data/health/+/+/+/+/vitals"
RECONNECT_DELAY = 5

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Message received: {payload}")
        save_to_db(payload)
    except Exception as e:
        print(f"Error processing message: {e}")

def setup_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    return client

def run_subscriber():
    client = setup_mqtt_client()
    
    while True:
        try:
            print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
            client.connect(MQTT_BROKER, MQTT_PORT)
            client.subscribe(MQTT_TOPIC)
            print("Connection successful. Listening for messages...")
            client.loop_forever()
            
        except ConnectionRefusedError:
            print(f"Could not connect to broker. Retrying in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying...")
            time.sleep(RECONNECT_DELAY)
        finally:
            client.disconnect()

if __name__ == "__main__":
    run_subscriber()
