# hand_gesture_fist.py
# Nhận diện nắm bàn tay (fist) và mở bàn tay (open) bằng Mediapipe
import cv2
import numpy as np
import os
import urllib.request
import threading
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker, HandLandmarkerResult
from mediapipe.tasks.python.vision.core.image import Image, ImageFormat

class HandGestureFistDetector:
    def __init__(self, show_camera=True):
        self.model_path = "hand_landmarker.task"
        if not os.path.exists(self.model_path):
            self.download_model(self.model_path)
        self.landmarker = HandLandmarker.create_from_model_path(self.model_path)
        self.cap = cv2.VideoCapture(0)
        self.gesture = "OPEN"
        self.running = False
        self.thread = None
        self.show_camera = show_camera
        self.fist_threshold = 0.22  # Tăng ngưỡng để dễ nhận diện cả FIST và OPEN hơn
        self.last_avg_dist = 0.0

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

    def _run(self):
        prev_gesture = None
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.gesture = "OPEN"
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_frame)
            result: HandLandmarkerResult = self.landmarker.detect(mp_image)
            if result.hand_landmarks:
                # Lấy các điểm đầu ngón tay và cổ tay
                lm = result.hand_landmarks[0]
                wrist = lm[0]
                tip_ids = [4, 8, 12, 16, 20]
                # Tính khoảng cách trung bình từ đầu ngón tay đến cổ tay
                dists = [np.sqrt((lm[i].x - wrist.x) ** 2 + (lm[i].y - wrist.y) ** 2) for i in tip_ids]
                avg_dist = np.mean(dists)
                # Nếu các đầu ngón tay gần cổ tay (nắm tay), ngược lại là mở tay
                self.last_avg_dist = avg_dist
                if avg_dist < self.fist_threshold:
                    self.gesture = "FIST"
                else:
                    self.gesture = "OPEN"
                percent = min(100, int(100 * avg_dist / self.fist_threshold))
                if prev_gesture != self.gesture:
                    print(f"[Hand Fist Detection] Gesture: {self.gesture}, avg_dist: {avg_dist:.3f}, threshold: {self.fist_threshold}, percent: {percent}%")
                prev_gesture = self.gesture
                # Vẽ landmarks và trạng thái lên frame
                h, w, _ = frame.shape
                for idx, landmark in enumerate(lm):
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"Gesture: {self.gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"avg_dist: {avg_dist:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                cv2.putText(frame, f"Detect: {percent}%", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
            else:
                self.gesture = "OPEN"
                self.last_avg_dist = 0.0
                cv2.putText(frame, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.putText(frame, f"Detect: 0%", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
                def get_detect_percent(self):
                    if self.fist_threshold == 0:
                        return 0
                    return min(100, int(100 * self.last_avg_dist / self.fist_threshold))
            if self.show_camera:
                cv2.imshow("Camera - Fist Tracking", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    self.running = False
                    break
        if self.show_camera:
            cv2.destroyWindow("Camera - Fist Tracking")
