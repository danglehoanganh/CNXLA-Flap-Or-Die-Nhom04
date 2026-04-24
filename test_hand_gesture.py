# test_hand_gesture.py
from hand_gesture import HandGestureDetector
import time

def main():
    detector = HandGestureDetector(show_camera=True)
    detector.start()
    print("Đưa tay lên/xuống trước camera để kiểm tra. Nhấn ESC để thoát.")
    try:
        while detector.running:
            gesture = detector.get_gesture()
            y_norm = detector.get_y_norm()
            print(f"Gesture: {gesture}, y_norm: {y_norm}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    detector.stop()

if __name__ == "__main__":
    main()
