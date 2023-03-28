import streamlit as st
from leaflesiondetector import ui_functions
from leaflesiondetector.leaf import LeafList
from leaflesiondetector import clustering
import time
from streamlit_lottie import st_lottie_spinner
from collections import defaultdict

st.set_page_config(
    page_title="Leaf Lesion Detector", page_icon=":leaves:", layout="wide"
)

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
    num_clusters = st.number_input("Number of clusters", min_value=2, max_value=10, value=2)
    submitted = st.form_submit_button("Process Images")
    if (len(uploaded_files) >= num_clusters) and submitted:
        st.session_state["cluster_leaves"] = LeafList()
        st.session_state["maintain"] = False
        ui_functions.save_uploaded_files(
            uploaded_files, st.session_state["cluster_leaves"].leaves
        )
        st.session_state["cluster"] = True
    elif (len(uploaded_files) == 0) and submitted:
        st.session_state["cluster"] = False
        upload_status.error("Please upload at least one image.")
        time.sleep(2) # For Streamlit UI behaviour
        upload_status.empty()
    elif (len(uploaded_files) < num_clusters) and submitted:
        st.session_state["cluster"] = False
        upload_status.error("Number of images should be greater than or equal to number of clusters.")
        time.sleep(2) # For Streamlit UI behaviour

if st.session_state["cluster"]:
    st.markdown(f"## Clustering into {num_clusters} clusters")
    with st_lottie_spinner(
        ui_functions.load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_XIIxSb.json"),
        key="download",
        speed=0.5,
        loop=True,
    ):
        clusters = defaultdict(list)
        print("\n\nclustering\n\n")
        clustering.run(st.session_state["cluster_leaves"].leaves, num_clusters)
        print("\n\nclustered\n\n")
        for leaf in st.session_state["cluster_leaves"].leaves:
            clusters[leaf.cluster].append(leaf)
        for cluster in clusters:
            st.markdown(f"## Cluster {cluster}")
            cols = st.columns(4)
            for i, leaf in enumerate(clusters[cluster]):
                cols[i%4].markdown(f"#### {leaf.name}")
                cols[i%4].image(leaf.img)