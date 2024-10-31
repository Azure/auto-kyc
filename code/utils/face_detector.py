import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt

class FaceDetector:
    def __init__(self, model_path='yolov8n.pt'):
        # Load the YOLOv8 model
        self.model = YOLO(model_path)  # You can also use 'yolov8n.pt' for a nano model

    def detect_faces(self, image_path, confidence_threshold=0.01):
        # Read the image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for visualization

        # Run inference
        results = self.model(image_rgb,  conf=confidence_threshold)
        detected_faces = [res for res in results[0].boxes.data.tolist() if res[5] == 0]  # Assuming class_id 0 is for 'person'
        print(detected_faces)

        # Draw bounding boxes
        if len(detected_faces) > 0:
            x1, y1, x2, y2, confidence, class_id = detected_faces[0]
            if class_id == 0:  # Assuming class_id 0 is for 'person'
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 3)

        # Display the results
        plt.axis('off')
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # Convert back to RGB for displaying
        plt.show()
