import streamlit as st
from leaflesiondetector import ui_functions
from leaflesiondetector.leaf import LeafList
from leaflesiondetector import clustering
import time

st.title(":leaves: Leaf clustering tool")

if "cluster" not in st.session_state:
    st.session_state["cluster"] = False

if "cluster_leaves" not in st.session_state:
    st.session_state["cluster_leaves"] = LeafList()

upload_status = st.empty()
with st.form("my-form", clear_on_submit=True):
    uploaded_files = st.file_uploader(
        "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )
    submitted = st.form_submit_button("Process Images")
    if (len(uploaded_files) > 0) and submitted:
        st.session_state["cluster_leaves"] = LeafList()
        st.session_state["maintain"] = False
        ui_functions.save_uploaded_files(
            uploaded_files, st.session_state["cluster_leaves"].leaves
        )
        st.session_state["cluster"] = True
    elif (len(uploaded_files) == 0) and submitted:
        st.session_state["cluster"] = False  # For Streamlit UI behaviour
        upload_status.error("Please upload at least one image.")
        time.sleep(2)
        upload_status.empty()

if st.session_state["cluster"]:
    cluster_0 = []
    cluster_1 = []
    print("\n\nclustering\n\n")
    clustering.run(st.session_state["cluster_leaves"].leaves)
    print("\n\nclustered\n\n")
    for leaf in st.session_state["cluster_leaves"].leaves:
        if leaf.cluster == 0:
            cluster_0.append(leaf)
        else:    
            cluster_1.append(leaf)
    st.markdown("## Cluster 0")
    cols = st.columns(5)
    for i, leaf in enumerate(cluster_0):
        cols[i%5].image(leaf.img)
    st.markdown("## Cluster 1")
    cols = st.columns(5)
    for i, leaf in enumerate(cluster_1):
        cols[i%5].image(leaf.img)