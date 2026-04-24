# camera_gesture_test.py
import cv2
import numpy as np
import os
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker, HandLandmarkerResult
from mediapipe.tasks.python.vision.core.image import Image, ImageFormat

def download_model(model_path):
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    print("Downloading hand_landmarker.task...")
    import urllib.request
    urllib.request.urlretrieve(url, model_path)
    print("Model downloaded.")

def main():
    model_path = "hand_landmarker.task"
    if not os.path.exists(model_path):
        download_model(model_path)
    landmarker = HandLandmarker.create_from_model_path(model_path)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    print("Đưa tay vào camera để kiểm tra nhận diện. Nhấn ESC để thoát.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không nhận được hình ảnh từ camera!")
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_frame)
        result: HandLandmarkerResult = landmarker.detect(mp_image)
        h, w, _ = frame.shape
        detected = False
        confidence = 0.0
        gesture = "UNKNOWN"
        if result.hand_landmarks and result.hand_landmarks[0]:
            lm = result.hand_landmarks[0]
            # Tính confidence dựa trên số lượng landmark và bounding box
            if result.handedness and result.handedness[0]:
                confidence = result.handedness[0][0].score
            else:
                confidence = 1.0  # fallback nếu không có handedness
            # Nhận diện FIST/OPEN dựa vào khoảng cách trung bình từ cổ tay đến đầu ngón
            wrist = lm[0]
            tip_ids = [4, 8, 12, 16, 20]
            dists = [np.sqrt((lm[i].x - wrist.x)**2 + (lm[i].y - wrist.y)**2) for i in tip_ids]
            avg_dist = np.mean(dists)
            fist_threshold = 0.22
            if avg_dist < fist_threshold:
                gesture = "FIST"
            else:
                gesture = "OPEN"
            for idx, landmark in enumerate(lm):
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"{gesture} ({confidence*100:.1f}%)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Dist: {avg_dist:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            detected = True
        else:
            cv2.putText(frame, "No hand", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        # Tối ưu: làm mượt hiển thị bằng GaussianBlur nhẹ
        frame = cv2.GaussianBlur(frame, (3, 3), 0)
        cv2.imshow("Camera Gesture Test", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
