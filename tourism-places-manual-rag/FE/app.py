import streamlit as st
import requests

# --- Page Configuration & API URL ---
st.set_page_config(page_title="Travel Advisor AI", page_icon="✈️")
FASTAPI_URL = "http://127.0.0.1:8000/ask"

# --- UI Components ---
st.title("✈️ Travel Advisor AI")
st.markdown("Ask for travel recommendations in **Bangkok, Chiang Mai, or Phuket**.")

user_question = st.text_input(
    "Enter your question:", 
    placeholder="e.g., 'อยากไปเที่ยวเชียงใหม่ ไปไหนดี'"
)

# --- Backend Logic ---
if st.button("Get Recommendation", type="primary"):
    with st.spinner("Finding the best spots for you..."):
        # Prepare and send the request to the backend
        payload = {"user_question": user_question}
        response = requests.post(FASTAPI_URL, json=payload)
        
        # Get the answer from the JSON response
        answer = response.json().get("answer", "Sorry, I couldn't get an answer.")
        
        # Display the result
        st.success("Here's my recommendation:")
        st.markdown(f"> {answer}")