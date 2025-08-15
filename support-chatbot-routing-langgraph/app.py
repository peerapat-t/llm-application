# streamlit_app.py

import streamlit as st
import requests
import uuid

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"  # URL of your FastAPI backend

st.title("DOGBRAIN666 Product Support 🐾")
st.caption("Your friendly neighborhood chatbot (with a separate backend!)")

# --- Session State Management ---
# Set up a unique thread ID for the user session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Functions ---
def get_chat_history():
    """Fetches chat history from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/history/{st.session_state.thread_id}")
        response.raise_for_status()
        messages = response.json()
        # Convert message dicts to AIMessage/HumanMessage objects if needed,
        # but for display, dicts are fine.
        st.session_state.messages = messages
    except requests.exceptions.RequestException as e:
        # Handle cases where the backend is not running
        st.error(f"Could not connect to the backend: {e}")
        st.session_state.messages = [{
            "type": "ai",
            "content": "Error: Could not retrieve chat history. Is the backend server running?"
        }]

def send_message(message: str):
    """Sends a message to the backend and updates the chat history."""
    # Add user message to session state
    st.session_state.messages.append({"type": "human", "content": message})
    
    # Display the user message
    with st.chat_message("user"):
        st.markdown(message)
        
    # Send message to backend and get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/invoke",
                    json={"message": message, "thread_id": st.session_state.thread_id}
                )
                response.raise_for_status()
                bot_response = response.json()["response"]
                st.markdown(bot_response)
                # Add assistant response to session state
                st.session_state.messages.append({"type": "ai", "content": bot_response})
            except requests.exceptions.RequestException as e:
                error_message = f"Error communicating with the backend: {e}"
                st.error(error_message)
                st.session_state.messages.append({"type": "ai", "content": error_message})


# --- Main App Logic ---

# Load history only once at the start
if not st.session_state.messages:
    get_chat_history()

# Display chat messages from history
for message in st.session_state.messages:
    role = "assistant" if message["type"] == "ai" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me about our products!"):
    send_message(prompt)