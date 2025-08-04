import streamlit as st
import requests
import base64

st.title("Quotation Generator")

tab1, tab2 = st.tabs(["📤 Upload Image", "📸 Use Camera"])

image_file = None

with tab1:
    uploaded_file = st.file_uploader(
        "Upload a label image", 
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        image_file = uploaded_file

with tab2:
    camera_file = st.camera_input(
        "Take a photo of the label",
        label_visibility="collapsed"
    )
    if camera_file:
        image_file = camera_file

if image_file is not None:
    st.image(image_file, caption="Selected Image", use_column_width=True)

    if st.button("Generate Quotation PDF"):
        files = {"file": (image_file.name, image_file, image_file.type)}
        with st.spinner("Generating quotation..."):
            try:
                response = requests.post("http://127.0.0.1:8000/generate-quotation/", files=files)
                
                if response.status_code == 200:
                    pdf_bytes = response.content
                    st.success("Quotation PDF generated!")

                    st.download_button(
                        label="Download Quotation PDF",
                        data=pdf_bytes,
                        file_name="quotation.pdf",
                        mime="application/pdf"
                    )

                    # --- PDF Preview Section ---
                    st.markdown("### PDF Preview")
                    pdf_display = base64.b64encode(pdf_bytes).decode("utf-8")
                    pdf_embed = f'<iframe src="data:application/pdf;base64,{pdf_display}" width="100%" height="800px" type="application/pdf"></iframe>'
                    st.markdown(pdf_embed, unsafe_allow_html=True)

                else:
                    st.error(f"Failed to generate PDF. Server responded with status: {response.status_code}")
                    st.error(f"Server message: {response.text}")

            except requests.exceptions.ConnectionError as e:
                st.error("Connection Error: Could not connect to the backend service.")
                st.info("Please make sure your FastAPI server is running on http://127.0.0.1:8000")