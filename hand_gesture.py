# hand_gesture.py
# Module nhận diện cử chỉ tay (lên/xuống) dùng Mediapipe, chạy ở thread riêng

import cv2
import numpy as np
import os
import urllib.request
import threading
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker, HandLandmarkerResult
from mediapipe.tasks.python.vision.core.image import Image, ImageFormat

class HandGestureDetector:
    def __init__(self, show_camera=True):
        self.model_path = "hand_landmarker.task"
        if not os.path.exists(self.model_path):
            self.download_model(self.model_path)
        self.landmarker = HandLandmarker.create_from_model_path(self.model_path)
        self.cap = cv2.VideoCapture(0)
        self.gesture = "NONE"
        self.y_norm = None
        self.running = False
        self.thread = None
        self.show_camera = show_camera

    def download_model(self, model_path):
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        urllib.request.urlretrieve(url, model_path)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()

    def get_gesture(self):
        return self.gesture

    def get_y_norm(self):
        return self.y_norm

    def _run(self):
        prev_gesture = None
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.gesture = "DOWN"
                self.y_norm = None
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_frame)
            result: HandLandmarkerResult = self.landmarker.detect(mp_image)
            if result.hand_landmarks:
                tip = result.hand_landmarks[0][8]  # Index finger tip
                self.y_norm = tip.y
                # Tăng ngưỡng lên 0.7 cho dễ nhảy
                if self.y_norm < 0.7:
                    self.gesture = "UP"
                else:
                    self.gesture = "DOWN"
                # Debug: in ra console khi chuyển trạng thái
                if prev_gesture != self.gesture:
                    print(f"Gesture: {self.gesture}, y_norm: {self.y_norm:.2f}")
                prev_gesture = self.gesture
                # Vẽ landmarks lên frame
                h, w, _ = frame.shape
                for idx, landmark in enumerate(result.hand_landmarks[0]):
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"Gesture: {self.gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"y_norm: {self.y_norm:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            else:
                # Không phát hiện tay thì luôn là DOWN
                if self.gesture != "DOWN":
                    print("Gesture: DOWN (no hand detected)")
                self.gesture = "DOWN"
                self.y_norm = None
                cv2.putText(frame, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            # Hiển thị camera nếu bật
            if self.show_camera:
                cv2.imshow("Camera - Hand Tracking", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    self.running = False
                    break
        if self.show_camera:
            cv2.destroyWindow("Camera - Hand Tracking")
