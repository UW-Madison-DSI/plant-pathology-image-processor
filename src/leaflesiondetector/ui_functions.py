import streamlit as st
import lesion_detector
import os
import shutil
from PIL import Image
import time
from pathlib import Path
import pandas as pd

leaves = []

# paths used
input_folder_path = lesion_detector.settings["input_folder_path"]
output_folder_path = lesion_detector.settings["output_folder_path"]

def maintain_results() -> None:
    """
    This function maintains the results.
    """
    st.session_state["maintain"] = True

def download_results() -> None:
    """
    This function downloads the results of the image processing.
    """
    os.mkdir(output_folder_path)
    os.mkdir(output_folder_path + "/leaf_area_binaries/")
    os.mkdir(output_folder_path + "/lesion_area_binaries/")
    # Readying the data
    res_df = pd.DataFrame(columns=["Image", "Percentage area", "Run time (seconds)", "Intensity threshold"])
    for leaf in leaves:
        res_df = res_df.append(
            {
                "Image": leaf.name,
                "Percentage area": leaf.lesion_area_percentage,
                "Run time (seconds)": leaf.run_time,
                "Intensity threshold": leaf.intensity_threshold,
            },
            ignore_index=True,
        )
        leaf.leaf_binary.save(output_folder_path + "/leaf_area_binaries/" + f"{Path(leaf.name).stem}_leaf_area_binary{Path(leaf.name).suffix}")
        leaf.lesion_binary.save(output_folder_path + "/lesion_area_binaries/" + f"{Path(leaf.name).stem}_lesion_area_binary{Path(leaf.name).suffix}")
    res_df.to_csv(output_folder_path + "/results.csv", index=False)

    shutil.make_archive("results", "zip", output_folder_path)
    shutil.rmtree(output_folder_path)
    # Add a download button
    with open("results.zip", "rb") as fp:
        st.download_button(
            label="Download Results",
            data=fp,
            file_name="results.zip",
            mime="application/zip",
            on_click=maintain_results,
        )


def process_uploaded_images() -> None:
    """
    This function processes the uploaded images.
    """
    my_bar = st.progress(0)
    start_time = time.time()
    for i,leaf in enumerate(leaves):
        lesion_detector.process_image(leaf)
        my_bar.progress((i+1 )/ len(leaves))
    end_time = time.time()
    st.markdown(f"#### Total run time: {'%.2f'%(end_time - start_time)} seconds")
    my_bar.empty()


def display_results() -> None:
    """
    This function displays the results of the image processing.
    """

    for leaf in leaves:
        cols = st.columns(4)
        cols[0].image(leaf.img)
        cols[1].image(leaf.leaf_binary)
        cols[2].image(leaf.lesion_binary)
        cols[3].markdown(
            f"#### {leaf.name}\n ### {'%.2f'%leaf.lesion_area_percentage} %\n ### {'%.2f'%leaf.run_time} s"
        )
        cols[3].number_input('Adjust detection intensity range', min_value=0, max_value=255, value=leaf.intensity_threshold, step=5, key=leaf.name, on_change=update_result, args=[leaf])

def update_result(leaf) -> None:
    st.session_state["maintain"] = False
    leaf.intensity_threshold = st.session_state[leaf.name]
    lesion_detector.process_image(leaf)
    st.session_state["res_updated"] = True

def save_uploaded_files(uploaded_files: list) -> None:
    """
    This function saves the uploaded files to disk.
    """
    leaves.clear()

    for uploaded_file in uploaded_files:

        image_upload_status = st.empty()
        # Check if the image is usable
        try:
            Image.open(uploaded_file)
        except:
            image_upload_status.error(f"{uploaded_file.name} is not a valid image.")
            time.sleep(2) # For Streamlit UI purposes
            image_upload_status.empty()
            return

        # Save the file to disk
        with Image.open(uploaded_file) as img:
            leaves.append(lesion_detector.Leaf(uploaded_file.name, img.copy()))

    st.session_state["process"] = True
