import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from PIL import ImageFilter
import json
import time
from leaflesiondetector.leaf import Leaf
from skimage import measure
import matplotlib.colors as mcolors

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

    # Create a mask of pink regions
    hues = hsv[:, :, 0] > settings[leaf.background_colour]["reference_area"]["min_hue"]
    saturation = (
        hsv[:, :, 1]
        > settings[leaf.background_colour]["reference_area"]["min_saturation"]
    )
    values = (
        hsv[:, :, 2] > settings[leaf.background_colour]["reference_area"]["min_value"]
    )

    if np.sum(hues * saturation * values) > (hsv.shape[0] * hsv.shape[1] * 0.01):
        leaf.reference = True
    else:
        leaf.reference = False
        return

    new_img = Image.fromarray(np.uint8(hues * saturation * values * 255))

    # Remove noise
    new_img = new_img.filter(
        ImageFilter.MedianFilter(settings["median_blur_size"]["reference"])
    )

    # Save reference
    leaf.reference_area = np.sum(hues * saturation * values)

    leaf.reference_binary = new_img.convert("RGB").copy()

    pixels = leaf.modified_image.load()
    reference_mask = leaf.reference_binary.load()
    for i in range(leaf.img.size[0]):  # for every pixel:
        for j in range(leaf.img.size[1]):
            if reference_mask[i, j] == (255, 255, 255):  # if white in reference mask
                pixels[i, j] = (0, 255, 0)  # change to pink


# def append_leaf_area_binary(leaf: Leaf) -> None:
#     """
#     Takes a leaf object as input and saves a binary image with the leaf area highlighted in white, to the object.
#     """

#     # Convert to HSV
#     hsv_img = leaf.img.convert("HSV")
#     hsv = np.array(hsv_img)

#     # Create a mask of green regions
#     min_hues = hsv[:, :, 0] > settings[leaf.background_colour]["leaf_area"]["min_hue"]
#     max_hues = hsv[:, :, 0] < settings[leaf.background_colour]["leaf_area"]["max_hue"]
#     saturation = (
#         hsv[:, :, 1] > settings[leaf.background_colour]["leaf_area"]["min_saturation"]
#     )
#     values = hsv[:, :, 2] > settings[leaf.background_colour]["leaf_area"]["min_value"]

#     new_img = Image.fromarray(np.uint8(min_hues * max_hues * saturation * values * 255))

#     # Remove noise
#     new_img = new_img.filter(
#         ImageFilter.MedianFilter(settings["median_blur_size"]["leaf"])
#     )

#     # Save leaf size to dataframe
#     leaf.leaf_area = np.sum(min_hues * max_hues * saturation * values)

#     leaf.leaf_binary = new_img.convert("RGB").copy()


def append_leaf_area_binary(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and saves a binary image with the leaf area highlighted in white, to the object.
    """

    # Convert the image to grayscale
    image_gray = leaf.img.convert("L")

    enhancer = ImageEnhance.Contrast(image_gray)
    image_gray = enhancer.enhance(2)

    # Find contours in the grayscale image
    level = settings[leaf.background_colour]["leaf_area"]["level"]
    contours = (
        measure.find_contours(np.array(image_gray), level=level - 10)
        + measure.find_contours(np.array(image_gray), level=level)
        + measure.find_contours(np.array(image_gray), level=level + 10)
    )
    # Create a colormap for contour colors
    colors = list(mcolors.TABLEAU_COLORS.values())

    # Convert the image to RGB mode for drawing contours
    new_img = Image.new("RGB", (image_gray.size[0], image_gray.size[1]), color="black")
    draw_on_white = ImageDraw.Draw(new_img)
    draw_on_img = ImageDraw.Draw(leaf.modified_image)

    # Draw the contours on the image with different colors
    for i, contour in enumerate(contours):
        # Get the leftmost and rightmost x-coordinates of the shape
        x_coords = [coord[0] for coord in contour]
        leftmost_x = min(x_coords)
        rightmost_x = max(x_coords)
        # Calculate the width of the shape
        width = rightmost_x - leftmost_x
        if width >= image_gray.size[1] / 4:
            contour_points = (
                np.flip(contour, axis=1).flatten().tolist()
            )  # Convert contour to list of points
            # "blue" instead of colors[i % len(colors)]
            draw_on_white.line(contour_points, fill="blue", width=2)
            draw_on_img.line(contour_points, fill="blue", width=5)

    # floodfill
    ImageDraw.floodfill(
        new_img, (new_img.size[0] / 2, new_img.size[1] / 2), (255, 255, 255)
    )

    pixels = new_img.load()
    area = 0
    for i in range(new_img.size[0]):
        for j in range(new_img.size[1]):
            if pixels[i, j] != (255, 255, 255):  # if not white:
                pixels[i, j] = (0, 0, 0)  # change to black
            else:
                area += 1

    # Save leaf size to dataframe
    leaf.leaf_area = area
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

    if leaf.leaf_area == 0:
        leaf.lesion_area_percentage = 0
        leaf.lesion_area_mm2 = 0
    else:
        leaf.lesion_area_percentage = 100 * leaf.lesion_area / leaf.leaf_area

    if leaf.reference_area == 0:
        leaf.lesion_area_mm2 = None
    else:
        leaf.lesion_area_mm2 = (
            leaf.lesion_area * settings["reference_area_mm"]
        ) / leaf.reference_area

    leaf.lesion_binary = new_img.convert("RGB").copy()

    pixels = leaf.modified_image.load()
    leaf_mask = leaf.leaf_binary.load()
    lesion_mask = leaf.lesion_binary.load()
    area = 0
    for i in range(leaf.img.size[0]):  # for every pixel:
        for j in range(leaf.img.size[1]):
            if leaf_mask[i, j] == (255, 255, 255) and lesion_mask[i, j] == (
                0,
                0,
                0,
            ):  # if white in leaf mask and black in lesion mask
                pixels[i, j] = (255, 0, 0)  # change to red
            else:
                area += 1


def process_image(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and calls the functions required to process the object.
    """

    start_time = time.time()
    leaf.modified_image = leaf.img.copy()
    append_reference_area_binary(leaf)
    append_leaf_area_binary(leaf)
    append_lesion_area_binary(leaf)
    leaf.run_time = time.time() - start_time
