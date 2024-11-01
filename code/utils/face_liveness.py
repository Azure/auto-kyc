# face_liveness.py
import cv2
import matplotlib.pyplot as plt
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceSessionClient
from azure.ai.vision.face.models import (
    CreateLivenessSessionContent,
    LivenessOperationMode,
)
from azure.ai.vision.face.models import (
    FaceDetectionModel,
    FaceRecognitionModel,
    FaceAttributeTypeDetection03,
    FaceAttributeTypeRecognition04,
    QualityForRecognition,
)
import uuid
from pydantic import BaseModel

from utils.storage_helpers import *
from env_vars import *

class LivenessSessionRequest(BaseModel):
    livenessOperationMode: str
    sendResultsToClient: bool
    deviceCorrelationId: str

class FaceLivenessDetectionService:

    def __init__(self, endpoint=FACE_API_ENDPOINT, key=FACE_API_KEY, auth_token_time_to_live_in_seconds=120):
        self.face_session_client = FaceSessionClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        self.device_correlation_id = str(uuid.uuid4())
        self.auth_token_time_to_live_in_seconds = auth_token_time_to_live_in_seconds

    async def startLivenessDetection(self, live_session_content=None, verify_image_content=None):
        if verify_image_content is not None:
            # Create liveness session with verification
            created_session = self.face_session_client.create_liveness_with_verify_session(
                CreateLivenessSessionContent(
                    liveness_operation_mode=live_session_content.livenessOperationMode,
                    device_correlation_id=live_session_content.deviceCorrelationId,
                    send_results_to_client=live_session_content.sendResultsToClient,
                    auth_token_time_to_live_in_seconds=self.auth_token_time_to_live_in_seconds,
                ),
                verify_image=verify_image_content,
            )
        else:
            # Create liveness session without verification
            created_session = self.face_session_client.create_liveness_session(
                CreateLivenessSessionContent(
                    liveness_operation_mode=live_session_content.livenessOperationMode,
                    device_correlation_id=live_session_content.deviceCorrelationId,
                    send_results_to_client=live_session_content.sendResultsToClient,
                    auth_token_time_to_live_in_seconds=self.auth_token_time_to_live_in_seconds,
                )
            )

        print("Session created.")
        print(f"Session id: {created_session.session_id}")
        print(f"Auth token: {created_session.auth_token}")

        return created_session

    async def queryLivenessDetectionResults(self, session_id):
        try:
            liveness_result = self.face_session_client.get_liveness_session_result(session_id)
            print(f"Session id: {liveness_result.id}")
            print(f"Session status: {liveness_result.status}")
            print(f"Liveness status: {liveness_result.liveness_result.liveness_assessment}")
            if liveness_result.recognition_result:
                print(f"Recognition status: {liveness_result.recognition_result.status}")
        except Exception as e:
            print(f"Error: {e}")
