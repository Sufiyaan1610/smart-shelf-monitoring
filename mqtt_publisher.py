import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TOPIC = "shelf/alerts"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

def send_alert(compartment, item, status, count):
    payload = {
        "event_id": str(uuid.uuid4()),
        "type": "stock_gap" if status == "out_of_stock" else "low_stock" if count < 15 else "in_stock",
        "location": compartment,
        "item": item,
        "count": count,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    client.publish(TOPIC, json.dumps(payload), qos=1)
    print(f" MQTT Alert sent: {compartment} → {status} ({count} limes)")
    return payload

client.disconnect()
