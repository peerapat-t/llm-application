import streamlit as st
import requests
import base64
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Lead Generation Assistant",
    page_icon="🤖",
    layout="centered"
)

# --- UI Elements ---
st.title("🤖 Lead Generation Assistant")
st.markdown("Enter your request in plain English to generate a targeted customer list. For example: `I want a list of lead customers who are over 40 and purchased a Laptop.`")

# --- User Input ---
with st.form("query_form"):
    user_query = st.text_area("Your Request:", height=100)
    submit_button = st.form_submit_button("Generate Report")

# --- Backend Interaction ---
if submit_button and user_query:
    API_URL = "http://127.0.0.1:8000/generate_report"
    
    with st.spinner("Processing your request... Please wait."):
        try:
            # Send the request to the FastAPI backend
            response = requests.post(API_URL, json={"query": user_query})
            
            # --- Handle the Response ---
            if response.status_code == 200:
                data = response.json()
                message = data.get("message")
                conditions = data.get("conditions")
                sql_query = data.get("sql")
                excel_b64 = data.get("excel_file_b64")

                # 1. Display Status
                if message:
                    st.info(f"**Status:** {message}")

                # 2. Display Condition List
                if conditions:
                    with st.expander("✅ Extracted Conditions", expanded=True):
                        for condition in conditions:
                            st.write(f"- {condition}")

                # 3. Display SQL Query
                if sql_query:
                    with st.expander("🔍 Generated SQL Query"):
                        st.code(sql_query, language="sql")

                # 4. Display Download Button for Excel file
                if excel_b64:
                    st.success("Your report is ready for download.")
                    # Decode the base64 string to bytes
                    excel_bytes = base64.b64decode(excel_b64)
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_bytes,
                        file_name="lead_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            else:
                # Display an error message if the request failed
                st.error(f"Error: Received status code {response.status_code}")
                st.json(response.json())

        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend. Please ensure the FastAPI server is running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")