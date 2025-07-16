import cv2
import time

# Camera 1 - iPhone
cap = cv2.VideoCapture(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
  ret, frame = cap.read()
  if not ret:
    break

  start = time.time()

  # Dummy detection (replace with actual model inference)
  cv2.putText(frame, "Running detection...", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

  # Show FPS
  end = time.time()
  fps = 1 / (end - start)
  cv2.putText(frame, f"FPS: {fps:.2f}", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

  # Display
  cv2.imshow("iPhone Feed with ML", frame)
  if cv2.waitKey(1) == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()
