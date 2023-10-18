import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from PIL import ImageFilter
import json
import time
from leaflesiondetector.leaf import Leaf
from skimage import measure
from scipy import ndimage

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


def value_to_color(value, vmin, vmax):
    """Convert a value to an RGB color tuple based on its position between vmin and vmax."""
    vrange = vmax - vmin
    if vrange == 0:
        return (0, 0, 0)
    else:
        v = (value - vmin) / vrange
        return (255, int(255 * (1.0 - v)), 0)


def segment_lesions(leaf: Leaf):
    """
    This function segments the lesions in the image.
    """

    # Segment individual regions from the binary
    lesion_binary = np.asarray(leaf.lesion_binary)
    lesion_binary = ~lesion_binary
    labeled, num_objects = ndimage.label(lesion_binary)

    # Filter the lesions based on the size threshold
    leaf.labeled_pixels = labeled
    classes, sizes = np.unique(labeled, return_counts=True)
    if leaf.reference:
        leaf.lesion_class_map = {
            int(k): float(v)
            for k, v in zip(
                classes, sizes * settings["reference_area_mm"] / leaf.reference_area
            )
            if v > leaf.lesion_size_threshold
        }
    else:
        leaf.lesion_size_threshold = (
            10.0 if leaf.lesion_size_threshold == 0.01 else leaf.lesion_size_threshold
        )
        leaf.lesion_class_map = {
            int(k): float(v)
            for k, v in zip(classes, sizes)
            if v > leaf.lesion_size_threshold
        }

    # Remove segmented classes 0 and 1 since they represent the background and the leaf
    leaf.lesion_class_map.pop(0)
    leaf.lesion_class_map.pop(1)

    # Create a color map for the lesions
    class_color = {}
    for class_value in leaf.lesion_class_map.keys():
        class_color[class_value] = value_to_color(
            leaf.lesion_class_map[class_value],
            min(leaf.lesion_class_map.values()),
            max(leaf.lesion_class_map.values()),
        )

    # Create a new image with the lesions highlighted
    leaf_pixels = leaf.leaf_binary.load()
    leaf.lesion_area = 0
    for y in range(leaf.labeled_pixels.shape[0]):
        for x in range(leaf.labeled_pixels.shape[1]):
            if (labeled[y, x] not in class_color.keys()) or (
                leaf_pixels[x, y] == (0, 0, 0)
            ):
                continue
            leaf.modified_image.putpixel((x, y), class_color[labeled[y, x]])
            leaf.lesion_area += 1

    # Save calculated values to the leaf object
    leaf.lesion_area = (
        (leaf.lesion_area * settings["reference_area_mm"]) / leaf.reference_area
        if leaf.reference
        else leaf.lesion_area
    )
    leaf.lesion_area_percentage = 100 * leaf.lesion_area / leaf.leaf_area

    leaf.average_lesion_size = np.mean(list(leaf.lesion_class_map.values()))
    leaf.min_lesion_size = min(list(leaf.lesion_class_map.values()))
    leaf.max_lesion_size = max(list(leaf.lesion_class_map.values()))
    leaf.num_lesions = len(list(leaf.lesion_class_map.values()))


