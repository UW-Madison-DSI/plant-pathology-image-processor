import os
from leaflesiondetector import settings, process_image, get_leaf_area_binary, get_lesion_area_binary
import shutil
from PIL import Image, ImageChops

# Unit test for the get_leaf_area_binary function
def test_get_leaf_area_binary():
    '''
    Tests the get_leaf_area_binary function to ensure
    the function is not breaking.
    '''
    # Create a test pillow image
    test_img = Image.new("RGB", (4, 4))
    # Pass the test image to the function
    try:
        test_img = get_leaf_area_binary(test_img)
    except Exception as e:
        assert False
    # Check the output is a pillow image
    assert isinstance(test_img, Image.Image)
    
# Unit test for get_lesion_area_binary function
def test_get_lesion_area_binary():
    '''
    Tests the get_lesion_area_binary function to ensure
    the function is not breaking.
    '''
    # Create a test pillow image
    test_img = Image.new("RGB", (4, 4))
    # Pass the test image to the function
    try:
        test_img = get_lesion_area_binary(test_img)
    except Exception as e:
        assert False
    # Check the output is a pillow image
    assert isinstance(test_img, Image.Image)

# Unit test for process_image function
def test_process_image():
    '''
    Tests the process_image function to ensure
    the function is not breaking.
    '''
    # Modify settings.json to use the test images
    settings["input_folder_path"] = "tests/fixtures/input_images/"
    settings["output_folder_path"] = "tests/fixtures/new_output_images/"
    # Make temporary output folders
    os.makedirs(settings["output_folder_path"])
    os.makedirs(settings["output_folder_path"] + "leaf_area_binaries/")
    os.makedirs(settings["output_folder_path"] + "lesion_area_binaries/")
    # Process and check one test image
    try:
        process_image("Xg_01_post.jpeg")
    except Exception as e:
        assert False
    assert os.path.exists(settings["output_folder_path"] + "leaf_area_binaries/Xg_01_post_leaf_area_binary.jpeg") and os.path.exists(settings["output_folder_path"] + "lesion_area_binaries/Xg_01_post_lesion_area_binary.jpeg")

# Integration test
def output_consistency_test():
    '''
    This function tests the consistency of the image output to determine whether
    the changes made to the code affect the base functionality of the image processor.
    '''
    # Modify settings.json to use the test images
    settings["input_folder_path"] = "tests/fixtures/input_images/"
    settings["output_folder_path"] = "tests/fixtures/new_output_images/"

    # Make temporary output folders
    os.makedirs(settings["output_folder_path"])
    os.makedirs(settings["output_folder_path"] + "leaf_area_binaries/")
    os.makedirs(settings["output_folder_path"] + "lesion_area_binaries/")

    # Process and check the test images
    for image_name in os.listdir(settings["input_folder_path"]):
        process_image(image_name)
        diff_leaf = ImageChops.difference(
            Image.open(f"{settings['output_folder_path']}leaf_area_binaries/{image_name[:-4]}_leaf_area_binary.jpeg"),
            Image.open(f"tests/fixtures/output_images/leaf_area_binaries/{image_name[:-4]}_leaf_area_binary.jpeg"))
        diff_lesion = ImageChops.difference(
            Image.open(f"{settings['output_folder_path']}lesion_area_binaries/{image_name[:-4]}_lesion_area_binary.jpeg"),
            Image.open(f"tests/fixtures/output_images/lesion_area_binaries/{image_name[:-4]}_lesion_area_binary.jpeg"))
        if diff_leaf.getbbox() is None or diff_lesion.getbbox() is None:
            continue
        else:
            return False

    # Remove the new output folders
    if os.path.exists(settings["output_folder_path"]):
        shutil.rmtree(settings["output_folder_path"])

    return True
    
def test_answer():
    assert output_consistency_test() == True
    