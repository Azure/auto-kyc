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

- npm package manager installed on your machine for the frontend
- Python 3.10+ (for the backend)
- Azure account with Face API and OpenAI services enabled
- Azure Blob Storage and Cosmos DB set up



### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Azure/auto-kyc.git
   cd auto-kyc
   ```

2. **Backend Setup**:
   - Install Python dependencies:
     ```bash
     conda create -n auto-kyc python=3.10
     conda activate auto-kyc
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
     uvicorn api:app --port 80 --reload
     ```

3. **Frontend Setup**:
   - Navigate to the frontend directory:
     ```bash
     cd ../ui
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


### Face API Access and Installation

Please follow the instructions in the [link here](https://github.com/Azure-Samples/azure-ai-vision-sdk/blob/main/GET_FACE_ARTIFACTS_ACCESS.md), to apply for access. 

After getting access, and creating the Face API resource on Azure, you will need to:
1. Generate an access token
1. Create an .npmrc file with the access token, please follow the instructions [here](https://github.com/Azure-Samples/azure-ai-vision-sdk/blob/main/samples/web/SetupEnvironment.md).
1. Download the node module:
    ```bash
    npm install azure-ai-vision-face-ui@latest
    ```
1. After installing the `azure-ai-vision-face-ui` node package, navigate to the installed files under `ui > react-js > node_modules > azure-ai-vision-face-ui` and copy the whole folder and the contents of the `facelivenessdetector-assets` directory as is into the `ui > react-js > public` directory.

The `ui > react-js > public` directory should eventually look like this:

```bash
public
├── assets
├── facelivenessdetector-assets
├── sample-documents
└── index.html
```

## Folder Structure

The project is organized as follows:

```
auto-kyc/
├── code/                 # Python FastAPI backend
│   ├── utils/               # Helper modules for storage, document processing, etc.
│   ├── data_models/         # Data models for ID document processing
│   └── env_vars.py          # Environment variable configuration
├── frontend/                # React frontend application
│   ├── public/              # Static assets
│   ├── src/                 # Source code for the React application
│   └── package.json         # Frontend dependencies
└── api.py                   # API Server
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


## Contributing

Contributions are welcome! Please follow the steps below:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit and push your changes (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
