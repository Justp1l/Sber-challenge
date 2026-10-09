import cv2 
import ultralytics
from pathlib import Path

model = ultralytics.YOLO("yolo11x.pt")

video_path = Path(".\\rendered_video.mp4")
video = cv2.VideoCapture(video_path)
detected_obj = set()

while video.isOpened():
    success, frame = video.read()
    if not success:
        break
    
    results = model.track(frame, persist=True, stream=True)
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls.item())
                class_name = model.names[cls_id]
                detected_obj.add(class_name)
                
        annotated_frame = result.plot()
        cv2.imshow("YOLO detection", annotated_frame)
       
    # q - exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()

print(detected_obj)