# app.py
import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Furniture Bot",
    page_icon="🛋️",
    layout="centered"
)

# --- UI Setup ---
st.title("🛋️ Furniture Support Chatbot")
st.caption("Your AI-powered assistant for product details, pricing, and warranty information.")

# --- Session State Initialization ---
# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you with our furniture products today?"}
    ]

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Response Handling ---
# Get user input from the chat input box
if prompt := st.chat_input("Ask a question about our products..."):
    # Add user's message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Backend Communication ---
    # Display an empty assistant message container while waiting for the response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # URL of your FastAPI endpoint
            api_url = "http://127.0.0.1:8000/chat"
            
            # Create the request payload
            payload = {"query": prompt}
            
            # Use requests to stream the response from the FastAPI backend
            with requests.post(api_url, json=payload, stream=True) as response:
                response.raise_for_status()  # Raise an exception for bad status codes
                
                for line in response.iter_lines():
                    if line:
                        # SSE format is "data: {content}"
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            content = decoded_line[len('data: '):]
                            full_response += content
                            message_placeholder.markdown(full_response + "▌") # Add a blinking cursor effect
            
            message_placeholder.markdown(full_response)
            
        except requests.exceptions.RequestException as e:
            full_response = f"**Error:** Could not connect to the chatbot service. Please make sure the FastAPI server is running. \n\n*Details: {e}*"
            message_placeholder.error(full_response)
            
    # Add the final assistant response to the session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# To run this app, save it as app.py and run:
# streamlit run app.py