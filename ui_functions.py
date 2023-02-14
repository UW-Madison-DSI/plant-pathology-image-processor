import streamlit as st
import lesion_detector
import os
import shutil

# paths used
input_folder_path = lesion_detector.settings["input_folder_path"]
output_folder_path = lesion_detector.settings["output_folder_path"]


def download_results() -> None:
    """
    This function downloads the results of the image processing.
    """
    # Readying the data
    lesion_detector.results_df.drop(["leaf area", "lesion area"], axis=1).to_csv(
        f"{output_folder_path}results.csv", index=False
    )
    shutil.make_archive("results", "zip", output_folder_path)
    # Add a download button
    with open("results.zip", "rb") as fp:
        st.download_button(
            label="Download Results",
            data=fp,
            file_name="results.zip",
            mime="application/zip",
        )


def process_uploaded_images() -> None:
    """
    This function processes the uploaded images.
    """
    dir = os.listdir(lesion_detector.settings["input_folder_path"])
    count = 0
    my_bar = st.progress(count)
    for image_name in dir:
        count += 1
        lesion_detector.process_image(image_name)
        my_bar.progress(count / len(dir))

    my_bar.empty()


def display_results() -> None:
    """
    This function displays the results of the image processing.
    """

    for image_name in os.listdir(lesion_detector.settings["input_folder_path"]):
        cols = st.columns(4)
        cols[0].image(f"{input_folder_path}/{image_name}")
        cols[1].image(
            f"{output_folder_path}/leaf_area_binaries/{image_name[:-4]}_leaf_area_binary.jpeg"
        )
        cols[2].image(
            f"{output_folder_path}/lesion_area_binaries/{image_name[:-4]}_lesion_area_binary.jpeg"
        )
        cols[3].markdown(
            f"#### {image_name}\n ### {'%.2f'%lesion_detector.results_df.loc[lesion_detector.results_df['image'] == image_name, 'percentage of leaf area'].values[0]} %"
        )


def save_uploaded_files(uploaded_files: list) -> None:
    """
    This function saves the uploaded files to disk.
    """

    # Input folder
    if os.path.exists(input_folder_path):
        shutil.rmtree(input_folder_path)
    os.makedirs(input_folder_path)

    # Output folder
    if os.path.exists(output_folder_path):
        shutil.rmtree(output_folder_path)
    os.makedirs(output_folder_path)
    os.makedirs(output_folder_path + "leaf_area_binaries/")
    os.makedirs(output_folder_path + "lesion_area_binaries/")

    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name

        # Save the file to disk
        save_path = os.path.join(
            lesion_detector.settings["input_folder_path"], file_name
        )
        with open(save_path, "wb") as f:
            f.write(file_bytes)

    st.session_state["process"] = True
