import streamlit as st
import requests
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="HR Policy Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Title and Description ---
st.title("HR Policy Chatbot 🤖")

# --- Sidebar for Controls ---
with st.sidebar:
    st.title("Controls")
    if st.button("Reset Chat"):
        # Clear chat history and session ID
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun() # Rerun the app to reflect the changes immediately

# --- Session State Initialization ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Backend API URL ---
BACKEND_URL = "http://localhost:8000/chat"

# --- Display Chat History ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input Handling ---
if prompt := st.chat_input("Ask a question about HR policies..."):
    # Add user's message to the chat history and display it
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Interact with the Backend ---
    try:
        # Prepare the data to be sent to the FastAPI backend
        payload = {
            "question": prompt,
            "session_id": st.session_state.session_id
        }

        # Display a spinner while waiting for the response
        with st.spinner("Thinking..."):
            # Send the request to the backend
            response = requests.post(BACKEND_URL, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            # Extract the answer from the JSON response
            result = response.json()
            answer = result.get("answer", "Sorry, I couldn't get a response.")

        # Add the assistant's response to the chat history and display it
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

    except requests.exceptions.RequestException as e:
        # Handle connection errors or other request-related issues
        st.error(f"Could not connect to the chatbot service: {e}")
    except Exception as e:
        # Handle other potential errors
        st.error(f"An error occurred: {e}")