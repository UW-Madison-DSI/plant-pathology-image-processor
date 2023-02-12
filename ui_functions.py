import streamlit as st
import lesion_detector
import os
import shutil

# paths used
input_folder_path = lesion_detector.settings["input_folder_path"]
output_folder_path = lesion_detector.settings["output_folder_path"]

# if 'process' not in st.session_state:
#     st.session_state['process'] = False

def download_buttons() -> None:
    '''
    This function downloads the results of the image processing.
    '''
    # Readying the data
    csv_data = bytes(lesion_detector.results_df.drop(["leaf area", "lesion area"], axis=1).to_csv(index=False), encoding='utf-8')
    shutil.make_archive('binaries', 'zip', output_folder_path)
    # Add a download button
    download_cols = st.columns(2)
    download_cols[0].download_button('Download CSV Results', csv_data, file_name = "results.csv", mime = "text/csv")
    with open("binaries.zip", "rb") as fp:
        download_cols[1].download_button(
            label="Download Binaries",
            data=fp,
            file_name="binaries.zip",
            mime="application/zip"
        )

def process_uploaded_images() -> None:
    '''
    This function processes the uploaded images.
    '''
    dir = os.listdir(lesion_detector.settings["input_folder_path"])
    count = 0
    my_bar = st.progress(count)
    for image_name in dir:
        count += 1
        lesion_detector.process_image(image_name)
        my_bar.progress(count / len(dir))

    my_bar.empty()

def display_results() -> None:
    '''
    This function displays the results of the image processing.
    '''

    for image_name in os.listdir(lesion_detector.settings["input_folder_path"]):
        cols = st.columns(4)
        cols[0].image(f"{input_folder_path}/{image_name}")
        cols[1].image(f"{output_folder_path}/leaf_area_binaries/{image_name[:-4]}_leaf_area_binary.jpeg")
        cols[2].image(f"{output_folder_path}/lesion_area_binaries/{image_name[:-4]}_lesion_area_binary.jpeg")
        cols[3].markdown(f"#### {image_name}\n ### {'%.2f'%lesion_detector.results_df.loc[lesion_detector.results_df['image'] == image_name, 'percentage of leaf area'].values[0]} %")

def save_uploaded_files(uploaded_files: list) -> None:
    '''
    This function saves the uploaded files to disk.
    '''
    
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
        save_path = os.path.join(lesion_detector.settings["input_folder_path"], file_name)
        with open(save_path, "wb") as f:
            f.write(file_bytes)

    st.session_state['process'] = True