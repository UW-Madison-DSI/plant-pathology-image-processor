import numpy as np
from PIL import Image
from PIL import ImageFilter
import json
import time
from leaflesiondetector.leaf import Leaf
import math

# from leaf import Leaf

# Read in settings from JSON file
with open("src/leaflesiondetector/settings.json") as f:
    settings = json.load(f)


def background_detector(leaf: Leaf):
    hsv_img = leaf.img.convert("HSV")
    hsv = np.array(hsv_img)
    value = hsv[:, :, 2] < 70

    if np.sum(value) > (hsv.shape[0] * hsv.shape[1] * 0.4):
        leaf.background_colour = "Black"
    else:
        leaf.background_colour = "White"


def append_reference_area_binary(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and saves a binary image with the reference area highlighted in white, to the object.
    """

    # Convert to HSV
    hsv_img = leaf.img.convert("HSV")
    hsv = np.array(hsv_img)

    # Create a mask of non green regions
    hues = hsv[:, :, 0] > settings[leaf.background_colour]["reference_area"]["min_hue"]
    saturation = (
        hsv[:, :, 1]
        > settings[leaf.background_colour]["reference_area"]["min_saturation"]
    )
    values = (
        hsv[:, :, 2] > settings[leaf.background_colour]["reference_area"]["min_value"]
    )
    new_img = Image.fromarray(np.uint8(hues * saturation * values * 255))

    # Remove noise
    new_img = new_img.filter(
        ImageFilter.MedianFilter(settings["median_blur_size"]["reference"])
    )

    # Save reference
    leaf.reference = settings["reference_radius"] / math.sqrt(
        np.sum(hues * saturation * values) / math.pi
    )

    leaf.reference_binary = new_img.convert("RGB").copy()

    return hues * saturation * values


def append_leaf_area_binary(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and saves a binary image with the leaf area highlighted in white, to the object.
    """

    # Convert to HSV
    hsv_img = leaf.img.convert("HSV")
    hsv = np.array(hsv_img)

    # Create a mask of green regions
    min_hues = hsv[:, :, 0] > settings[leaf.background_colour]["leaf_area"]["min_hue"]
    max_hues = hsv[:, :, 0] < settings[leaf.background_colour]["leaf_area"]["max_hue"]
    saturation = (
        hsv[:, :, 1] > settings[leaf.background_colour]["leaf_area"]["min_saturation"]
    )
    values = hsv[:, :, 2] > settings[leaf.background_colour]["leaf_area"]["min_value"]

    new_img = Image.fromarray(np.uint8(min_hues * max_hues * saturation * values * 255))

    # Remove noise
    new_img = new_img.filter(
        ImageFilter.MedianFilter(settings["median_blur_size"]["leaf"])
    )

    # Save leaf size to dataframe
    leaf.leaf_area = np.sum(min_hues * max_hues * saturation * values)

    leaf.leaf_binary = new_img.convert("RGB").copy()


def append_lesion_area_binary(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and saves a binary image with the non lesion area highlighted in white, to the object.
    i.e. the lesion area is black.
    """

    # Convert to HSV
    hsv_img = leaf.img.convert("HSV")
    hsv = np.array(hsv_img)

    # Create a mask of lesions
    min_hues = hsv[:, :, 0] > settings[leaf.background_colour]["lesion_area"]["min_hue"]
    max_hues = hsv[:, :, 0] < settings[leaf.background_colour]["lesion_area"]["max_hue"]
    saturation = (
        hsv[:, :, 1] > settings[leaf.background_colour]["lesion_area"]["min_saturation"]
    )
    values = hsv[:, :, 2] > leaf.minimum_lesion_area_value

    new_img = Image.fromarray(np.uint8(min_hues * max_hues * saturation * values * 255))

    # Remove noise
    new_img = new_img.filter(
        ImageFilter.MedianFilter(settings["median_blur_size"]["lesion"])
    )

    # Save lesion size and percentage
    leaf.lesion_area = leaf.leaf_area - np.sum(
        min_hues * max_hues * saturation * values
    )

    leaf.lesion_area_percentage = 100 * leaf.lesion_area / leaf.leaf_area
    leaf.lesion_area_cm2 = leaf.lesion_area * leaf.reference**2
    leaf.lesion_binary = new_img.convert("RGB").copy()


def process_image(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and calls the functions required to process the object.
    """

    start_time = time.time()
    if leaf.reference:
        append_reference_area_binary(leaf)
    append_leaf_area_binary(leaf)
    append_lesion_area_binary(leaf)
    leaf.run_time = time.time() - start_time
