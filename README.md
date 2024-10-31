# Auto-KYC Application

The Auto-KYC Application offers an advanced, AI-powered identity verification solution that streamlines the compliance process for financial institutions and businesses. By leveraging Azure's Face API for facial recognition and Azure OpenAI for intelligent data extraction and semantic comparison, our platform ensures accurate and secure verification of ID documents against customer records. This solution not only reduces manual verification time but also enhances fraud detection and compliance accuracy, making it ideal for companies seeking to optimize their onboarding and regulatory processes with cutting-edge AI technology. 
Face Liveness detection is used to determine if a face in an input video stream is real or fake. It's an important building block in a biometric authentication system to prevent imposters from gaining access to the system using a photograph, video, mask, or other means to impersonate another person. The goal of liveness detection is to ensure that the system is interacting with a physically present, live person at the time of authentication. 


## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Backend Services](#backend-services)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Document Upload and Analysis**: Supports uploading documents (e.g., passport, driver's license) for analysis using Azure services.
- **Automated Data Extraction**: Uses Azure OpenAI models to automatically extract relevant fields from documents.
- **Semantic Field Comparison**: Compares extracted data with the corresponding records in the database using natural language processing techniques.
- **Face Recognition and Matching**: Leverages Azure Face API to detect and compare faces from the uploaded document with the stored customer records.
- **Log Viewer and Status Indicators**: Provides a visual interface to review data comparison results, including matching status and discrepancies.
- **Face Liveness Check**: Determines if a face in an input video stream is real or fake

## Architecture Overview

The KYC application is divided into two main components:

1. **Frontend (React Application)**:
   - A React-based user interface for uploading documents, viewing and editing customer data, and visualizing document analysis results.
   - Responsive layout with a fixed-width sidebar (340px) for navigation and status indicators.
   - Uses Material-UI for styling and layout components.

2. **Backend (Python FastAPI Server)**:
   - **Document Processing**: Handles file uploads and processes documents using Python libraries like `pdf2image` and `PIL` for image handling.
   - **Data Extraction and Verification**: Integrates with Azure OpenAI models to extract structured information from uploaded documents.
   - **Face Recognition**: Uses Azure Face API for detecting and comparing faces in documents.
   - **Semantic Comparison**: Leverages Azure OpenAI to perform semantic matching of extracted fields with the stored data, going beyond simple string matching.
   - **Storage and Database**: Utilizes Azure Blob Storage for storing document images and Azure Cosmos DB for storing customer data.

## Installation

### Prerequisites

- Node.js (for the frontend)
- Python 3.8+ (for the backend)
- Azure account with Face API and OpenAI services enabled
- Azure Blob Storage and Cosmos DB set up

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/kyc-application.git
   cd kyc-application
   ```

2. **Backend Setup**:
   - Install Python dependencies:
     ```bash
     cd backend
     pip install -r requirements.txt
     ```
   - Set up environment variables in a `.env` file:
     ```
     FACE_API_ENDPOINT=<your-face-api-endpoint>
     FACE_API_KEY=<your-face-api-key>
     AZURE_OPENAI_ENDPOINT=<your-openai-endpoint>
     AZURE_OPENAI_KEY=<your-openai-key>
     COSMOS_DB_URI=<your-cosmos-db-uri>
     COSMOS_DB_KEY=<your-cosmos-db-key>
     ```
   - Run the FastAPI server:
     ```bash
     uvicorn main:app --reload
     ```

3. **Frontend Setup**:
   - Navigate to the frontend directory:
     ```bash
     cd ../frontend
     ```
   - Install frontend dependencies:
     ```bash
     npm install
     ```
   - Start the React development server:
     ```bash
     npm start
     ```
   - The application will be available at `http://localhost:3000`.

## Usage

1. **Uploading Documents**:
   - Navigate to the "Upload Documents" page and select an ID document to upload.
   - The uploaded files will be sent to the backend for processing.

2. **Viewing Customer Data**:
   - Select a customer from the "View/Edit Customer Data" page.
   - The system fetches customer records from the Cosmos DB.

3. **Document Analysis**:
   - Go to the "Document Comparison" page to compare the uploaded document with the stored customer data.
   - The backend performs field extraction, face recognition, and semantic data comparison.

4. **Review Logs and Status Indicators**:
   - The sidebar displays the status of data matching and logs any discrepancies found during the analysis.

## Folder Structure

The project is organized as follows:

```
kyc-application/
├── backend/                 # Python FastAPI backend
│   ├── main.py              # Main FastAPI application
│   ├── utils/               # Helper modules for storage, document processing, etc.
│   ├── data_models/         # Data models for ID document processing
│   └── env_vars.py          # Environment variable configuration
├── frontend/                # React frontend application
│   ├── public/              # Static assets
│   ├── src/                 # Source code for the React application
│   └── package.json         # Frontend dependencies
└── README.md                # Project documentation
```

## Backend Services

### 1. **Face Recognition (Azure Face API)**

- The backend uses Azure's Face API to detect faces in uploaded documents.
- It draws rectangles around detected faces and performs face-to-face verification with the stored customer image.
- The service supports quality checks to ensure the highest-quality face is used for verification.

### 2. **Data Extraction (Azure OpenAI)**

- Azure OpenAI models are used to extract key fields from documents, such as name, date of birth, ID number, address, etc.
- The system is designed to work with various types of identification documents, including passports, driver's licenses, and national ID cards.

### 3. **Semantic Field Comparison**

- Once the data is extracted, it is semantically compared with the customer's existing database record using NLP techniques.
- The backend can handle complex comparisons, such as matching name variations, address similarities, and date formats.

### 4. **Data Storage and Retrieval**

- The application uses Azure Blob Storage to securely store document images and processed files.
- Azure Cosmos DB is employed to store and manage customer records, with the backend providing interfaces for reading and updating records.

## API Endpoints

### Customer Management

- **`GET /api/customers`**: Retrieve a list of customers.
- **`GET /api/customer/{customer_id}`**: Fetch details for a specific customer.

### Document Handling

- **`POST /api/upload`**: Upload documents to the backend for processing.
- **`POST /api/analyze`**: Analyze an uploaded document, including field extraction and face recognition.
- **`POST /api/get_sas`**: Obtain a SAS URL for accessing secure resources.
- **`POST /api/update`**: Update a customer's data in the database.

### Status and Logs

- **`GET /api/status/{customer_id}`**: Get the current status of a customer's verification.
- **`GET /api/logs/{customer_id}`**: Retrieve logs of verification checks for a customer.

## Contributing

Contributions are welcome! Please follow the steps below:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit and push your changes (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
