# for loading/processing the images  
from tensorflow.keras.utils import load_img 
from tensorflow.keras.utils import save_img
from keras.applications.vgg16 import preprocess_input 

# models 
from keras.applications.vgg16 import VGG16 
from keras.models import Model

# clustering and dimension reduction
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# for everything else
import os
import numpy as np
import matplotlib.pyplot as plt
# import shutil

# holds the cluster id and the images { id: [images] }
groups = {}
global image_filenames

def set_path(p):
    '''sets the path to the directory of images'''
    global path
    path = p

def extract_features(file, model):
    # load the image as a 224x224 array
    img = load_img(file, target_size=(224,224))
    # convert from 'PIL.Image.Image' to numpy array
    img = np.array(img) 
    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape(1,224,224,3) 
    # prepare image for model
    imgx = preprocess_input(reshaped_img)
    # get the feature vector
    features = model.predict(imgx, use_multiprocessing=True)
    return features

# function that lets you view a cluster (based on identifier)        
def save_cluster(cluster):
    # gets the list of filenames for a cluster
    files = groups[cluster]
    # save each image in the cluster
    for index, file in enumerate(files):
      print(f"Cluster {cluster} - Image: {file}")
      img = load_img(f'{path}{file}')
      img.show()
      #save_img(f"clusters/{cluster}_{index}.jpg", img)

def get_best(x):
    # this is just incase you want to see which value for k might be the best 
    sse = []
    list_k = list(range(3, 50))

    for k in list_k:
        km = KMeans(n_clusters=k, random_state=22, n_jobs=-1)
        km.fit(x)
        sse.append(km.inertia_)

    # Plot sse against k
    plt.figure(figsize=(6, 6))
    plt.plot(list_k, sse)
    plt.xlabel(r'Number of clusters *k*')
    plt.ylabel('Sum of squared distance')

def get_images():
  # creates a ScandirIterator aliased as files
  image_filenames = []
  with os.scandir(path) as files:
  # loops through each file in the directory
      for file in files:
        if file.name.endswith('.jpeg'):
          # adds only the image files to the flowers list
          image_filenames.append(file.name)
  return image_filenames

def cluster(x, n, image_filenames):
  # cluster feature vectors
  kmeans = KMeans(n_clusters=n, random_state=25)
  kmeans.fit(x)

  for file, cluster in zip(image_filenames,kmeans.labels_):
      if cluster not in groups.keys():
          groups[cluster] = []
          groups[cluster].append(file)
      else:
          groups[cluster].append(file)

  # save the clusters
  for cluster in groups.keys():
    save_cluster(cluster)

def run():
    '''runs the clustering algorithm'''
    # shutil.rmtree("clusters")
    # os.mkdir("clusters")
    # set the path to the directory of images
    set_path(f'data/{input("Enter the name of the directory: ")}/')
    # get the image filenames
    image_filenames = get_images()
    # load the model
    model = VGG16()
    # re-structure the model
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    # extract features from each image
    features = [extract_features(f'{path}{file}', model) for file in image_filenames]
    # flatten into a 2D array
    features = np.array(features).reshape(len(image_filenames), 4096)
    # reduce the features to 2D
    pca = PCA(n_components=len(image_filenames))
    pca.fit(features)
    x = pca.transform(features)
    # cluster the features
    cluster(x, 2, image_filenames)