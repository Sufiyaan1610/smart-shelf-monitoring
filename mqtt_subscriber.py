import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TOPIC = "shelf/alerts"

def save_alert(payload):
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            type TEXT,
            location TEXT,
            item TEXT,
            count INTEGER,
            status TEXT,
            resolved INTEGER DEFAULT 0,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO alerts (event_id, type, location, item, count, status, timestamp)
        VALUES (?,?,?,?,?,?,?)
    """, (
        payload["event_id"], payload["type"], payload["location"],
        payload["item"], payload["count"], payload["status"], payload["timestamp"]
    ))
    conn.commit()
    conn.close()
    print(f"Alert saved: {payload['location']} → {payload['status']}")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f" Received MQTT message: {payload}")
    save_alert(payload)

def on_connect(client, userdata, flags, rc):
    print(" Connected to MQTT broker!")
    client.subscribe(TOPIC, qos=1)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
print("Listening for shelf alerts...")
client.loop_forever()
