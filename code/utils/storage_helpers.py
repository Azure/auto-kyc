import os
import urllib
from requests.utils import requote_uri
from datetime import datetime, timezone, timedelta

import logging
import copy
import uuid
import json
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    ContainerClient,
    generate_blob_sas,
    BlobSasPermissions,
)
from azure.identity import DefaultAzureCredential

from env_vars import *

class BlobStorageHelper:
    def __init__(self, storage_account_name = AZURE_STORAGE_ACCOUNT_NAME, container_name = AZURE_STORAGE_CONTAINER_NAME, category_id = COSMOS_CATEGORYID):
        self.work_dir = "temp_imgs"
        os.makedirs(self.work_dir, exist_ok=True)

        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self.category_id = category_id
        self.account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
        self.credential = DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient(
            account_url=self.account_url, credential=self.credential
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        # Ensure the container exists
        try:
            self.container_client.get_container_properties()
        except Exception:
            self.container_client.create_container()

    def create_sas_from_blob(self, blob_name, expiry_days=1):
        """
        Creates a SAS token for the specified blob.

        :param blob_name: The name of the blob for which the SAS token will be generated.
        :param expiry_hours: The number of hours until the SAS token expires.
        :return: The SAS URL for the blob.
        """
        blob_name = os.path.basename(blob_name)

        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_name
        )

        # Generate a valid user delegation key with timezone-aware datetime
        key_start_time = datetime.now(timezone.utc)
        key_expiry_time = key_start_time + timedelta(days=expiry_days)


        print(f"Expiry time: {key_expiry_time}")
        user_delegation_key = self.blob_service_client.get_user_delegation_key(
            key_start_time=key_start_time,
            key_expiry_time=key_expiry_time,
        )

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            user_delegation_key=user_delegation_key,
            protocol="https",
            start=key_start_time,
            expiry=key_expiry_time,  # Using timezone-aware datetime
        )

        # Construct the SAS URL
        sas_url = blob_client.url + "?" + sas_token
        return sas_url

    def save_json_document(self, data_dict):
        new_doc = copy.deepcopy(data_dict)
        new_doc["id"] = new_doc.get("id", str(uuid.uuid4()))
        new_doc["categoryId"] = self.category_id
        new_doc["timestamp"] = new_doc.get(
            "timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        new_doc["doc_url"] = new_doc.get(
            "doc_url",
            f"https://{self.storage_account_name}.blob.core.windows.net/"
            f"{self.container_name}/{new_doc['id']}.json",
        )

        new_doc.pop("content", None)

        blob_name = f"{new_doc['id']}.json"
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(json.dumps(new_doc, indent=4), overwrite=True)

        ret_dict = {
            "status": f"Document {new_doc['id']} was successfully saved to the "
            f"{self.container_name} container"
        }
        logging.info(ret_dict["status"])
        return ret_dict

    def list_documents(self):
        blobs = []
        generator = self.container_client.list_blobs()
        for blob in generator:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob.name
            )
            blobs.append(blob_client.url)
        return blobs

    def get_document_url(self, blob_name):
        url = (
            f"https://{self.storage_account_name}.blob.core.windows.net/"
            f"{self.container_name}/{blob_name}"
        )
        return requote_uri(url)

    def get_document(self, blob_name, as_text=True):
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        download_stream = blob_client.download_blob()
        if as_text:
            return download_stream.content_as_text()
        else:
            return download_stream.readall()

    def download_document_by_url(self, url, as_text=True):
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        # Path format is /container/blob_name
        path_parts = path.lstrip("/").split("/", 1)
        if len(path_parts) != 2:
            raise ValueError("URL path does not contain container and blob name")
        container_name, blob_name = path_parts
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        download_stream = blob_client.download_blob()
        if as_text:
            return download_stream.content_as_text()
        else:
            return download_stream.readall()

    def upload_document(self, local_file_path, blob_name=None):
        """
        Uploads a local file to Azure Blob Storage.

        :param local_file_path: The path to the local file to upload.
        :param blob_name: The name of the blob in storage. If not provided,
                          the local file name will be used.
        :return: The URL of the uploaded blob.
        """
        if not blob_name:
            blob_name = os.path.basename(local_file_path)

        blob_client = self.container_client.get_blob_client(blob=blob_name)

        with open(local_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        blob_url = blob_client.url
        logging.info(f"Uploaded {local_file_path} to {blob_url}")
        return blob_url

    def download_document(self, blob_name, local_file_path = None):
        """
        Downloads a blob from Azure Blob Storage to a local file.

        :param blob_name: The name of the blob to download.
        :param local_file_path: The local path where the blob will be saved.
        :return: None
        """
        if local_file_path is None:
            local_file_path = os.path.join(self.work_dir, blob_name)

        # if os.path.exists(local_file_path):
        #     logging.info(f"File {local_file_path} already exists. Skipping download.")
        #     return
        
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        download_stream = blob_client.download_blob()

        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        with open(local_file_path, "wb") as file:
            file.write(download_stream.readall())

        logging.info(f"Downloaded {blob_name} to {local_file_path}")

        return local_file_path


    def download_blob_by_url(self, url, local_file_path=None):
        """
        Downloads a blob from Azure Blob Storage using its URL and saves it locally.

        :param url: The full URL of the blob to download.
        :param local_file_path: The local path where the blob will be saved. If not provided,
                                the blob name will be used as the local file name.
        :return: The path of the downloaded file.
        """
        # Parse the URL to extract container name and blob name
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        # Path format is /container/blob_name
        path_parts = path.lstrip("/").split("/", 1)
        if len(path_parts) != 2:
            raise ValueError("URL path does not contain container and blob name")
        
        container_name, blob_name = path_parts
        
        # Get blob client
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )

        # Set local file path if not provided
        if local_file_path is None:
            local_file_path = os.path.join(self.work_dir, blob_name)

        # Create local directories if they don't exist
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Download the blob and save it to the local file
        download_stream = blob_client.download_blob()
        with open(local_file_path, "wb") as file:
            file.write(download_stream.readall())

        logging.info(f"Downloaded blob {blob_name} from {url} to {local_file_path}")
        
        return local_file_path


    def upload_document_with_sas(self, local_file_path, blob_name=None, expiry_days=1):
        """
        Uploads a local file to Azure Blob Storage and generates a SAS token.

        :param local_file_path: The path to the local file to upload.
        :param blob_name: The name of the blob in storage. If not provided,
                        the local file name will be used.
        :param expiry_hours: The number of hours until the SAS token expires.
        :return: The SAS URL of the uploaded blob.
        """
        # Upload the document
        uploaded_blob_url = self.upload_document(local_file_path, blob_name)

        # Get the blob name if it wasn't provided
        if not blob_name:
            blob_name = os.path.basename(local_file_path)

        # Generate the SAS token for the uploaded blob
        sas_url = self.create_sas_from_blob(blob_name, expiry_days=expiry_days)

        logging.info(f"Uploaded {local_file_path} and generated SAS URL: {sas_url}")
        return sas_url