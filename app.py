from flask import Flask, render_template, request, redirect
from ultralytics import YOLO
import sqlite3
import os
import uuid
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import random

app = Flask(__name__)
model = YOLO("/Users/sufiyaanahmed/runs/detect/train5/weights/best.pt")
os.makedirs("static/uploads", exist_ok=True)

BROKER = "localhost"
PORT = 1883
TOPIC = "shelf/alerts"

def get_stock_level(count):
    if count == 0:
        return "out_of_stock", "Out of Stock"
    elif count <= 10:
        return "low", "Low"
    elif count <= 20:
        return "medium", "Medium"
    else:
        return "high", "High"

def get_stock():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT compartment, item, MAX(timestamp), status, MAX(count), image
        FROM stock GROUP BY compartment ORDER BY compartment
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_history():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, location, item, status, count, timestamp, resolved
        FROM alerts ORDER BY timestamp DESC LIMIT 20
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_chart_data():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT compartment, count, timestamp FROM stock
        ORDER BY timestamp ASC LIMIT 40
    """)
    rows = cursor.fetchall()
    conn.close()
    labels, left, right = [], [], []
    for row in rows:
        if row[0] == "Left Bottom":
            labels.append(row[2][11:19])
            left.append(row[1])
        elif row[0] == "Right Bottom":
            right.append(row[1])
    return labels, left, right

def get_all_detections():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT compartment, count, image, timestamp, status
        FROM stock WHERE image IS NOT NULL
        ORDER BY timestamp DESC LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_metrics():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM stock")
    total_scans = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(count) FROM stock")
    avg_count = round(cursor.fetchone()[0] or 0, 1)
    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE resolved=1")
    resolved = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM stock WHERE count <= 10 AND count > 0")
    low_stock_events = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM stock WHERE count = 0")
    out_of_stock_events = cursor.fetchone()[0]
    conn.close()
    return {
        "total_scans": total_scans,
        "avg_count": avg_count,
        "total_alerts": total_alerts,
        "resolved": resolved,
        "low_stock_events": low_stock_events,
        "out_of_stock_events": out_of_stock_events,
        "resolution_rate": round((resolved / total_alerts * 100) if total_alerts > 0 else 0, 1)
    }

def render_base():
    stock = get_stock()
    history = get_history()
    chart_labels, chart_left, chart_right = get_chart_data()
    total_limes = sum(row[4] for row in stock)
    low_stock_count = sum(1 for row in stock if row[4] <= 10)
    last_scan = stock[0][2] if stock else "N/A"
    return stock, history, chart_labels, chart_left, chart_right, total_limes, low_stock_count, last_scan

@app.route("/")
def index():
    stock, history, chart_labels, chart_left, chart_right, total_limes, low_stock_count, last_scan = render_base()
    return render_template("index.html",
        stock=stock, history=history,
        chart_labels=chart_labels, chart_left=chart_left, chart_right=chart_right,
        total_limes=total_limes, low_stock_count=low_stock_count, last_scan=last_scan,
        upload_result=None, upload_count=0, upload_level=""
    )

@app.route("/upload", methods=["GET", "POST"])
def upload():
    stock, history, chart_labels, chart_left, chart_right, total_limes, low_stock_count, last_scan = render_base()
    file = request.files.get("image")
    if not file:
        return redirect("/")
    filename = f"uploads/{uuid.uuid4().hex}.jpg"
    filepath = f"static/{filename}"
    file.save(filepath)
    results = model(filepath, verbose=False)
    count = len(results[0].boxes)
    level_class, level_label = get_stock_level(count)
    result_filename = f"uploads/result_{uuid.uuid4().hex}.jpg"
    results[0].save(filename=f"static/{result_filename}")
    mqtt_client = mqtt.Client()
    mqtt_client.connect(BROKER, PORT, 60)
    payload = {
        "event_id": str(uuid.uuid4()),
        "type": level_class,
        "location": "Manual Upload",
        "item": "lime",
        "count": count,
        "status": level_label,
        "timestamp": datetime.now().isoformat()
    }
    mqtt_client.publish(TOPIC, json.dumps(payload), qos=1)
    mqtt_client.disconnect()
    return render_template("index.html",
        stock=stock, history=history,
        chart_labels=chart_labels, chart_left=chart_left, chart_right=chart_right,
        total_limes=total_limes, low_stock_count=low_stock_count, last_scan=last_scan,
        upload_result=result_filename, upload_count=count, upload_level=level_label
    )

@app.route("/resolve/<int:alert_id>", methods=["POST"])
def resolve(alert_id):
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/gallery")
def gallery():
    detections = get_all_detections()
    return render_template("gallery.html", detections=detections)

@app.route("/weight")
def weight():
    compartments = [
        {"name": "Left Bottom", "current": random.randint(8, 15), "max": 20, "unit": "kg"},
        {"name": "Right Bottom", "current": random.randint(8, 15), "max": 20, "unit": "kg"},
    ]
    history = []
    for i in range(10):
        history.append({
            "time": f"0{i}:00",
            "left": random.randint(5, 20),
            "right": random.randint(5, 20)
        })
    return render_template("weight.html", compartments=compartments, history=history)

@app.route("/metrics")
def metrics():
    m = get_metrics()
    return render_template("metrics.html", metrics=m)

if __name__ == "__main__":
    app.run(debug=True, port=3000)
    