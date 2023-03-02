import os
from leaflesiondetector.lesion_detector import process_image, get_leaf_area_binary, get_lesion_area_binary, Leaf
import shutil
from PIL import Image, ImageChops
from pathlib import Path

# Unit test for the get_leaf_area_binary function
def test_get_leaf_area_binary():
    '''
    Tests the get_leaf_area_binary function to ensure
    the function is not breaking.
    '''
    # Create a test pillow image
    # Create a leaf object
    with Image.open("./tests/fixtures/input_images/Xg_01_post.jpeg") as img:
        leaf = Leaf('test', img.copy())
    # Pass the test image to the function
    try:
        get_leaf_area_binary(leaf)
    except Exception as e:
        print(e)
        assert False
    # Check the output is a pillow image
    assert isinstance(leaf.leaf_binary, Image.Image)
    
# Unit test for get_lesion_area_binary function
def test_get_lesion_area_binary():
    '''
    Tests the get_lesion_area_binary function to ensure
    the function is not breaking.
    '''
    # Create a test pillow image
    # Create a leaf object
    with Image.open("./tests/fixtures/input_images/Xg_01_post.jpeg") as img:
        leaf = Leaf('test', img.copy())
    # Pass the test image to the function
    try:
        get_lesion_area_binary(leaf)
    except Exception as e:
        print(e)
        assert False
    # Check the output is a pillow image
    assert isinstance(leaf.lesion_binary, Image.Image)

# Unit test for process_image function
def test_process_image():
    '''
    Tests the process_image function to ensure
    the function is not breaking.
    '''
    # Get a test image
    with Image.open("./tests/fixtures/input_images/Xg_01_post.jpeg") as img:
        leaf = Leaf('test', img.copy())
    # Process and check one test image
    try:
        process_image(leaf)
    except Exception as e:
        assert False
    assert isinstance(leaf.leaf_binary, Image.Image) and isinstance(leaf.lesion_binary, Image.Image) and leaf.leaf_area > 0 and leaf.lesion_area > 0 and leaf.lesion_area_percentage > 0 and leaf.run_time > 0

# Integration test
def test_output_consistency():
    '''
    This function tests the consistency of the image output to determine whether
    the changes made to the code affect the base functionality of the image processor.
    '''

    # Create a new output folder
    if not os.path.exists("./tests/fixtures/new_output_images"):
        os.mkdir("./tests/fixtures/new_output_images")
        os.mkdir("./tests/fixtures/new_output_images/leaf_area_binaries")
        os.mkdir("./tests/fixtures/new_output_images/lesion_area_binaries")

    # Process and check the test images
    for image_name in os.listdir("./tests/fixtures/input_images/"):
        with Image.open(f"./tests/fixtures/input_images/{image_name}") as img:
            leaf = Leaf('test', img.copy())
        try:
            process_image(leaf)
            leaf.leaf_binary.save(f"./tests/fixtures/new_output_images/leaf_area_binaries/{Path(image_name).stem}_leaf_area_binary{Path(image_name).suffix}")
            leaf.lesion_binary.save(f"./tests/fixtures/new_output_images/lesion_area_binaries/{Path(image_name).stem}_lesion_area_binary{Path(image_name).suffix}")
        except Exception as e:
            print(e)
            assert False
        diff_leaf = ImageChops.difference(
            Image.open(f"./tests/fixtures/new_output_images/leaf_area_binaries/{Path(image_name).stem}_leaf_area_binary{Path(image_name).suffix}"),
            Image.open(f"./tests/fixtures/new_output_images/leaf_area_binaries/{Path(image_name).stem}_leaf_area_binary{Path(image_name).suffix}"))
        diff_lesion = ImageChops.difference(
            Image.open(f"./tests/fixtures/new_output_images/lesion_area_binaries/{Path(image_name).stem}_lesion_area_binary{Path(image_name).suffix}"),
            Image.open(f"./tests/fixtures/new_output_images/lesion_area_binaries/{Path(image_name).stem}_lesion_area_binary{Path(image_name).suffix}"))
        assert diff_leaf.getbbox() is None or diff_lesion.getbbox() is None

    # Remove the new output folders
    if os.path.exists("./tests/fixtures/new_output_images"):
        shutil.rmtree("./tests/fixtures/new_output_images")
    