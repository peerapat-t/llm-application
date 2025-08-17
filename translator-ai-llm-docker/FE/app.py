# app.py (No changes required)

import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Language Translator",
    page_icon="🌐",
    layout="centered"
)

# --- Backend API URL ---
API_URL = "http://127.0.0.1:8000/translate"

# --- Streamlit UI ---
st.title("AI Language Translator")
st.caption("Powered by LangChain, OpenAI, and a FastAPI Backend") # Updated caption for context

# Initialize session state
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""

# Language data
languages = [
    "English", "Spanish", "French", "German", "Japanese", 
    "Korean", "Chinese (Simplified)", "Russian", "Arabic", "Thai", "Vietnamese"
]

target_lang = st.selectbox("Translate To", options=languages, index=1)
source_text = st.text_area("Enter text to translate", height=150, placeholder="Type here...")

# Translate button
if st.button("Translate"):
    if not source_text.strip():
        st.warning("Please enter some text to translate.")
    else:
        with st.spinner(f"Translating to {target_lang}..."):
            try:
                payload = {"text": source_text, "target_language": target_lang}
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.translated_text = result.get("translated_text", "")
                    st.success("Translation complete!")
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"Error: {error_detail} (Status code: {response.status_code})")
                    st.session_state.translated_text = ""

            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not connect to the backend service. Is it running?")
                st.session_state.translated_text = ""
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.session_state.translated_text = ""

# Display the translated text
st.text_area(
    "Translated text", 
    value=st.session_state.translated_text, 
    height=150, 
    disabled=True
)