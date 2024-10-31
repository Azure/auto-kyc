# pages/2_View_Edit_Customer_Data.py
import streamlit as st
import json
import sys
import os
import requests

# Ensure the utils module is accessible
sys.path.append(os.path.abspath('.'))
from ui_utils import fetch_customer_data, update_customer_data, add_custom_css

st.set_page_config(page_title="View/Edit Customer Data", layout="wide")

# Initialize session state variables
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {}
if 'customer_id' not in st.session_state:
    st.session_state.customer_id = None
if 'customer_list' not in st.session_state:
    st.session_state.customer_list = []
if 'selected_customer_id' not in st.session_state:
    st.session_state.selected_customer_id = None


# Add custom CSS
add_custom_css()

st.title("View and Edit Customer Records")

# Display and edit customer data
if st.session_state.customer_data:
    st.subheader("Customer Data (Editable)")
    customer_data_json = st.text_area(
        "Edit Customer Data",
        json.dumps(st.session_state.customer_data, indent=2),
        height=300
    )
    try:
        st.session_state.customer_data = json.loads(customer_data_json)
    except json.JSONDecodeError:
        st.error("Invalid JSON format.")

    if st.button("Update DB"):
        update_customer_data()
else:
    st.info("No customer data loaded.")


# Fetch the list of customers when the page loads
def fetch_customer_list():
    response = requests.get('http://localhost:8000/api/customers')
    if response.status_code == 200:
        st.session_state.customer_list = response.json()
    else:
        st.error("Failed to fetch customer list.")
        st.session_state.customer_list = []

# Only fetch the customer list once per session
if 'customer_list_fetched' not in st.session_state:
    fetch_customer_list()
    st.session_state.customer_list_fetched = True

st.subheader("Select a Customer")
if st.session_state.customer_list:
    # Create a dictionary mapping customer display names to customer IDs
    if st.session_state.selected_customer_id is None: 
        default_index = 0
    else:
        for i, cust in enumerate(st.session_state.customer_list):
            if cust['customer_id'] == st.session_state.selected_customer_id:
                default_index = i
                break

    customer_options = {
        f"{cust['customer_id']} - {cust.get('name', '')}": cust['customer_id']
        for cust in st.session_state.customer_list
    }
    selected_customer_display = st.selectbox("Select a customer:", list(customer_options.keys()), index=default_index)
    selected_customer_id = customer_options[selected_customer_display]
    
    if st.button("Load Selected Customer"):
        st.session_state.selected_customer_id = selected_customer_id
        fetch_customer_data(selected_customer_id)
else:
    st.info("No customers available.")

st.subheader("Or Enter Customer ID")
customer_id_input = st.text_input("Enter Customer ID")
if st.button("Fetch Customer"):
    st.session_state.selected_customer_id = customer_id_input
    fetch_customer_data(customer_id_input)


