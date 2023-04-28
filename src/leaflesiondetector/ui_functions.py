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
import json
import csv
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import ImageDraw
import numpy as np
import plotly.express as px

# Read in settings from JSON file
with open("src/leaflesiondetector/settings.json") as f:
    settings = json.load(f)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def apply_changes(leaf: Leaf, point: tuple[int, int]) -> None:
    """
    This function applies the changes to the image.
    """
    # Image modification
    draw = ImageDraw.Draw(leaf.modified_image)
    class_value = leaf.labeled_pixels[point[1]][point[0]]
    if class_value in [0, 1]:
        return
    x, y = np.where(leaf.labeled_pixels == class_value)
    draw.point(list(zip(y, x)), fill=(0, 0, 0))

    # Values modification
    leaf.lesion_area -= leaf.lesion_class_map[class_value]
    leaf.lesion_class_map[class_value] = 0
    leaf.lesion_area_percentage = 100 * leaf.lesion_area / leaf.leaf_area
    if leaf.reference:
        leaf.lesion_area_mm2 = (
            leaf.lesion_area * settings["reference_area_mm"]
        ) / leaf.reference_area
    leaf.num_lesions -= 1
    leaf.average_lesion_size = leaf.lesion_area / leaf.num_lesions
    leaf.max_lesion_size = max(sorted(leaf.lesion_class_map.values())[:-2])
    leaf.min_lesion_size = min(sorted(leaf.lesion_class_map.values())[:-2])


def get_ellipse_coords(point: tuple[int, int]) -> tuple[int, int, int, int]:
    center = point
    radius = 10
    return (
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius,
    )


def maintain_results() -> None:
    """
    This function maintains the results.
    """
    st.session_state["render"] = True


def write_csv(file: str, leaves: list) -> None:
    """
    This function writes the results of the image processing to a CSV file.
    """
    with open(file, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Image",
                "Percentage area",
                "Percentage area mm2",
                "Run time (seconds)",
                "Intensity threshold",
            ],
        )
        writer.writeheader()
        for leaf in leaves:
            writer.writerow(
                {
                    "Image": leaf.name,
                    "Percentage area": leaf.lesion_area_percentage,
                    "Percentage area mm2": leaf.lesion_area_mm2,
                    "Run time (seconds)": leaf.run_time,
                    "Intensity threshold": leaf.minimum_lesion_area_value,
                }
            )


def download_results(leaves: list) -> None:
    """
    This function downloads the results of the image processing.
    """
    # Create a temporary directory to store the results
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.mkdir(tmpdirname + "/leaf_area_binaries/")
        os.mkdir(tmpdirname + "/lesion_area_binaries/")
        os.mkdir(tmpdirname + "/reference_binaries/")
        write_csv(f"{tmpdirname}/results.csv", leaves)
        for leaf in leaves:
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
            if leaf.reference:
                leaf.reference_binary.save(
                    tmpdirname
                    + "/reference_binaries/"
                    + f"{Path(leaf.name).stem}_reference_binary{Path(leaf.name).suffix}"
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
        key="leaf_loader",
        speed=0.5,
        loop=True,
    ):
        for i, leaf in enumerate(leaves):
            lesion_detector.background_detector(leaf)
            leaf.minimum_lesion_area_value = settings[leaf.background_colour][
                "low_intensity"
            ]
            my_bar.progress((i + 1) / len(leaves), f"{leaf.name}...")
            lesion_detector.process_image(leaf)
            if leaf.lesion_area_percentage > 8.5:
                leaf.minimum_lesion_area_value = settings[leaf.background_colour][
                    "high_intensity"
                ]
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
        num_cols = 2
        cols = st.columns(num_cols)
        with cols[0]:
            # Draw an ellipse at each coordinate in points
            for point in st.session_state["points"]:
                apply_changes(leaf, point)
            value = streamlit_image_coordinates(
                leaf.modified_image,
                width=leaf.modified_image.size[0] / 4,
                height=leaf.modified_image.size[1] / 4,
            )
            if value is not None:
                point = value["x"] * 4, value["y"] * 4
                if point not in st.session_state["points"]:
                    st.session_state["points"].append(point)
                    st.experimental_rerun()

        cols[1].markdown(
            f"""
            #### {leaf.name}\n 
            ### {'%.2f'%leaf.lesion_area_percentage} %\n 
            ### {'%.2f'%leaf.lesion_area_mm2+" mm²" if leaf.reference else ""}
            #### {leaf.num_lesions} lesions
            **Average lesion size:** {'%.2f'%leaf.average_lesion_size} {"mm²" if leaf.reference else "pixels"}\n
            **Maximum lesion size:** {'%.2f'%leaf.max_lesion_size} {"mm²" if leaf.reference else "pixels"}\n
            **Minimum lesion size:** {'%.2f'%leaf.min_lesion_size} {"mm²" if leaf.reference else "pixels"}\n
            {'%.2f'%leaf.run_time} seconds"""
        )

        if leaf.reference:
            cols[1].plotly_chart(
                px.histogram(
                    list(leaf.lesion_class_map.values()),
                    log_y=True,
                    labels={"0": "test"},
                ),
                use_container_width=True,
            )
        else:
            cols[1].plotly_chart(
                px.histogram(list(leaf.lesion_class_map.values()), log_y=True),
                use_container_width=True,
            )

        with cols[1].expander("Settings"):
            st.number_input(
                "Adjust detection intensity",
                min_value=0,
                max_value=255,
                value=leaf.minimum_lesion_area_value,
                step=5,
                key=leaf.key + "_intensity",
                on_change=update_result,
                args=[leaf],
            )
            st.radio(
                "Background colour",
                ["Black", "White"],
                index=["Black", "White"].index(leaf.background_colour),
                key=leaf.key + "_colour",
                on_change=update_result,
                args=[leaf],
            )


def update_result(leaf) -> None:
    leaf.minimum_lesion_area_value = st.session_state[leaf.key + "_intensity"]
    leaf.background_colour = st.session_state[leaf.key + "_colour"]
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
