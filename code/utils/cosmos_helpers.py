import logging
from azure.cosmos import CosmosClient, PartitionKey
import copy
import uuid

from env_vars import *

import logging
import copy
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential

from env_vars import COSMOS_URI, COSMOS_DB_NAME, COSMOS_CONTAINER_NAME, COSMOS_CATEGORYID

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

class CosmosDBHelper:
    def __init__(self, container_name=COSMOS_CONTAINER_NAME):
        try:
            credential = DefaultAzureCredential()
            self.client = CosmosClient(url=COSMOS_URI, credential=credential)
            self.database = self.client.create_database_if_not_exists(id=COSMOS_DB_NAME)
            self.container = self.database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path="/categoryId"),
                indexing_policy={
                    "includedPaths": [{"path": "/*"}],
                    "excludedPaths": [{"path": "/_etag/?"}]
                }
            )
        except Exception as e:
            logging.error(f"Failed to initialize Cosmos DB: {e}")
            raise

    def get_all_documents(self):
        try:
            return list(self.container.read_all_items(max_item_count=10))
        except Exception as e:
            logging.error(f"Error reading all documents: {e}")
            return []

    def read_document(self, doc_id, partition_key=COSMOS_CATEGORYID):
        try:
            return self.container.read_item(item=doc_id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            logging.warning(f"Document with ID {doc_id} not found.")
            return None
        except Exception as e:
            logging.error(f"Error reading document {doc_id}: {e}")
            return None

    def query_documents(self, query, parameters):
        try:
            return list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
        except Exception as e:
            logging.error(f"Error querying documents: {e}")
            return []

    def upsert_document(self, document):
        try:
            return self.container.upsert_item(body=document)
        except Exception as e:
            logging.error(f"Error upserting document: {e}")
            return None

    def delete_document(self, doc_id, partition_key=COSMOS_CATEGORYID):
        try:
            self.container.delete_item(item=doc_id, partition_key=partition_key)
            logging.info(f"Deleted document with ID {doc_id}")
        except exceptions.CosmosResourceNotFoundError:
            logging.warning(f"Document with ID {doc_id} not found.")
        except Exception as e:
            logging.error(f"Error deleting document {doc_id}: {e}")

    def clean_document(self, document, allowed_fields):
        clean_doc = {k: v for k, v in document.items() if k in allowed_fields}
        return clean_doc

    def create_document(self, document):
        if document.get("id") is None: document['id'] = str(uuid.uuid4())
        if document.get('categoryId') is None: document[COSMOS_CATEGORYID] = COSMOS_CATEGORYID_VALUE

        try:
            return self.container.create_item(body=document)
        except Exception as e:
            logging.error(f"Error creating document: {e}")
            return None

    def get_document_by_id(self, doc_id, category_id=COSMOS_CATEGORYID):
        query = "SELECT * FROM c WHERE c.categoryId = @categoryId AND c.id = @id"
        parameters = [
            {"name": "@categoryId", "value": category_id},
            {"name": "@id", "value": doc_id}
        ]
        results = self.query_documents(query, parameters)
        return results[0] if results else None