def append_reference_area_binary(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and saves a binary image with the reference area highlighted in white, to the object.
    """

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

    leaf.reference_binary = new_img.convert("RGB").copy()

    # Mark the reference area in the image and save calculated values to the leaf object
    pixels = leaf.modified_image.load()
    reference_mask = leaf.reference_binary.load()
    for i in range(leaf.img.size[0]):  # for every pixel:
        for j in range(leaf.img.size[1]):
            if reference_mask[i, j] == (255, 255, 255):  # if white in reference mask
                leaf.reference_area += 1
                pixels[i, j] = (0, 255, 0)  # change to green


def append_leaf_area_binary(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and saves a binary image with the leaf area highlighted in white, to the object.
    """

    hsv_img = leaf.img.convert("HSV")
    hsv = np.array(hsv_img)

    # Create a mask of the estimated leaf region using image thresholding
    min_hues = hsv[:, :, 0] > settings[leaf.background_colour]["leaf_area"]["min_hue"]
    max_hues = hsv[:, :, 0] < settings[leaf.background_colour]["leaf_area"]["max_hue"]
    saturation = (
        hsv[:, :, 1] > settings[leaf.background_colour]["leaf_area"]["min_saturation"]
    )
    values = hsv[:, :, 2] > settings[leaf.background_colour]["leaf_area"]["min_value"]

    new_img = Image.fromarray(np.uint8(min_hues * max_hues * saturation * values * 255))

    # Apply contouring to mark the leaf boundary
    image_gray = new_img.convert("L")

    enhancer = ImageEnhance.Contrast(image_gray)
    image_gray = enhancer.enhance(2)

    level = settings[leaf.background_colour]["leaf_area"]["level"]
    contours = (
        measure.find_contours(np.array(image_gray), level=level - 10)
        + measure.find_contours(np.array(image_gray), level=level)
        + measure.find_contours(np.array(image_gray), level=level + 10)
    )

    new_img = Image.new("RGB", (image_gray.size[0], image_gray.size[1]), color="black")
    draw_on_white = ImageDraw.Draw(new_img)
    draw_on_img = ImageDraw.Draw(leaf.modified_image)

    for contour in contours:
        x_coords = [coord[0] for coord in contour]
        leftmost_x = min(x_coords)
        rightmost_x = max(x_coords)
        width = rightmost_x - leftmost_x
        if width >= image_gray.size[1] / 4:
            contour_points = (
                np.flip(contour, axis=1).flatten().tolist()
            )  # Convert contour to list of points
            draw_on_white.line(contour_points, fill="white", width=2)  #blue, 2
            draw_on_img.line(contour_points, fill="blue", width=5)

    leaf.leaf_outline_binary = new_img.copy().convert("RGB")

    # Floodfill the image to remove any noise within the boundary
    ImageDraw.floodfill(
        new_img, (new_img.size[0] / 2, new_img.size[1] / 2), (255, 255, 255)
    )

    # Save calculated values to the leaf object
    leaf.leaf_area = np.sum(np.asarray(new_img.convert("1")))
    leaf.leaf_area = (
        leaf.leaf_area * settings["reference_area_mm"] / leaf.reference_area
        if leaf.reference
        else leaf.leaf_area
    )
    leaf.leaf_binary = new_img.convert("RGB").copy()


def append_lesion_area_binary(leaf: Leaf) -> None:
    """
    Takes a leaf object as input and saves a binary image with the non lesion area highlighted in white, to the object.
    i.e. the lesion area is black.
    """

    hsv_img = leaf.img.convert("HSV")
    hsv = np.array(hsv_img)

    # Create a mask of the estimated lesion region using image thresholding
    min_hues = hsv[:, :, 0] > settings[leaf.background_colour]["lesion_area"]["min_hue"]
    max_hues = hsv[:, :, 0] < settings[leaf.background_colour]["lesion_area"]["max_hue"]
    saturation = (
        hsv[:, :, 1] > settings[leaf.background_colour]["lesion_area"]["min_saturation"]
    )
    values = hsv[:, :, 2] > leaf.minimum_lesion_area_value

    leaf.lesion_binary = Image.fromarray(
        np.uint8(min_hues * max_hues * saturation * values * 255)
    )

    image_gray = leaf.leaf_binary.copy().convert("L")

    # Enhance contrast and use contouring to mark the estimated leaf boundary to ensure lesions on the leaf boundary are included
    enhancer = ImageEnhance.Contrast(image_gray)
    image_gray = enhancer.enhance(2)

    level = settings[leaf.background_colour]["lesion_area"]["level"]
    contours = (
        measure.find_contours(np.array(image_gray), level=level - 10)
        + measure.find_contours(np.array(image_gray), level=level)
        + measure.find_contours(np.array(image_gray), level=level + 10)
    )

    draw = ImageDraw.Draw(leaf.lesion_binary)

    for contour in contours:
        x_coords = [coord[0] for coord in contour]
        leftmost_x = min(x_coords)
        rightmost_x = max(x_coords)
        width = rightmost_x - leftmost_x
        if width >= image_gray.size[1] / 4:
            contour_points = (
                np.flip(contour, axis=1).flatten().tolist()
            )  # Convert contour to list of points
            draw.line(contour_points, fill="white", width=10)

    # Segment individual lesions
    segment_lesions(leaf)


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
