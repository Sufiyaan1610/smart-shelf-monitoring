from ultralytics import YOLO
import sqlite3
import os
import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime

model = YOLO("/Users/sufiyaanahmed/runs/detect/train5/weights/best.pt")
os.makedirs("static/detected", exist_ok=True)

BROKER = "localhost"
PORT = 1883
TOPIC = "shelf/alerts"

mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT, 60)

def send_mqtt_alert(compartment, item, status, count):
    payload = {
        "event_id": str(uuid.uuid4()),
        "type": "out_of_stock" if count == 0 else "low_stock" if count <= 10 else "medium_stock" if count <= 20 else "in_stock",
        "location": compartment,
        "item": item,
        "count": count,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    mqtt_client.publish(TOPIC, json.dumps(payload), qos=1)
    print(f"MQTT sent: {compartment} → {status} ({count} limes)")

def log_event(compartment, item, status, count, image_file):
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO stock (compartment, item, status, count, image) VALUES (?,?,?,?,?)",
        (compartment, item, status, count, image_file)
    )
    conn.commit()
    conn.close()

photos_folder = "/Users/sufiyaanahmed/Downloads/edge_case_dataset/train/images/"
images = sorted(os.listdir(photos_folder))

for i, image_file in enumerate(images):
    if image_file.endswith(".jpg") or image_file.endswith(".jpeg"):
        path = os.path.join(photos_folder, image_file)
        results = model(path, verbose=False, show=False, conf=0.5)
        count = len(results[0].boxes)

        if count == 0:
            status = "out_of_stock"
        elif count <= 10:
            status = "low"
        elif count <= 20:
            status = "medium"
        else:
            status = "high"

        compartment = "Left Bottom" if i % 2 == 0 else "Right Bottom"
        save_path = f"static/detected/{compartment.replace(' ', '_')}_{image_file}"
        results[0].save(filename=save_path)

        log_event(compartment, "lime", status, count,
                  f"detected/{compartment.replace(' ', '_')}_{image_file}")
        send_mqtt_alert(compartment, "lime", status, count)
        print(f"Frame {image_file}: {count} limes → {compartment} → {status}")

mqtt_client.disconnect()
print("Done!")