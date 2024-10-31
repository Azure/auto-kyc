from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum



# Define the Enum for document types
class DocumentType(str, Enum):
    PASSPORT = "Passport"
    DRIVER_LICENSE = "Driver's License"
    NATIONAL_ID = "National ID"
    SOCIAL_SECURITY_CARD = "Social Security Card"


names_fields = ['first_name', 'middle_name', 'last_name']

high_priority_fields_list = ['address', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'nationality']
middle_priority_fields_list = ['passport_number', 'place_of_birth', 'passport_issue_date', 'passport_expiry_date', 'passport_place_of_issue', 'passport_mrz_code', 'license_number', 'vehicle_class', 'license_issue_date', 'license_expiry_date', 'national_id_number', 'id_card_issue_date', 'id_card_expiry_date', 'social_security_number', 'ssn_issue_date']
low_priority_fields_list = ['photo', 'signature', 'additional_attributes']


class IDDocument(BaseModel):
    # Common fields across multiple types of IDs
    document_type: DocumentType = Field(..., description="Type of the document (e.g., Passport, Driver's License, National ID, Social Security Card)")

    # Photo
    photo: str = Field(None, description="Confirmation that the ID document does include the individual's photo")

    # Signature 
    signature: str = Field(None, description="Confirmation that the ID document does include the individual's signature")

    # Personal information fields
    first_name: Optional[str] = Field(None, description="Name of the individual (First Name)")
    middle_name: Optional[str] = Field(None, description="Middle name of the individual (Middle)")
    last_name: Optional[str] = Field(None, description="Surname (family name) of the individual (Last)")
    date_of_birth: Optional[str] = Field(None, description="Date of birth in DD.MM.YYYY format")
    nationality: Optional[str] = Field(None, description="Nationality of the individual")
    gender: Optional[str] = Field(None, description="Gender of the individual")

    # Address
    address: Optional[str] = Field(None, description="Home address of the individual (if applicable)")
    
    # Passport-specific fields
    passport_number: Optional[str] = Field(None, description="Passport number")
    place_of_birth: Optional[str] = Field(None, description="Place of birth for passport holders")
    passport_issue_date: Optional[str] = Field(None, description="Date when the passport was issued")
    passport_expiry_date: Optional[str] = Field(None, description="Passport expiry date")
    passport_place_of_issue: Optional[str] = Field(None, description="Place where the passport was issued")
    passport_mrz_code: Optional[str] = Field(None, description="Machine Readable Zone (MRZ) code for passports")
    
    # Driver's License-specific fields
    license_number: Optional[str] = Field(None, description="Driver's license number")
    vehicle_class: Optional[str] = Field(None, description="Vehicle class or endorsement on the license")
    license_issue_date: Optional[str] = Field(None, description="Driver's license issue date")
    license_expiry_date: Optional[str] = Field(None, description="Driver's license expiry date")

    # National ID Card-specific fields
    national_id_number: Optional[str] = Field(None, description="National ID card number")
    id_card_issue_date: Optional[str] = Field(None, description="National ID card issue date")
    id_card_expiry_date: Optional[str] = Field(None, description="National ID card expiry date")

    # Social Security-specific fields
    social_security_number: Optional[str] = Field(None, description="Social Security number")
    ssn_issue_date: Optional[str] = Field(None, description="Date when the Social Security card was issued (if available)")

    # File URL
    file_url: Optional[str] = Field(None, description="URL to the file containing the ID document")
        
    # Additional/Other information
    additional_attributes: Optional[Dict[str, str]] = Field(None, description="Any additional information not covered by other fields")

    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "Passport",
                "first_name": "John",
                "middle_name": "Michael",
                "last_name": "Doe",
                "date_of_birth": "15.06.1985",
                "nationality": "American",
                "passport_number": "123456789",
                "place_of_birth": "Los Angeles, California",
                "passport_issue_date": "01.01.2018",
                "passport_expiry_date": "31.12.2028",
                "passport_place_of_issue": "California, USA",
                "passport_mrz_code": "P<USADOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<<<<",
                "photo": "True",
                "signature": "True"
            }
        }

