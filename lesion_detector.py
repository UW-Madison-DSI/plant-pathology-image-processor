# import packages
import pandas as pd
import numpy as np
import os
from PIL import Image
from PIL import ImageFilter

# Using a Dataframe to save data to a CSV 
results_df = pd.DataFrame(columns=['image', 'leaf area', 'lesion area', 'percentage of leaf area'])

def get_leaf_area_binary(img):
    '''
    This function takes an image as input and returns a binary image with the leaf area highlighted in white.
    '''

    # Convert to HSV
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    
    # Create a mask of green regions
    min_hues = hsv[:,:,0] > 50
    max_hues = hsv[:,:,0] < 100
    saturation = hsv[:,:,1] > 0
    values = hsv[:,:,2] > 60
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
    min_hues = hsv[:,:,0] > 45
    max_hues = hsv[:,:,0] < 100
    saturation = hsv[:,:,1] > 0
    values = hsv[:,:,2] > 140
    new_img = Image.fromarray(np.uint8(min_hues*max_hues*saturation*values*255))

    # Remove noise
    new_img = new_img.filter(ImageFilter.MedianFilter(5))

    # Save lesion size to dataframe
    results_df.loc[results_df['image'] == image_name, 'lesion area'] = results_df.loc[results_df['image'] == image_name, 'leaf area'] - np.sum(min_hues*max_hues*saturation*values)
    results_df.loc[results_df['image'] == image_name, 'percentage of leaf area'] = results_df.loc[results_df['image'] == image_name, 'lesion area'] / results_df.loc[results_df['image'] == image_name, 'leaf area']

    return new_img.convert('RGB')

if __name__ == '__main__':

    # paths used
    input_folder_path = "./input_images/"
    output_folder_path = "./results/"

    # process images
    for image_name in os.listdir(input_folder_path):
        results_df = results_df.append({'image': image_name}, ignore_index=True)    
        print(f'Processing image: {image_name}')
        get_leaf_area_binary(Image.open(input_folder_path + image_name)).save(output_folder_path+'leaf_area_binaries/' + f'{image_name[:-4]}_leaf_area_binary.jpeg')
        get_lesion_area_binary(Image.open(input_folder_path + image_name)).save(output_folder_path+'lesion_area_binaries/' + f'{image_name[:-4]}_lesion_area_binary.jpeg')

    # save calculations to output file
    results_df.to_csv('./results/output.csv', index=False)
