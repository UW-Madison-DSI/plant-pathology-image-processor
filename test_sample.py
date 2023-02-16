import os
# import sys
# sys.path.append(os.path.realpath('../'))
from lesion_detector import settings, process_image
import shutil
from PIL import Image, ImageChops

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