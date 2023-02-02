# import packages
import pandas as pd
import numpy as np
import os
from PIL import Image

def get_leaf(img):
    hsv_img = img.convert('HSV')
    hsv = np.array(hsv_img)
    for dim1 in hsv:
        for dim2 in dim1:
            dim2[0] = 0
            dim2[1] = 100
    new_img = Image.fromarray(hsv, 'HSV')
    return new_img.convert('RGB')

if __name__ == '__main__':

    # Using a Dataframe to save data to a CSV 
    df = pd.DataFrame(columns=['image', 'leaf area', 'lesion area', 'percentage of leaf area'])

    # images folder path
    folder_path = "./images/"

    # process images
    for image_name in os.listdir(folder_path):
        print(f'Processing image: {image_name}')
        image = Image.open(folder_path + image_name)
        modified_image = get_leaf(image)
        
        # show the picture
        modified_image.show()

    # save calculations to output file

    df.to_csv('output.csv', index=False)
