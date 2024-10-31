import os
import json

import tempfile 
from pdf2image import convert_from_path
import PIL
from PIL import Image
import uuid
from data_models.id_document import *
from data_models.name_check import *
from data_models.address_check import *
from data_models.field_check import *

from utils.storage_helpers import *
from utils.general_helpers import *
from utils.cosmos_helpers import *
from utils.face_service import *
from utils.field_checker import FieldChecker

import logging

logger = logging.getLogger(__name__)

from rich.console import Console
console = Console()


cosmos = CosmosDBHelper()
blob_helper = BlobStorageHelper() 

module_directory = os.path.dirname(os.path.abspath(__file__))


class IDDocumentProcessor():

    def __init__(self, customer_id = None, doc_path = None):

        self.work_dir = 'temp_imgs'
        os.makedirs(self.work_dir, exist_ok=True)

        self.customer_id = customer_id
        self.prompt_template = read_file(os.path.join(module_directory, "../prompts/id_document_extraction.txt"))
        self.extract_document(doc_path)
        self.field_checker = FieldChecker()


    def extract_document(self, doc_path):
        logger.info(f"Extracting information from document: {doc_path}")
        if doc_path.endswith(".pdf"):
            pdf_images = convert_from_path(doc_path)
            self.images = []

            for pdf_image in pdf_images:
                fn = os.path.join(self.work_dir, str(uuid.uuid4()))
                pdf_image.save(fn)
                self.images.append(fn)

            self.doc_path = doc_path

        elif doc_path.endswith(".jpg") or doc_path.endswith(".png") or doc_path.endswith(".jpeg"):
            # self.images = [cv2.imread(doc_path)]
            self.images = [doc_path]
            self.doc_path = doc_path
        else:
            raise ValueError(f"Provide either a PDF path or an image path.\n{doc_path}")


    def process_document(self, doc_path = None):
        photo_analysis_ret_dict = {}

        if doc_path is not None:
            self.extract_document(doc_path)
            self.doc_path = doc_path

        doc_explanation = "Please check attached image."
        extracted = "No extracted information."
        prompt = self.prompt_template.format(document=doc_explanation, extracted=extracted)
        id_doc = ask_LLM_with_structured_outputs(prompt,  self.images, response_format=IDDocument)
        id_doc.file_url = blob_helper.upload_document(self.doc_path) 
        
        # if id_doc.photo == 'True':
        #     id_doc = self.rectangle_faces(id_doc)

        return {
            "id_doc": id_doc,
            "photo_analysis_ret_dict": photo_analysis_ret_dict
        }


    def rectangle_faces(self, id_doc, images):
        if images is None: images = self.images

        face_service = FaceRecognitionService()

        for im in images:
            photo_analysis_ret_dict = face_service.detect_faces(im, display_image=False, print_results=False)
            face_ids = photo_analysis_ret_dict['face_ids']
            results = photo_analysis_ret_dict['results']

            if len(face_ids) > 0:                                  
                im_fn, face_index = face_service.extract_and_save_cropped_face(im, results)     
                print(f"Uploading face image to blob storage: {im_fn}")
                id_doc.photo = blob_helper.upload_document(im_fn)                                        
                break

        return id_doc


    def IDDocument_to_dict(id_doc):
        return id_doc.dict()
    

    def dict_to_IDDocument(id_doc_dict):
        return IDDocument(**id_doc_dict)
    
        
    def compare_document_to_database(self, customer_id = None, categoryId = COSMOS_CATEGORYID_VALUE):

        if customer_id is None: customer_id = self.customer_id

        red_dict = self.process_document()
        id_doc = red_dict['id_doc']
        photo_analysis_ret_dict = red_dict['photo_analysis_ret_dict']
        id_doc_dict = IDDocumentProcessor.IDDocument_to_dict(id_doc)
        id_doc_from_db = cosmos.read_document(customer_id, partition_key=categoryId)

        console.print(40*"-")
        print("-- Extracted Document --")
        console.print(id_doc_dict)
        console.print(40*"-")
        print("-- Database Document --")
        console.print(id_doc_from_db)
        console.print(40*"-")

        name_check = False

        checks = {}
        
        for k in list(IDDocument.__fields__.keys()):
            if id_doc_dict[k] is None: continue
            if id_doc_from_db.get(k, None) is None: 
                checks[k] = FieldComparisonResult(match=False, field1=id_doc_dict[k], field2="None", result="Different")
                continue

            if k in ['photo', 'signature', 'additional_attributes', 'document_type', "file_url", "photo_sas"]:
                continue
                   
            if id_doc_dict[k] != id_doc_from_db[k]:
                print(f"Field {k} does not match. Document: {id_doc_dict[k]}. Database: {id_doc_from_db[k]}. Calling LLM for comparison.")

                if k in names_fields:
                    if not name_check:
                        name1 = f"{id_doc_dict['first_name']} {id_doc_dict['middle_name']} {id_doc_dict['last_name']}"
                        name2 = f"{id_doc_from_db['first_name']} {id_doc_from_db['middle_name']} {id_doc_from_db['last_name']}"
                        check = self.field_checker.check_name(name1, name2)
                        name_check = True
                        checks[k] = check
                        print(f">>> Name Matching Result: {check}")
                
                elif k == 'address':
                    check = self.field_checker.check_address(id_doc_dict[k], id_doc_from_db[k])
                    checks[k] = check
                    print(f">> Address Matching Result: {check}")

                else:
                    check = self.field_checker.check_field(k, id_doc_dict[k], id_doc_from_db[k])  
                    checks[k] = check
                    print(f">> Field {k} Matching Result: {check}")
                
            else:
                print(f"Field {k} matches. Document: {id_doc_dict[k]}. Database: {id_doc_from_db[k]}")
                checks[k] = FieldComparisonResult(match=True, field1=id_doc_dict[k], field2=id_doc_from_db[k], result="Same")
        
        status = all([checks[check].result == "Same" for check in checks])

        face_service = FaceRecognitionService()
        photo_comparison_result = face_service.compare_document_photos(self.images[0], id_doc_from_db['photo'])

        if "error" in photo_comparison_result:
            photo_status = False
        else: 
            photo_status = photo_comparison_result["isIdentical"]

        # Define the structure for log checks
        log_checks = []

        for k, result in checks.items():
            # Determine the type of the log based on the result
            if result.result == "Same":
                log_type = "success"
                log_message = f"{k} matches."
            else:
                log_type = "error"
                log_message = f"{k} does not match."

            # Append the log message and type to the log_checks list
            log_checks.append({
                "type": log_type,
                "message": log_message
            })

        # Example: Adding the photo comparison to the logs
        if photo_status:
            log_checks.append({
                "type": "success",
                "message": "The photos match."
            })
        else:
            log_checks.append({
                "type": "error",
                "message": "Photos don't match"
        })
    

        return {
            "data_fields_checks": {check:checks[check].to_string() for check in checks}, 
            "document_id_extracted_data": id_doc_dict,
            "document_visual_analysis": photo_analysis_ret_dict,
            "data_fields_status": status,
            "photo_comparison_result": photo_comparison_result,
            "photo_comparison_status": photo_status,
            "log_checks": log_checks
        }




