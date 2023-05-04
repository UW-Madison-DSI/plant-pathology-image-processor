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


@pytest.fixture()
def base_leaf():
    with Image.open("./tests/fixtures/input_images/Xg_01_post.jpeg") as img:
        return Leaf(
            f"test_{int(time.time_ns())}",
            "test",
            img.copy(),
            background_colour="Black",
            minimum_lesion_area_value=120,
            modified_image=img.copy(),
        )


# Unit test for the get_leaf_area_binary function
def test_get_leaf_area_binary(base_leaf):
    """
    Tests the get_leaf_area_binary function to ensure
    the function is not breaking.
    """
    append_leaf_area_binary(base_leaf)
    assert isinstance(base_leaf.leaf_binary, Image.Image)


# Unit test for get_lesion_area_binary function
def test_get_lesion_area_binary(base_leaf):
    """
    Tests the get_lesion_area_binary function to ensure
    the function is not breaking.
    """
    append_leaf_area_binary(base_leaf)
    append_lesion_area_binary(base_leaf)
    assert isinstance(base_leaf.lesion_binary, Image.Image)


# Unit test for process_image function
def test_process_image(base_leaf):
    """
    Tests the process_image function to ensure
    the function is not breaking.
    """
    process_image(base_leaf)
    assert (
        isinstance(base_leaf.leaf_binary, Image.Image)
        and isinstance(base_leaf.lesion_binary, Image.Image)
        and (base_leaf.leaf_area > 0)
        and (base_leaf.lesion_area > 0)
        and (base_leaf.lesion_area_percentage > 0)
        and (base_leaf.run_time > 0)
    )


# Integration test
@pytest.mark.parametrize("image_name", os.listdir("./tests/fixtures/input_images/"))
def test_pipeline_produces_expected_output(image_name):
    """
    This function tests the consistency of the image output to determine whether
    the changes made to the code affect the base functionality of the image processor.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.mkdir(f"{tmpdirname}/new_output_images")
        os.mkdir(f"{tmpdirname}/new_output_images/leaf_area_binaries")
        os.mkdir(f"{tmpdirname}/new_output_images/lesion_area_binaries")

        with Image.open(f"./tests/fixtures/input_images/{image_name}") as img:
            leaf = Leaf(
                f"test_{int(time.time_ns())}",
                "test",
                img.copy(),
                background_colour="Black",
            )

            leaf.minimum_lesion_area_value = 120
            process_image(leaf)
            if leaf.lesion_area_percentage > 3.5:
                leaf.minimum_lesion_area_value = 140
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
