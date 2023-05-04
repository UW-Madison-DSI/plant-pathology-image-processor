import streamlit as st
from leaflesiondetector import ui_functions

# import ui_functions
import time
from leaflesiondetector.leaf import LeafList

# from leaf import LeafList

if "leaves" not in st.session_state:
    st.session_state["leaves"] = LeafList()

if "process" not in st.session_state:
    st.session_state["process"] = False

if "render" not in st.session_state:
    st.session_state["render"] = False

if "points" not in st.session_state:
    st.session_state["points"] = []

st.set_page_config(
    page_title="Leaf Lesion Detector", page_icon=":leaves:", layout="wide"
)

st.title(":leaves: Leaf Lesion Detector")
st.write(
    "This app will process images of plant leaves and calculate the percentage of leaf area affected by disease."
)

upload_status = st.empty()
with st.form("my-form", clear_on_submit=True):
    uploaded_files = st.file_uploader(
        "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )
    submitted = st.form_submit_button("Process Images")
    if (len(uploaded_files) > 0) and submitted:
        st.session_state["leaves"] = LeafList()
        st.session_state["maintain"] = False
        ui_functions.save_uploaded_files(
            uploaded_files, st.session_state["leaves"].leaves
        )
        st.session_state["process"] = True
    elif (len(uploaded_files) == 0) and submitted:
        st.session_state["process"] = False  # For Streamlit UI behaviour
        upload_status.error("Please upload at least one image.")
        time.sleep(2)
        upload_status.empty()

if st.session_state["process"]:
    ui_functions.process_uploaded_images(st.session_state["leaves"].leaves)

if st.session_state["render"]:
    message = st.empty()
    message.info("Loading images...")
    ui_functions.download_results(st.session_state["leaves"].leaves)
    ui_functions.display_results(st.session_state["leaves"].leaves)
    message.empty()
