# utils.py
import streamlit as st
import requests
import copy
import os
import json
import base64
import io
from PIL import Image
import uuid



# Function to fetch customer data
def fetch_customer_data(customer_id):
    response = requests.get(f'http://localhost:8000/api/customer/{customer_id}')
    if response.status_code == 200:
        st.session_state.customer_data = response.json()
        st.session_state.customer_id = customer_id
        st.session_state.status = 'Customer Data Loaded'
        photo_url = st.session_state.customer_data["photo"].replace("'", "").replace('"', '')
        response = requests.post('http://localhost:8000/api/get_sas', json={"url": photo_url})        
        st.session_state.customer_data["photo_sas"] = response.json().get('sas', '')
        
    else:
        st.error("Customer not found.")
        st.session_state.customer_data = {}
        st.session_state.customer_id = None
        st.session_state.status = 'Error'

    st.rerun()

# Function to upload files
def upload_files(files):
    # Store the file bytes and names in session state
    if st.session_state.uploaded_file_names == [file.name for file in files]: return

    st.session_state.uploaded_file_bytes =  [file.read() for file in files]
    st.session_state.uploaded_file_names = [file.name for file in files]

    # Reset file pointer to beginning after reading
    for file in files:
        file.seek(0)

    files_to_upload = [('files', file.getvalue()) for file in files]
    response = requests.post('http://localhost:8000/api/upload', files=files_to_upload)
    if response.status_code == 200:
        st.success("Files uploaded successfully.")
    else:
        st.error("File upload failed.")
    st.rerun()

# Function to analyze documents
def analyze_documents():
    st.session_state.analyze_button = True
    customer_id = st.session_state.customer_data.get('id', '')
    if customer_id:

        info = {}
        info['customer_id'] = customer_id
        im_bytes = Image.open(io.BytesIO(st.session_state.selected_id_document))
        buffered = io.BytesIO()
        im_bytes.save(buffered, format="JPEG")  # or "PNG" depending on the image type
        image_data = buffered.getvalue()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        info['id_document'] = image_base64
        info['id_document_name'] = st.session_state.selected_id_document_name

        response = requests.post(f'http://localhost:8000/api/analyze', json=info)
        if response.status_code == 200:
            data = response.json()
            st.session_state.extracted_data = data.get('document_id_extracted_data', {})
            st.session_state.logs = data.get('log_checks', [])

            if data.get('data_fields_status', 'Unknown') == True:
                st.session_state.status = 'OK'
            else:
                st.session_state.status = 'Not OK'

            if data.get('photo_comparison_status', 'Unknown') == True:
                st.session_state.photo_status = 'OK'
            else:
                st.session_state.photo_status = 'Not OK'

            visual_analysis = data.get('photo_comparison_result', {})
            
            if visual_analysis.get('photo_2', False):
                response = requests.post('http://localhost:8000/api/get_sas', json={"url": visual_analysis['photo_2']})        
                st.session_state.current_showing_profile_photo = response.json().get('sas', '')
                st.session_state.current_showing_profile_toggle = True
            
            if visual_analysis.get('photo_1', False):
                response = requests.post('http://localhost:8000/api/get_sas', json={"url": visual_analysis['photo_1']})        
                st.session_state.current_showing_id_document = response.json().get('sas', '')
                st.session_state.current_showing_id_document_toggle = True

            st.success("Analysis complete.")
        else:
            st.error("Analysis failed.")
    else:
        st.error("No customer data available.")

    st.session_state.analyze_button = False
    st.rerun()

# Function to update customer data
def update_customer_data():
    cust_record = copy.deepcopy(st.session_state.customer_data)
    del cust_record['photo_sas']
    response = requests.post('http://localhost:8000/api/update', json=cust_record)
    if response.status_code == 200:
        st.success("Database updated successfully.")
    else:
        st.error("Failed to update database.")

# Custom CSS for limiting sizes and improving layout
def add_custom_css():
    st.markdown("""
        <style>
        /* Limiting the width of the columns */
        div[data-testid="column"]:nth-child(1) {
            flex: 0 0 300px;  /* Left Column width (fixed 300px) */
            max-width: 300px;
            min-width: 300px;
        }
        div[data-testid="column"]:nth-child(2) {
            flex: 1;  /* Center Column takes up remaining space */
        }
        div[data-testid="column"]:nth-child(3) {
            flex: 0 0 300px;  /* Right Column width (fixed 300px) */
            max-width: 300px;
            min-width: 300px;
        }
        /* Limiting height and width of the Document Viewer */
        img {
            max-width: 600px;
            max-height: 400px;
            object-fit: cover;  /* Ensure image is contained within these dimensions */
        }
        section[data-testid="stSidebar"] {
            width: 340px !important; # Set the width to your desired value
        }
        </style>
        """, unsafe_allow_html=True)


def render_logs(logs):
    """
    Renders logs as stacked blocks with labels and colored backgrounds.
    Each log will have a color-coded background based on its type (success, warning, error, info).
    """

    # Loop through each log and display it with a colored background
    for log in logs:
        # Determine the background color based on log type (assuming the log has a "type" field)
        log_type = log.get("type", "info")
        highlight_color = {
            "success": "#4caf50",   # Green
            "error": "#f44336",     # Red
            "warning": "#ffeb3b",   # Yellow
            "info": "#2196f3"       # Blue
        }.get(log_type, "#2196f3")  # Default to blue if type is unknown
        
        # Set text color based on background (black for yellow, white for others)
        text_color = "#000" if log_type == "warning" else "#fff"

        # Create the log block with inline styles for color and bolding
        log_block = f"""
        <div style="background-color: {highlight_color}; padding: 10px; border-radius: 5px; margin-bottom: 5px; color: {text_color};">
            <span style="font-size: 14px;"><b style="color: #fff;">{log.get('message', '')}</b></span>
        </div>
        """

        # Render the log block in the Streamlit app
        st.markdown(log_block, unsafe_allow_html=True)


