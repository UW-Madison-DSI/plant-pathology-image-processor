# import packages
import numpy as np
from PIL import Image
from PIL import ImageFilter
import json
import time
from leaf import Leaf

# Read in settings from JSON file
with open("src/leaflesiondetector/settings.json") as f:
    settings = json.load(f)

def get_leaf_area_binary(leaf: Leaf) -> None:
    """
    This function takes an image as input and returns a binary image with the leaf area highlighted in white.
    """

    # Convert to HSV
    hsv_img = leaf.img.convert("HSV")
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
    leaf.leaf_area = np.sum(min_hues * max_hues * saturation * values)

    leaf.leaf_binary = new_img.convert("RGB").copy()


def get_lesion_area_binary(leaf: Leaf) -> None:
    """
    This function takes an image as input and returns a binary image with the non lesion area highlighted in white.
    i.e. the lesion area is black.
    """

    # Convert to HSV
    hsv_img = leaf.img.convert("HSV")
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

    # Save lesion size and percentage
    leaf.lesion_area = leaf.leaf_area - np.sum(min_hues * max_hues * saturation * values)
    leaf.lesion_area_percentage = 100*leaf.lesion_area/leaf.leaf_area

    leaf.lesion_binary =  new_img.convert("RGB").copy()

def set_custom_params(intensity_threshold: int) -> None:
    """
    This function takes a dictionary of custom parameters as input and updates the settings dictionary.
    """
    settings[settings['background_colour']]['lesion_area']['min_value'] = intensity_threshold

def reset_params() -> None:
    """
    This function resets the settings dictionary to the default values.
    """
    global settings
    with open("src/leaflesiondetector/settings.json") as f:
        settings = json.load(f)


def process_image(leaf: Leaf) -> None:
    """
    This function takes an image file name as input and saves the leaf area binary and lesion area binary to the output folder.
    """

    if leaf.intensity_threshold != settings[settings['background_colour']]['lesion_area']['min_value']:
        set_custom_params(leaf.intensity_threshold)

    start_time = time.time()
    get_leaf_area_binary(leaf)
    get_lesion_area_binary(leaf)
    leaf.run_time = time.time() - start_time

    reset_params()