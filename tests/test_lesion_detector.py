import os
import pytest
from leaflesiondetector.lesion_detector import (
    process_image,
    append_leaf_area_binary,
    append_lesion_area_binary,
)
from leaflesiondetector.leaf import Leaf
from PIL import Image, ImageChops
from pathlib import Path
import tempfile
import time

# Unit test for the get_leaf_area_binary function
def test_get_leaf_area_binary():
    """
    Tests the get_leaf_area_binary function to ensure
    the function is not breaking.
    """
    # Create a test pillow image
    # Create a leaf object
    with Image.open("./tests/fixtures/input_images/Xg_01_post.jpeg") as img:
        leaf = Leaf(f"test_{int(time.time_ns())}", "test", img.copy())
    # Pass the test image to the function
    append_leaf_area_binary(leaf)
    # Check the output is a pillow image
    assert isinstance(leaf.leaf_binary, Image.Image)


# Unit test for get_lesion_area_binary function
def test_get_lesion_area_binary():
    """
    Tests the get_lesion_area_binary function to ensure
    the function is not breaking.
    """
    # Create a test pillow image
    # Create a leaf object
    with Image.open("./tests/fixtures/input_images/Xg_01_post.jpeg") as img:
        leaf = Leaf(f"test_{int(time.time_ns())}", "test", img.copy())
    # Pass the test image to the function
    append_lesion_area_binary(leaf)
    # Check the output is a pillow image
    assert isinstance(leaf.lesion_binary, Image.Image)


# Unit test for process_image function
def test_process_image():
    """
    Tests the process_image function to ensure
    the function is not breaking.
    """
    # Get a test image
    with Image.open("./tests/fixtures/input_images/Xg_01_post.jpeg") as img:
        leaf = Leaf(f"test_{int(time.time_ns())}", "test", img.copy())
    # Process and check one test image
    process_image(leaf)
    assert (
        isinstance(leaf.leaf_binary, Image.Image)
        and isinstance(leaf.lesion_binary, Image.Image)
        and leaf.leaf_area > 0
        and leaf.lesion_area > 0
        and leaf.lesion_area_percentage > 0
        and leaf.run_time > 0
    )


# Integration test
@pytest.mark.parametrize("image_name", os.listdir("./tests/fixtures/input_images/"))
def test_output_consistency(image_name):
    """
    This function tests the consistency of the image output to determine whether
    the changes made to the code affect the base functionality of the image processor.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.mkdir(f"{tmpdirname}/new_output_images")
        os.mkdir(f"{tmpdirname}/new_output_images/leaf_area_binaries")
        os.mkdir(f"{tmpdirname}/new_output_images/lesion_area_binaries")

        with Image.open(f"./tests/fixtures/input_images/{image_name}") as img:
            leaf = Leaf(f"test_{int(time.time_ns())}", "test", img.copy())
            process_image(leaf)
            leaf.leaf_binary.save(
                f"{tmpdirname}/new_output_images/leaf_area_binaries/{Path(image_name).stem}_leaf_area_binary{Path(image_name).suffix}"
            )
            leaf.lesion_binary.save(
                f"{tmpdirname}/new_output_images/lesion_area_binaries/{Path(image_name).stem}_lesion_area_binary{Path(image_name).suffix}"
            )

        test_image_leaf_area = Image.open(
            f"{tmpdirname}/new_output_images/leaf_area_binaries/{Path(image_name).stem}_leaf_area_binary{Path(image_name).suffix}"
        )
        test_image_lesion_area = Image.open(
            f"{tmpdirname}/new_output_images/lesion_area_binaries/{Path(image_name).stem}_lesion_area_binary{Path(image_name).suffix}"
        )
        test_fixture_leaf_area = Image.open(
            f"./tests/fixtures/output_images/leaf_area_binaries/{Path(image_name).stem}_leaf_area_binary{Path(image_name).suffix}"
        )
        test_fixture_lesion_area = Image.open(
            f"./tests/fixtures/output_images/lesion_area_binaries/{Path(image_name).stem}_lesion_area_binary{Path(image_name).suffix}"
        )
        leaf_area_matches = (
            ImageChops.difference(
                test_image_leaf_area, test_fixture_leaf_area
            ).getbbox()
            is None
        )
        lesion_area_matches = (
            ImageChops.difference(
                test_image_lesion_area, test_fixture_lesion_area
            ).getbbox()
            is None
        )
        assert leaf_area_matches and lesion_area_matches
