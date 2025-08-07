import streamlit as st
import requests
import json

st.set_page_config(
    page_title="HR Policy Chatbot",
    page_icon="🤖"
)

st.title("HR Policy Chatbot 🤖")
st.caption("This chatbot can answer questions about company policies, find items, and generate documents.")

BACKEND_URL = "http://localhost:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีค่ะ มีอะไรให้ช่วยสอบถามเกี่ยวกับบริษัทไหมคะ?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about leave, salary, or company info..."):
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    api_payload = {
        "prompt": prompt,
        "chat_history": st.session_state.messages[:-1]
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(BACKEND_URL, json=api_payload)
                response.raise_for_status() 

                assistant_response_data = response.json()
                assistant_response = assistant_response_data.get("response", "Sorry, something went wrong.")

            except requests.exceptions.RequestException as e:
                assistant_response = f"Could not connect to the backend: {e}"

        st.markdown(assistant_response)
        assistant_message = {"role": "assistant", "content": assistant_response}
        st.session_state.messages.append(assistant_message)