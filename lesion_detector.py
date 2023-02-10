# import packages
import pandas as pd
import numpy as np
import os
from PIL import Image
from PIL import ImageFilter
import json

# Using a Dataframe to save data to a CSV 
results_df = pd.DataFrame(columns=['image', 'leaf area', 'lesion area', 'percentage of leaf area'])

# Read in settings from JSON file
with open('settings.json') as f:
    settings = json.load(f)
    
def generate_report() -> None:
    '''
    This function generates a report in Markdown format.
    '''

    with open("output.md", "w") as file:
        file.write("Image Name | Original image | Leaf area binary |  Non-lesion area binary | Percentage Area Affected |\n")
        file.write(":---:|:---:|:---:|:---:|:---:\n")
        for image_name in os.listdir(input_folder_path):
            file.write(f"{image_name}|![](input_images/{image_name}) | ![](results/leaf_area_binaries/{image_name[:-4]}_leaf_area_binary.jpeg) | ![](results/lesion_area_binaries/{image_name[:-4]}_lesion_area_binary.jpeg)")
            file.write(f" | {'%.2f'%results_df.loc[results_df['image'] == image_name, 'percentage of leaf area'].values[0]} %\n")

def get_leaf_area_binary(img: Image) -> Image:
    '''
    This function takes an image as input and returns a binary image with the leaf area highlighted in white.
    '''

    # Convert to HSV
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    
    # Create a mask of green regions
    min_hues = hsv[:,:,0] > settings[settings['background_colour']]['leaf_area']['min_hue']
    max_hues = hsv[:,:,0] < settings[settings['background_colour']]['leaf_area']['max_hue']
    saturation = hsv[:,:,1] > settings[settings['background_colour']]['leaf_area']['min_saturation']
    values = hsv[:,:,2] > settings[settings['background_colour']]['leaf_area']['min_value']
    new_img = Image.fromarray(np.uint8(min_hues*max_hues*saturation*values*255))

    # Remove noise
    new_img = new_img.filter(ImageFilter.MedianFilter(5))

    # Save leaf size to dataframe
    results_df.loc[results_df['image'] == image_name, 'leaf area'] = np.sum(min_hues*max_hues*saturation*values)

    return new_img.convert('RGB')

def get_lesion_area_binary(img: Image) -> Image:
    '''
    This function takes an image as input and returns a binary image with the non lesion area highlighted in white.
    i.e. the lesion area is black.
    '''

    # Convert to HSV
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    
    # Create a mask of lesions
    min_hues = hsv[:,:,0] > settings[settings['background_colour']]['lesion_area']['min_hue']
    max_hues = hsv[:,:,0] < settings[settings['background_colour']]['lesion_area']['max_hue']
    saturation = hsv[:,:,1] > settings[settings['background_colour']]['lesion_area']['min_saturation']
    values = hsv[:,:,2] > settings[settings['background_colour']]['lesion_area']['min_value']
    new_img = Image.fromarray(np.uint8(min_hues*max_hues*saturation*values*255))

    # Remove noise
    new_img = new_img.filter(ImageFilter.MedianFilter(5))

    # Save lesion size to dataframe
    results_df.loc[results_df['image'] == image_name, 'lesion area'] = results_df.loc[results_df['image'] == image_name, 'leaf area'] - np.sum(min_hues*max_hues*saturation*values)
    results_df.loc[results_df['image'] == image_name, 'percentage of leaf area'] = 100*results_df.loc[results_df['image'] == image_name, 'lesion area'] / results_df.loc[results_df['image'] == image_name, 'leaf area']

    return new_img.convert('RGB')

if __name__ == '__main__':

    # get settings
    settings['background_colour'] = input('What is the background colour? (black_velvet or grey_background) ')

    # paths used
    input_folder_path = settings[settings['background_colour']]['input_folder_path']
    output_folder_path = settings[settings['background_colour']]['output_folder_path']
    
    # process images
    for image_name in os.listdir(input_folder_path):
        results_df = pd.concat([results_df, pd.DataFrame({'image': [image_name], 'leaf area': [0], 'lesion area': [0], 'percentage of leaf area': [0]})])  
        print(f'Processing image: {image_name}')
        get_leaf_area_binary(Image.open(input_folder_path + image_name)).save(output_folder_path+'leaf_area_binaries/' + f'{image_name[:-4]}_leaf_area_binary.jpeg')
        get_lesion_area_binary(Image.open(input_folder_path + image_name)).save(output_folder_path+'lesion_area_binaries/' + f'{image_name[:-4]}_lesion_area_binary.jpeg')

    # save calculations to output file
    results_df.to_csv(output_folder_path+'output.csv', index=False)

    # generate report
    generate_report()
