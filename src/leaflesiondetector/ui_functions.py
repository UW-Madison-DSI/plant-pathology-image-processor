import streamlit as st
from leaflesiondetector import lesion_detector
# import lesion_detector
import os
import shutil
from PIL import Image
import time
from pathlib import Path
from leaflesiondetector.leaf import Leaf
# from leaf import Leaf
import tempfile
import time
from streamlit_lottie import st_lottie_spinner
import requests
from leaflesiondetector import clustering


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def maintain_results() -> None:
    """
    This function maintains the results.
    """
    st.session_state["render"] = True


def download_results(leaves: list) -> None:
    """
    This function downloads the results of the image processing.
    """
    # Create a temporary directory to store the results
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.mkdir(tmpdirname + "/leaf_area_binaries/")
        os.mkdir(tmpdirname + "/lesion_area_binaries/")
        with open(f"{tmpdirname}/results.csv", "w") as f:
            f.write("Image,Percentage area,Run time (seconds),Intensity threshold\n")
            for leaf in leaves:
                f.write(
                    f"{leaf.name},{leaf.lesion_area_percentage},{leaf.run_time},{leaf.minimum_lesion_area_value}\n"
                )
                leaf.leaf_binary.save(
                    tmpdirname
                    + "/leaf_area_binaries/"
                    + f"{Path(leaf.name).stem}_leaf_area_binary{Path(leaf.name).suffix}"
                )
                leaf.lesion_binary.save(
                    tmpdirname
                    + "/lesion_area_binaries/"
                    + f"{Path(leaf.name).stem}_lesion_area_binary{Path(leaf.name).suffix}"
                )
        shutil.make_archive("results", "zip", tmpdirname)

    # Add a download button
    with open("results.zip", "rb") as fp:
        st.download_button(
            label="Download Results",
            data=fp,
            file_name="results.zip",
            mime="application/zip",
            on_click=maintain_results,
        )


def process_uploaded_images(leaves: list) -> None:
    """
    This function processes the uploaded images.
    """
    my_bar = st.progress(0, "Running...")
    start_time = time.time()
    with st_lottie_spinner(
        load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_XIIxSb.json"),
        key="download",
        speed=0.5,
        loop=True,
    ):
        for i, leaf in enumerate(leaves):
            leaf.minimum_lesion_area_value = 120
            my_bar.progress((i + 1) / len(leaves), f"{leaf.name}...")
            lesion_detector.process_image(leaf)
            if leaf.lesion_area_percentage > 7:
                leaf.minimum_lesion_area_value = 140
                lesion_detector.process_image(leaf)
        end_time = time.time()
    st.markdown(f"#### Total run time: {'%.2f'%(end_time - start_time)} seconds")
    my_bar.empty()

    st.session_state["process"] = False
    st.session_state["render"] = True


def display_results(leaves: list) -> None:
    """
    This function displays the results of the image processing.
    """

    for leaf in leaves:
        cols = st.columns(4)
        cols[0].image(leaf.img)
        cols[1].image(leaf.leaf_binary)
        cols[2].image(leaf.lesion_binary)
        cols[3].markdown(
            f"#### {leaf.name}\n ### {'%.2f'%leaf.lesion_area_percentage} %\n ### {'%.2f'%leaf.run_time} s \n ### Cluster: {leaf.cluster}"
        )
        with cols[3].expander("Settings"):
            st.number_input(
                "Adjust detection intensity",
                min_value=0,
                max_value=255,
                value=leaf.minimum_lesion_area_value,
                step=5,
                key=leaf.key,
                on_change=update_result,
                args=[leaf],
            )
            st.warning("To maintain consistency across a set of calculations using the same threshold for all images is recommended.")


def update_result(leaf) -> None:
    leaf.minimum_lesion_area_value = st.session_state[leaf.key]
    lesion_detector.process_image(leaf)


def save_uploaded_files(uploaded_files: list, leaves: list) -> None:
    """
    This function saves the uploaded files to disk.
    """

    for uploaded_file in uploaded_files:

        image_upload_status = st.empty()
        # Check if the image is usable
        try:
            Image.open(uploaded_file)
        except:
            image_upload_status.error(f"{uploaded_file.name} is not a valid image.")
            time.sleep(2)  # For Streamlit UI purposes
            image_upload_status.empty()
            return

        # Save the file to disk
        with Image.open(uploaded_file) as img:
            leaves.append(
                Leaf(
                    f"{uploaded_file.name}_{int(time.time_ns())}",
                    uploaded_file.name,
                    img.copy(),
                )
            )
