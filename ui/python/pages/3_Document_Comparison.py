# pages/3_Document_Comparison.py
import streamlit as st
from PIL import Image
import io
import sys
import os
import json
import requests
import copy
import uuid

# Ensure the utils module is accessible
sys.path.append(os.path.abspath('.'))
from ui_utils import (
    fetch_customer_data,
    analyze_documents,
    add_custom_css,
    render_logs
)

st.set_page_config(page_title="Document Comparison", layout="wide")

# Initialize session state variables
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {}
if 'uploaded_file_bytes' not in st.session_state:
    st.session_state.uploaded_file_bytes = []
if 'uploaded_file_names' not in st.session_state:
    st.session_state.uploaded_file_names = []
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'status' not in st.session_state:
    st.session_state.status = 'Not Started'
if 'photo_status' not in st.session_state:
    st.session_state.photo_status = 'Not Started'     
if 'selected_id_document' not in st.session_state:
    st.session_state.selected_id_document = None
if 'selected_id_document_name' not in st.session_state:
    st.session_state.selected_id_document_name = None
if 'analyze_button' not in st.session_state:
    st.session_state.analyze_button = False
if 'current_showing_profile_photo' not in st.session_state:
    st.session_state.current_showing_profile_photo = None    
if 'current_showing_id_document' not in st.session_state:
    st.session_state.current_showing_id_document = None
if 'current_showing_id_document_toggle' not in st.session_state:
    st.session_state.current_showing_id_document_toggle = False
if 'current_showing_profile_toggle' not in st.session_state:
    st.session_state.current_showing_profile_toggle = False

if 'profile_toggle_key' not in st.session_state:
    st.session_state.profile_toggle_key = str(uuid.uuid4())

if 'id_document_toggle_key' not in st.session_state:
    st.session_state.id_document_toggle_key = str(uuid.uuid4())


# Add custom CSS
add_custom_css()

st.title("Document Comparison")

# Layout: Two main columns
left_col, right_col = st.columns(2)

# Left Column - Customer Data and Photo
with left_col:
    # st.subheader("Customer ID Input")
    # customer_id_input = st.text_input("Enter Customer ID")
    # if st.button("Fetch Customer"):
    #     fetch_customer_data(customer_id_input)

    if st.session_state.customer_data:
        st.subheader("Customer Information")
        first_name = st.session_state.customer_data.get('first_name', '')
        middle_name = st.session_state.customer_data.get('middle_name', '')
        last_name = st.session_state.customer_data.get('last_name', '')
        full_name_str = f"{first_name} {middle_name} {last_name}"
        
        st.session_state.customer_data['full_name'] = full_name_str

        if 'photo' in st.session_state.customer_data:
            profile_bar_left_col, profile_bar_right_col = st.columns([0.6,0.4])
            with profile_bar_left_col:
                st.text(f"Full Name: {full_name_str}")        
            
            with profile_bar_right_col:
                on = st.toggle("Original / Analyzed Profile", st.session_state.current_showing_profile_toggle, key=st.session_state.profile_toggle_key)
            
            st.text(st.session_state.current_showing_profile_photo)
            if not on:
                if st.session_state.customer_data["photo_sas"] is not None:
                    st.image(st.session_state.customer_data["photo_sas"], use_column_width="auto")
            else:
                if st.session_state.current_showing_profile_photo is not None:
                    st.image(st.session_state.current_showing_profile_photo, use_column_width="auto")
        else:
            st.info("No photo available.")
    else:
        st.info("No customer data loaded.")

# Right Column - Document Viewer and Analysis
with right_col:
    st.subheader("Document Viewer")
    if st.session_state.uploaded_file_bytes:
        # Create a selectbox to select an image
        image_names = st.session_state.uploaded_file_names

        sub_bar_left_col, sub_bar_right_col = st.columns([0.6,0.4])

        with sub_bar_left_col:
            selected_image_name = st.selectbox("Select a document to view:", image_names)
            selected_image_index = image_names.index(selected_image_name)

        # Display the selected image
        selected_image_bytes = st.session_state.uploaded_file_bytes[selected_image_index]
        st.session_state.selected_id_document = selected_image_bytes
        st.session_state.selected_id_document_name = selected_image_name
        
        with sub_bar_right_col:
            on = st.toggle("Original / Analyzed", st.session_state.current_showing_id_document_toggle, key=st.session_state.id_document_toggle_key)
        # st.session_state.current_showing_id_document_toggle = on

        if not on:
            selected_image = Image.open(io.BytesIO(selected_image_bytes))
            st.image(selected_image, use_column_width="auto",  caption=selected_image_name)
        else:
            if st.session_state.current_showing_id_document is not None:
                st.image(st.session_state.current_showing_id_document, use_column_width="auto",  caption=selected_image_name)
    else:
        st.info("No documents uploaded. Please upload documents in the 'Upload Documents' page.")

    if st.button("Analyze Documents", disabled=st.session_state.analyze_button):
        # if st.button("Analyze Documents"):
        analyze_documents()

# Layout: Two main columns
view_left_col, view_right_col = st.columns(2)

with view_left_col:
    # Display Extracted Data and Logs
    st.subheader("Stored Data")
    json_data = copy.deepcopy(st.session_state.customer_data)
    for key in st.session_state.customer_data:
        if key.startswith('_'):
             del json_data[key]
        elif key in ['categoryId', 'photo_sas']:
            del json_data[key]
    st.json(json_data)

with view_right_col:
    # Display Extracted Data and Logs
    st.subheader("Extracted Data")
    st.json(st.session_state.extracted_data)

with st.sidebar:
    st.subheader("Status Indicator")
    
    status = str(st.session_state.status)    
    photo_status = str(st.session_state.photo_status)

    # Set background color for status and photo status (green for OK, red for NOT OK)
    status_bg_color = "green" if status.upper() == "OK" else "red"
    photo_status_bg_color = "green" if photo_status.upper() == "OK" else "red"

    # Style the Status and Photo Status with colored backgrounds and white text
    st.markdown(f"""
        <div style='padding: 5px; border-radius: 5px; background-color: {status_bg_color}; color: white;'>
            Data Status: {status.upper()}
        </div>
    """, unsafe_allow_html=True)
    st.text("")
    st.markdown(f"""
        <div style='padding: 5px; border-radius: 5px; background-color: {photo_status_bg_color}; color: white;'>
            Photo Status: {photo_status.upper()}
        </div>
    """, unsafe_allow_html=True)
    st.text("")
    st.subheader("Log Viewer")
    # logs = "\n".join(st.session_state.logs) if st.session_state.logs else "No discrepancies found."
    # st.text_area("Logs", logs, height=200)
    logs = st.session_state.logs  # Assuming logs is a list of dicts with 'message' and 'type' keys

    # Check if there are logs to display
    if logs:
        render_logs(logs)  # Example: Adding logs as success
    else:
        st.info("No analysis conducted.")

