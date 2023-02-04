# import packages
import pandas as pd
import numpy as np
import os
from PIL import Image
from PIL import ImageFilter

# Using a Dataframe to save data to a CSV 
results_df = pd.DataFrame(columns=['image', 'leaf area', 'lesion area', 'percentage of leaf area'])

settings = {
    'background_colour': 'black_velvet',
    'black_velvet': {
        'input_folder_path': "./input_images/black_velvet/",
        'output_folder_path': "./results/black_velvet/",
        'leaf_area': {'min_hue': 50, 'max_hue': 100, 'min_saturation': 0, 'max_saturation': 255, 'min_value': 60, 'max_value': 255},
        'lesion_area': {'min_hue': 45, 'max_hue': 100, 'min_saturation': 0, 'max_saturation': 255, 'min_value': 140, 'max_value': 255},
        },
    'grey_background': {
        'input_folder_path': "./input_images/grey_background/",
        'output_folder_path': "./results/grey_background/",
        'leaf_area': {'min_hue': 20, 'max_hue': 100, 'min_saturation': 20, 'max_saturation': 255, 'min_value': 60, 'max_value': 255},
        'lesion_area': {'min_hue': 20, 'max_hue': 100, 'min_saturation': 20, 'max_saturation': 255, 'min_value': 120, 'max_value': 255},
        }
    }

def get_leaf_area_binary(img):
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

def get_lesion_area_binary(img):
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
    input_folder_path = "./input_images/" + settings['background_colour'] + "/"
    output_folder_path = "./results/" + settings['background_colour'] + "/"

    # process images
    for image_name in os.listdir(input_folder_path):
        results_df = results_df.append({'image': image_name}, ignore_index=True)    
        print(f'Processing image: {image_name}')
        get_leaf_area_binary(Image.open(input_folder_path + image_name)).save(output_folder_path+'leaf_area_binaries/' + f'{image_name[:-4]}_leaf_area_binary.jpeg')
        get_lesion_area_binary(Image.open(input_folder_path + image_name)).save(output_folder_path+'lesion_area_binaries/' + f'{image_name[:-4]}_lesion_area_binary.jpeg')

    # save calculations to output file
    results_df.to_csv(output_folder_path+'output.csv', index=False)

    
