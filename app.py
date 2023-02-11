import streamlit as st
import lesion_detector
import os
import glob

# Hide filename on UI
st.markdown('''
    <style>
        .uploadedFile {display: none}
    <style>''',
    unsafe_allow_html=True)

st.title(":fallen_leaf: Plant Pathology Image Processor")
st.write(
    "This app will process images of plant leaves and calculate the percentage of leaf area affected by disease."
)

# paths used
input_folder_path = lesion_detector.settings["input_folder_path"]
output_folder_path = lesion_detector.settings["output_folder_path"]

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

    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name

        # Save the file to disk
        save_path = os.path.join(lesion_detector.settings["input_folder_path"], file_name)
        with open(save_path, "wb") as f:
            f.write(file_bytes)

# Add a file uploader widget
uploaded_files = st.file_uploader("Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

file_upload_status = st.empty()

# Save the uploaded files to disk
if uploaded_files:
    save_uploaded_files(uploaded_files)
    file_upload_status.success("Files uploaded successfully!")

    if st.button("Process images"):
        file_upload_status.empty()
        st.text("")
        dir = os.listdir(lesion_detector.settings["input_folder_path"])
        count = 0
        my_bar = st.progress(count)
        for image_name in dir:
            count += 1
            lesion_detector.process_image(image_name)
            my_bar.progress(count / len(dir))

        my_bar.empty()

        # Add a download button
        data = bytes(lesion_detector.results_df.drop(["leaf area", "lesion area"], axis=1).to_csv(index=False), encoding='utf-8')
        st.download_button('Download CSV Results', data, file_name = "results.csv", mime = "text/csv")

        # display results
        display_results()

# # get settings
# lesion_detector.settings["background_colour"] = st.selectbox(
#     "What is the background colour?", ("black_velvet", "grey_background")
# )

    # # generate report
    # lesion_detector.generate_report(input_folder_path)
    # # display markdown report
    # with open("output.md", "r") as f:
    #     report = f.read()
    # st.markdown(report)