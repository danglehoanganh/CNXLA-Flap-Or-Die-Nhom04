import cv2
import numpy as np
import os
import urllib.request
import threading
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker, HandLandmarkerResult
from mediapipe.tasks.python.vision.core.image import Image, ImageFormat

class HandTracker:
    def __init__(self, show_camera=False):
        self.model_path = "hand_landmarker.task"
        if not os.path.exists(self.model_path):
            self.download_model()
        self.landmarker = HandLandmarker.create_from_model_path(self.model_path)
        # Không mở camera ở đây nữa
        self.gesture = "OPEN"
        self.prev_gesture = "OPEN"
        self.running = False
        self.thread = None
        self.show_camera = show_camera
        self.fist_threshold = 0.22
        self.last_avg_dist = 0.0

    def download_model(self):
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        print("Downloading hand_landmarker.task...")
        urllib.request.urlretrieve(url, self.model_path)
        print("Model downloaded.")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        # Không cần release camera nữa

    def get_gesture(self):
        return self.gesture

    def is_fist(self, frame=None):
        return self.gesture == "FIST"

    def process(self, frame):
        # Nhận frame từ bên ngoài, không tự đọc camera nữa
        if frame is None:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_frame)
        result: HandLandmarkerResult = self.landmarker.detect(mp_image)

        current_frame = frame.copy()

        if result.hand_landmarks:
            lm = result.hand_landmarks[0]
            wrist = lm[0]
            tip_ids = [4, 8, 12, 16, 20]
            dists = [np.sqrt((lm[i].x - wrist.x)**2 + (lm[i].y - wrist.y)**2) for i in tip_ids]
            avg_dist = np.mean(dists)
            self.last_avg_dist = avg_dist

            if avg_dist < self.fist_threshold:
                self.gesture = "FIST"
            else:
                self.gesture = "OPEN"

            # Draw landmarks on current_frame
            h, w, _ = current_frame.shape
            for idx, landmark in enumerate(lm):
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(current_frame, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(current_frame, f"Gesture: {self.gesture}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(current_frame, f"Dist: {avg_dist:.3f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            self.gesture = "OPEN"
            self.last_avg_dist = 0.0
            cv2.putText(current_frame, "No hand", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if self.show_camera:
            cv2.imshow("HandTracker", current_frame)
            cv2.waitKey(1)

        return current_frame

    def draw_landmarks(self, frame):
        # For compatibility, but process already draws
        return self.process(frame)

    def _run(self):
        # Background thread not strictly needed since process handles single frame
        # But kept for potential future use
        while self.running:
            if not self.show_camera:
                cv2.waitKey(1)
