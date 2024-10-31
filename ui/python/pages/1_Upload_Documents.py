# pages/1_Upload_Documents.py
import streamlit as st
from PIL import Image
import io
import sys
import os

# Ensure the utils module is accessible
sys.path.append(os.path.abspath('.'))
from ui_utils import upload_files, add_custom_css

st.set_page_config(page_title="Upload Documents", layout="wide")

# Initialize session state variables
if 'uploaded_file_bytes' not in st.session_state:
    st.session_state.uploaded_file_bytes = []
if 'uploaded_file_names' not in st.session_state:
    st.session_state.uploaded_file_names = []

# Add custom CSS
add_custom_css()

st.title("Upload ID Documents")

def uploaded_files():
    print("hi")

# Image Viewer with Dropdown Selectbox
st.subheader("Document Viewer")
if st.session_state.uploaded_file_bytes:
    # Create a selectbox to select an image
    image_names = st.session_state.uploaded_file_names
    selected_image_name = st.selectbox("Select an image to view:", image_names)

    selected_image_index = image_names.index(selected_image_name)

    # Display the selected image
    selected_image_bytes = st.session_state.uploaded_file_bytes[selected_image_index]
    selected_image = Image.open(io.BytesIO(selected_image_bytes))
    st.image(selected_image, use_column_width=False, width=600, caption=selected_image_name)
else:
    st.info("No documents uploaded.")

# Upload files
uploaded_files = st.file_uploader("Drag and drop files here", accept_multiple_files=True, label_visibility ="collapsed")
if uploaded_files:
    upload_files(uploaded_files)