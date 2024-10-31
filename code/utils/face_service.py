import cv2
import matplotlib.pyplot as plt
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import (
    FaceDetectionModel,
    FaceRecognitionModel,
    FaceAttributeTypeDetection03,
    FaceAttributeTypeRecognition04,
    QualityForRecognition,
)
import uuid


from utils.storage_helpers import *
from env_vars import *

storage_helper = BlobStorageHelper()


class FaceRecognitionService:
    def __init__(self, endpoint = FACE_API_ENDPOINT, key = FACE_API_KEY, face_id_time_to_live=120, buffer=10):
        self.buffer = buffer
        self.work_dir = 'temp_imgs'
        os.makedirs(self.work_dir, exist_ok=True)
        self.face_client = FaceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        self.face_id_time_to_live = face_id_time_to_live

    def detect_faces(self, sample_file_path, display_image=False, print_results=False):
        """Detect faces in an image and optionally display results."""
        with open(sample_file_path, "rb") as fd:
            file_content = fd.read()

        result = self.face_client.detect(
            file_content,
            detection_model=FaceDetectionModel.DETECTION03,
            recognition_model=FaceRecognitionModel.RECOGNITION04,
            return_face_id=True,
            return_face_attributes=[
                FaceAttributeTypeDetection03.HEAD_POSE,
                FaceAttributeTypeDetection03.MASK,
                FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
            ],
            return_face_landmarks=True,
            return_recognition_model=True,
            face_id_time_to_live=self.face_id_time_to_live,
            logging_enable=False
        )

        face_ids = [face.face_id for face in result]

        if print_results: print(f"Detected faces from the file: {sample_file_path}")
        rectangled_images = []

        for idx, face in enumerate(result):
            if print_results: 
                print(f"----- Detection result: #{idx + 1} -----")
                print(f"Face: {face.as_dict()}")

            output_path = self._draw_face_rectangle(sample_file_path, face, display_image=display_image)
            blob_output_path = storage_helper.upload_document(output_path) 
            rectangled_images.append(blob_output_path)
        
        return {
            "face_ids": face_ids, 
            "results": result,
            "rectangled_images": rectangled_images
        }

    def verify_faces(self, face_id1, face_id2):
        """Verify if two faces are from the same person."""
        verify_result = self.face_client.verify_face_to_face(face_id1=face_id1, face_id2=face_id2)
        return verify_result

    def _draw_face_rectangle(self, image_path, face, isIdentical = False, display_image = False):
        """Draw rectangle around the detected face and display the image."""
        image = cv2.imread(image_path)
        fd = face.as_dict()
        
        
        x1 = fd['faceRectangle']['left'] - self.buffer
        y1 = fd['faceRectangle']['top'] - self.buffer
        x2 = x1 + fd['faceRectangle']['width'] + 2*self.buffer
        y2 = y1 + fd['faceRectangle']['height'] + 2*self.buffer
        
        # Draw rectangle on the image
        color = (0, 255, 0) if isIdentical else (0, 0, 255)

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        output_path = os.path.join(self.work_dir, f"face_rectangle_{uuid.uuid4()}.png")
        cv2.imwrite(output_path, image)

        if display_image:
            # Display the image
            plt.axis('off')
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            plt.show()

        return output_path



    def rectangle_faces(self, id_doc, images):
        for im in images:
            photo_analysis_ret_dict = self.detect_faces(im, display_image=False, print_results=False)
            face_ids = photo_analysis_ret_dict['face_ids']
            results = photo_analysis_ret_dict['results']

            if len(face_ids) > 0:                                  
                im_fn = self.extract_and_save_cropped_face(im, results)     
                print(f"Uploading face image to blob storage: {im_fn}")
                id_doc.photo = storage_helper.upload_document(im_fn)                                        
                break

        return id_doc
    

    def compare_document_photos(self, file_path_1, file_path_2, display_image=False, print_results=False):

        if file_path_1.startswith("http") and (".blob.core.windows.net" in file_path_1):
            file_path_1 = storage_helper.download_blob_by_url(file_path_1)

        if file_path_2.startswith("http") and (".blob.core.windows.net" in file_path_2):
            file_path_2 = storage_helper.download_blob_by_url(file_path_2)

        ret_dict_1 = self.detect_faces(file_path_1, display_image=display_image, print_results=print_results)
        ret_dict_2 = self.detect_faces(file_path_2, display_image=display_image, print_results=print_results)

        face_ids_0 = ret_dict_1['face_ids']
        face_ids_1 = ret_dict_2['face_ids']

        if (len(face_ids_0) == 0) or (len(face_ids_1) == 0):
            print("Please provide images with at least one photo.")
            verify_result = {
                "error": "Please provide images with at least one photo.",
                'isIdentical': False, 
                'confidence': -1
            }

        else:
            face_1 = self.find_highest_quality_face(ret_dict_1['results'])
            face_2 = self.find_highest_quality_face(ret_dict_2['results'])

            verify_result = self.verify_faces(face_1['faceId'], face_2['faceId'])

            im_fn_1 = self._draw_face_rectangle(file_path_1, face_1, isIdentical=verify_result['isIdentical'])     
            photo_1 = storage_helper.upload_document(im_fn_1)   

            im_fn_2 = self._draw_face_rectangle(file_path_2, face_2, isIdentical=verify_result['isIdentical'])     
            photo_2 = storage_helper.upload_document(im_fn_2)   

            verify_result['photo_1'] = photo_1
            verify_result['photo_2'] = photo_2
            print(f"Verify face to face: {verify_result}")

        return verify_result
    

    def find_highest_quality_face(self, faces):
        face = faces[0]
        for face_r in faces:
            if face_r.face_attributes.quality_for_recognition == QualityForRecognition.HIGH:
                face = face_r
                break
        
        return face

    def extract_and_save_cropped_face(self, image_path, faces):
        """Extract the cropped face from the image and save it as a new image file."""

        face = self.find_highest_quality_face(faces)
        
        image = cv2.imread(image_path)
        fd = face.as_dict()

        # Extract face rectangle coordinates
        x1 = fd['faceRectangle']['left'] - self.buffer
        y1 = fd['faceRectangle']['top'] - self.buffer
        x2 = x1 + fd['faceRectangle']['width'] + 2*self.buffer
        y2 = y1 + fd['faceRectangle']['height'] + 2*self.buffer

        # Crop the face from the image
        cropped_face = image[y1:y2, x1:x2]

        # Generate a unique filename for the cropped face image
        file_name = f"{uuid.uuid4()}.png"
        file_path = os.path.join(self.work_dir, file_name)

        # Save the cropped face image
        cv2.imwrite(file_path, cropped_face)

        print(f"Cropped face saved at: {file_path}")
        return file_path    