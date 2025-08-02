import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="PDF Summarizer",
    page_icon="📄",
    layout="centered"
)

# --- App Title and Description ---
st.title("📄 PDF Document Summarizer")
st.markdown("""
Upload a PDF document, and this app will generate a concise, bullet-point summary for you. 
""")

# --- Backend URL ---
BACKEND_URL = "http://127.0.0.1:8000/summarize/"

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose a PDF file to summarize.", 
    type="pdf"
)

# --- Summarization Trigger and Display ---
if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    if st.button("Summarize Document", key="summarize_button"):
        # Display a spinner while processing
        with st.spinner("Summarizing your document... This may take a moment."):
            try:
                # Prepare the file for the POST request
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                
                # Send the request to the FastAPI backend
                response = requests.post(BACKEND_URL, files=files, timeout=300) # 5-minute timeout
                
                # Check the response from the backend
                response.raise_for_status() # Raises an exception for 4XX/5XX errors
                
                summary_data = response.json()
                
                # Display the summary
                st.header("Summary")
                st.markdown(summary_data.get("summary", "No summary was returned."))

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while communicating with the backend: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")