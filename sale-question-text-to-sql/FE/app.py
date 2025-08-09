# streamlit_app.py

import streamlit as st
import requests
import os
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Text-to-SQL Interface",
    page_icon="🤖",
    layout="centered"
)

# --- Application Title and Description ---
st.title("📝 Questions to SQL Query")

# --- API Endpoint Configuration ---
FASTAPI_ENDPOINT = "http://127.0.0.1:8000/generate-and-save-query/"

# --- User Input ---
with st.form("query_form"):
    natural_language_query = st.text_area(
        "Enter your question here:",
        "Show me the total revenue for each product, sorted from highest to lowest."
    )
    submitted = st.form_submit_button("Generate Report")

# --- Processing Logic ---
if submitted:
    if not natural_language_query.strip():
        st.warning("Please enter a question before submitting.")
    else:
        with st.spinner("Processing your query... This may take a moment."):
            # Prepare the request payload
            payload = {"query": natural_language_query}
            
            # Send the request to the FastAPI backend
            response = requests.post(FASTAPI_ENDPOINT, json=payload)
            
            # Directly process the response, assuming it's always successful
            response_data = response.json()
            st.success("✅ Query processed successfully!")
            
            # Display the paths to the saved files
            st.subheader("Files Saved:")
            st.code(f"Excel Result: {response_data['files_saved']['excel_result']}", language="bash")
            st.code(f"SQL Log File: {response_data['files_saved']['sql_log']}", language="bash")
            
            st.info("You can find these files in your project directory.")