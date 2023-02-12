import streamlit as st
import ui_functions

if "process" not in st.session_state:
    st.session_state["process"] = False

st.title(":fallen_leaf: Plant Pathology Image Processor")
st.write(
    "This app will process images of plant leaves and calculate the percentage of leaf area affected by disease."
)

with st.form("my-form", clear_on_submit=True):
    uploaded_files = st.file_uploader(
        "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )
    submitted = st.form_submit_button("Process Images")
    if submitted and uploaded_files is not None:
        ui_functions.save_uploaded_files(uploaded_files)

if st.session_state["process"] == True:
    ui_functions.process_uploaded_images()
    ui_functions.download_buttons()
    ui_functions.display_results()
