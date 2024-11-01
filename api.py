# api.py
import os

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pydantic import BaseModel
import uuid
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import base64

import sys
sys.path.append('code')

import tempfile
from dotenv import load_dotenv
load_dotenv()

from utils.storage_helpers import *
from utils.cosmos_helpers import *
from utils.id_document_processor import *
from utils.general_helpers import *
from utils.face_liveness import *

from env_vars import *

import logging
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.INFO)

cosmos = CosmosDBHelper()
blob_helper = BlobStorageHelper()


class LivenessSessionRequest(BaseModel):
    livenessOperationMode: str
    sendResultsToClient: bool
    deviceCorrelationId: str

class LivenessSessionResponse(BaseModel):
    authToken: str
    session_id: str

# uvicorn main:app --reload
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ["http://localhost:80", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/detectLiveness", response_model=LivenessSessionResponse)
async def detect_liveness(
    parameters: str = Form(...),
    verify_image: UploadFile = File(None)
):
    # Log incoming data for debugging
    print("Received parameters:", parameters)
    print("Received verify_image:", verify_image.filename if verify_image else None)

    # Parse the parameters
    session_request = LivenessSessionRequest.parse_raw(parameters)

    # Read the verify image if provided
    verify_image_content = None
    if verify_image is not None:
        verify_image_content = await verify_image.read()

    flc = FaceLivenessDetectionService()
    session = await flc.startLivenessDetection(session_request, verify_image_content)

    return {
        "authToken": session.auth_token,
        "session_id": session.session_id
    }

@app.post("/api/livenessComplete")
async def livenessComplete(info: dict):
    print("info", info)
    flc = FaceLivenessDetectionService()
    await flc.queryLivenessDetectionResults(info.get("session_id"))

@app.get("/api/customers")
async def get_customers():
    # Fetch list of customers from the database
    customers = cosmos.get_all_documents()
    # Return a list of customer IDs and names
    customer_list = []
    for customer in customers:
        customer_id = customer.get("id")
        first_name = customer.get("first_name", "")
        last_name = customer.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        customer_list.append({
            "id": customer_id,
            "name": full_name
        })
    return customer_list

@app.post("/api/get_sas")
async def get_sas(info: dict):
    file_url = info.get("url", "")
    file_url = file_url.replace("'", "").replace('"', '')
    return {"sas": blob_helper.create_sas_from_blob(file_url)}

@app.get("/api/customer/{customer_id}")
async def get_customer(customer_id: str):
    # Fetch customer data from the database
    customer_record = cosmos.read_document(customer_id, partition_key="customers")
    if customer_record:
        return customer_record
    else:
        return {"error": "Customer not found."}

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    # Process uploaded files
    file_names = [file.filename for file in files]
    return {"uploaded_files": file_names}

@app.post("/api/analyze")
async def analyze_documents(info: dict):
    customer_id = info.get("customer_id", "")
    id_document = base64.b64decode(info.get("id_document", ""))
    id_document_name = info.get("id_document_name", "")

    logger.info(f"Analyzing document for customer {customer_id}")
    logger.info(f"Document name: {id_document_name}")
    logger.info(f"Document size: {len(id_document)} bytes")

    work_dir = "temp_imgs"
    os.makedirs(work_dir, exist_ok=True)
    im_fn = os.path.join(work_dir, id_document_name)
    write_bytes_to_file(id_document, im_fn, "wb")
    doc_processor = IDDocumentProcessor(customer_id=customer_id, doc_path=im_fn)
    return doc_processor.compare_document_to_database()

@app.get("/api/status/{customer_id}")
async def get_status(customer_id: str):
    return {"customer_id": customer_id, "status": "green"}

@app.get("/api/logs/{customer_id}")
async def get_logs(customer_id: str):
    return {"customer_id": customer_id, "logs": ["No discrepancies found."]}

@app.post("/api/update")
async def update_customer(data: dict):
    data = copy.deepcopy(data)
    try: del data['photo_sas']
    except: pass

    try: del data['processedPhotoUrl']
    except: pass
    
    return cosmos.upsert_document(data)

# Mount the 'build' directory to serve static files
app.mount("/", StaticFiles(directory="ui/react-js/build", html=True), name="static")
