import cv2
import os

video_path = "my_images/videos/IMG_0656.mp4"
output_folder = "my_images/photos/"
os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(video_path)
frame_count = 0
saved = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if frame_count % 10 == 0:
        cv2.imwrite(f"{output_folder}frame_{saved}.jpg", frame)
        saved += 1
    frame_count += 1

cap.release()
print(f"Saved {saved} frames!")