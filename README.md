# plant-pathology-image-processor
extract information from plant pathlogy images

> Setup and Information

1. Add input images to the folder `input_images`
2. Results are stored in the folder `results`
   1. `results/leaf_area_binaries` contains the leaf area binary images
   2. `results/lesion_area_binaries` contains the lesion area binary images
   3. `output.csv` contains the results of the program

> Use the following command to setup and run the program

```bash
pip3 install -r requirements.txt
```

```bash
python3 lesion_detector.py
```
> Example

Original image           | Leaf area binary           |  Non-lesion area binary
:-------------------------:|:-------------------------:|:-------------------------:
![Original image](./input_images/Xg_02_post.jpeg)  | ![Leaf area binary](./results/leaf_area_binaries/Xg_02_post._leaf_area_binary.jpeg)  |  ![Non-lesion area binary](results/lesion_area_binaries/Xg_02_post._lesion_area_binary.jpeg)