# Smart Shelf Monitoring System

A  automated shelf monitoring system that uses computer vision, IoT messaging, and a web dashboard to detect stock gaps and misplaced items in retail store shelves.

---

## Project Overview

This system was developed as part of a research thesis at Deakin University (SIT724 Research Project). It monitors a retail lime fridge shelf using a camera, detects stock levels using a custom-trained YOLOv8n object detection model, sends alerts via MQTT, and displays real-time stock status on a Flask web dashboard.

The system classifies shelf stock into four levels:

- High: Shelf is well stocked (21 or more items detected)
- Medium: Shelf has moderate stock (11 to 20 items detected)
- Low: Shelf needs restocking soon (1 to 10 items detected)
- Out of Stock: Shelf is empty (0 items detected)

---

## System Architecture

Camera Image → YOLOv8n Detection → MQTT Publisher → Mosquitto Broker → MQTT Subscriber → SQLite Database → Flask Dashboard

---

## Tech Stack

| Component | Technology |
|---|---|
| Object Detection | YOLOv8n (Ultralytics) |
| IoT Communication | MQTT (Mosquitto 2.1.2 + Paho Python) |
| Database | SQLite |
| Web Framework | Flask |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Dataset Management | Roboflow |
| Video Processing | OpenCV |

---

## Project Structure

```
lime-monitor/
├── app.py                  # Flask web application and main dashboard
├── detect.py               # YOLOv8n detection script and MQTT publisher
├── mqtt_subscriber.py      # MQTT subscriber and SQLite database writer
├── mqtt_publisher.py       # Standalone MQTT publisher
├── extract_frames.py       # OpenCV frame extraction from video footage
├── train.py                # Model training script
├── database.py             # Database initialisation
├── stock.db                # SQLite database file
├── dataset/                # Roboflow annotated training dataset
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   └── data.yaml
├── my_images/              # Warehouse shelf images and videos
│   ├── photos/
│   ├── sample/
│   └── videos/
├── static/                 # Flask static files
│   ├── detected/
│   └── uploads/
└── templates/              # Flask HTML templates
    ├── index.html
    ├── gallery.html
    ├── weight.html
    └── metrics.html
```

---

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Mosquitto MQTT Broker
- pip

### Step 1 - Clone the repository

```
git clone https://github.com/Sufiyaan1610/smart-shelf-monitoring.git
cd smart-shelf-monitoring
```

### Step 2 - Create and activate virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

### Step 3 - Install dependencies

```
pip install ultralytics flask paho-mqtt opencv-python
```

### Step 4 - Install Mosquitto broker

```
brew install mosquitto
```

### Step 5 - Set up the trained model

Download the trained YOLOv8n model weights (best.pt) and update the model path in app.py and detect.py to point to the correct location on your machine.

---

## Running the System

Three terminal windows need to run at the same time.

Terminal 1 - Start the MQTT Broker:
```
mosquitto
```

Terminal 2 - Start the MQTT Subscriber:
```
cd ~/Downloads/lime-monitor
source venv/bin/activate
python3 mqtt_subscriber.py
```

Terminal 3 - Start the Flask Dashboard:
```
cd ~/Downloads/lime-monitor
source venv/bin/activate
python3 app.py
```

Open a browser and go to: http://localhost:3000

To run detection on shelf images:
```
python3 detect.py
```

---

## Dashboard Pages

| Page | URL | Description |
|---|---|---|
| Dashboard | / | Main stock monitoring page with compartment status, alerts, and stock history chart |
| Gallery | /gallery | All detection frames with annotated lime bounding boxes |
| Weight Sensor | /weight | Simulated weight sensor readings per compartment |
| Metrics | /metrics | System statistics including total scans, alerts, and resolution rate |

---

## Model Performance

The YOLOv8n model was trained on 26 annotated warehouse images using transfer learning from COCO pretrained weights and evaluated against 6 real-world edge cases.

| Metric | Value |
|---|---|
| Precision | 89.3% |
| Recall | 86.8% |
| F1 Score | 88.0% |
| mAP50 | 92.4% |

---

## Edge Cases Tested

| ID | Edge Case | Outcome After Retraining |
|---|---|---|
| EC-01 | Different camera angles | Partially improved |
| EC-02 | Low lighting conditions | Marginal improvement |
| EC-03 | Damaged and yellowing limes | Improved detection |
| EC-04 | Empty compartment with packaging only | More consistent Out of Stock results |
| EC-05 | Overlapping and densely packed limes | Marginal improvement |
| EC-06 | Mixed items on shelf | Model now detects multiple classes |

---

## Research Details

Title: A Smart Shelf Monitoring System for Detecting Stock Gaps and Misplaced Items in Retail Stores

University: Deakin University

Unit: SIT724 Research Project

Supervisor: Dr Niroshinie Fernando
