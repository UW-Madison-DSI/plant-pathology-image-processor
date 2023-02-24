import streamlit as st
import ui_functions
import time

if "process" not in st.session_state:
    st.session_state["process"] = False

if "res_updated" not in st.session_state:
    st.session_state["res_updated"] = False

if "maintain" not in st.session_state:
    st.session_state["maintain"] = False

st.set_page_config(
        page_title="Leaf Lesion Detector",
        page_icon=":fallen_leaf:",
        layout='wide'
)
st.title(":fallen_leaf: Leaf Lesion Detector")
st.write(
    "This app will process images of plant leaves and calculate the percentage of leaf area affected by disease."
)

upload_status = st.empty()
with st.form("my-form", clear_on_submit=True):
    st.session_state["process"] = False
    uploaded_files = st.file_uploader(
        "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )
    submitted = st.form_submit_button("Process Images")
    if (len(uploaded_files) > 0) and submitted:
        ui_functions.save_uploaded_files(uploaded_files)
    elif (len(uploaded_files) == 0) and submitted:
        upload_status.error("Please upload at least one image.")
        time.sleep(2)
        upload_status.empty()

if st.session_state["res_updated"] == True:
    ui_functions.download_results()
    ui_functions.display_results()
    st.session_state["res_updated"] = False

if st.session_state["maintain"] == True:
    ui_functions.download_results()
    ui_functions.display_results()

if st.session_state["process"] == True:
    ui_functions.process_uploaded_images()
    ui_functions.download_results()
    ui_functions.display_results()
