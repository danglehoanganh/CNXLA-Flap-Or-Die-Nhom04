import cv2


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không mở được camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không đọc được frame từ camera.")
            break

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()