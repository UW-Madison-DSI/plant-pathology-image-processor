# import packages
import pandas as pd
import numpy as np
import os
from PIL import Image
from PIL import ImageFilter
import json
import time
from pathlib import Path

# File name and extension of the current image
filename = None
file_extension = None

# Using a Dataframe to save data to a CSV
results_df = pd.DataFrame(
    columns=["Image", "Leaf area", "Lesion area", "Percentage of leaf area", "Run time (seconds)"]
)

# Read in settings from JSON file
with open("src/leaflesiondetector/settings.json") as f:
    settings = json.load(f)


def get_leaf_area_binary(img: Image) -> Image:
    """
    This function takes an image as input and returns a binary image with the leaf area highlighted in white.
    """

    # Convert to HSV
    hsv_img = img.convert("HSV")
    hsv = np.array(hsv_img)

    # Create a mask of green regions
    min_hues = (
        hsv[:, :, 0] > settings[settings["background_colour"]]["leaf_area"]["min_hue"]
    )
    max_hues = (
        hsv[:, :, 0] < settings[settings["background_colour"]]["leaf_area"]["max_hue"]
    )
    saturation = (
        hsv[:, :, 1]
        > settings[settings["background_colour"]]["leaf_area"]["min_saturation"]
    )
    values = (
        hsv[:, :, 2] > settings[settings["background_colour"]]["leaf_area"]["min_value"]
    )
    new_img = Image.fromarray(np.uint8(min_hues * max_hues * saturation * values * 255))

    # Remove noise
    new_img = new_img.filter(ImageFilter.MedianFilter(5))

    # Save leaf size to dataframe
    results_df.loc[results_df["image"] == filename, "leaf area"] = np.sum(
        min_hues * max_hues * saturation * values
    )

    return new_img.convert("RGB")


def get_lesion_area_binary(img: Image) -> Image:
    """
    This function takes an image as input and returns a binary image with the non lesion area highlighted in white.
    i.e. the lesion area is black.
    """

    # Convert to HSV
    hsv_img = img.convert("HSV")
    hsv = np.array(hsv_img)

    # Create a mask of lesions
    min_hues = (
        hsv[:, :, 0] > settings[settings["background_colour"]]["lesion_area"]["min_hue"]
    )
    max_hues = (
        hsv[:, :, 0] < settings[settings["background_colour"]]["lesion_area"]["max_hue"]
    )
    saturation = (
        hsv[:, :, 1]
        > settings[settings["background_colour"]]["lesion_area"]["min_saturation"]
    )
    values = (
        hsv[:, :, 2]
        > settings[settings["background_colour"]]["lesion_area"]["min_value"]
    )
    new_img = Image.fromarray(np.uint8(min_hues * max_hues * saturation * values * 255))

    # Remove noise
    new_img = new_img.filter(ImageFilter.MedianFilter(5))

    # Save lesion size to dataframe
    results_df.loc[results_df["image"] == filename, "lesion area"] = results_df.loc[
        results_df["image"] == filename, "leaf area"
    ] - np.sum(min_hues * max_hues * saturation * values)
    results_df.loc[results_df["image"] == filename, "percentage of leaf area"] = (
        100
        * results_df.loc[results_df["image"] == filename, "lesion area"]
        / results_df.loc[results_df["image"] == filename, "leaf area"]
    )

    return new_img.convert("RGB")


def process_image(image_file_name: str) -> None:
    """
    This function takes an image file name as input and saves the leaf area binary and lesion area binary to the output folder.
    """

    global results_df

    global filename
    global file_extension 
    image_file = Path(image_file_name)
    filename, file_extension = image_file.stem, image_file.suffix

    results_df = pd.concat(
        [
            results_df,
            pd.DataFrame(
                {
                    "image": [filename],
                    "leaf area": [0],
                    "lesion area": [0],
                    "percentage of leaf area": [0],
                }
            ),
        ]
    )

    start_time = time.time()
    with Image.open(Path(settings["input_folder_path"]) / image_file.name) as img:
        get_leaf_area_binary(img).save(
            settings["output_folder_path"]
            + "/leaf_area_binaries/"
            + f"{filename}_leaf_area_binary.jpeg"
        )
        get_lesion_area_binary(img).save(
            settings["output_folder_path"]
            + "/lesion_area_binaries/"
            + f"{filename}_lesion_area_binary.jpeg"
        )
    run_time = time.time() - start_time

    results_df.loc[results_df["image"] == filename, "run time"] = run_time
