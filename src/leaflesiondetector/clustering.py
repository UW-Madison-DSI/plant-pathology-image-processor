# for loading/processing the images  
from tensorflow.keras.utils import load_img
from keras.applications.vgg16 import preprocess_input 

# models 
from keras.applications.vgg16 import VGG16 
from keras.models import Model

# clustering and dimension reduction
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import os
import numpy as np
from PIL import Image

from leaflesiondetector.leaf import Leaf, LeafList

# holds the cluster id and the images { id: [images] }
groups = {}

def extract_features(img, model):
    # load the image as a 224x224 array
    # img = load_img(file, target_size=(224,224))
    img = img.resize((224,224), Image.ANTIALIAS)
    # convert from 'PIL.Image.Image' to numpy array
    img = np.array(img) 
    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape(1,224,224,3) 
    # prepare image for model
    imgx = preprocess_input(reshaped_img)
    # get the feature vector
    features = model.predict(imgx, use_multiprocessing=True)
    return features

def cluster(x, n, leaflist: LeafList):
  # cluster feature vectors
  kmeans = KMeans(n_clusters=n, random_state=25)
  kmeans.fit(x)
  for leaf, cluster in zip(leaflist, kmeans.labels_):
      leaf.cluster = cluster

def run(leaflist: LeafList, n: int):
    '''runs the clustering algorithm'''
    # load the model
    print("Loading model...")
    model = VGG16()
    # re-structure the model
    print("Re-structuring model...")
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    # extract features from each image
    print("Extracting features from images...")
    features = [extract_features(leaf.img.copy(), model) for leaf in leaflist]
    # flatten into a 2D array
    features = np.array(features).reshape(len(leaflist), 4096)
    # reduce the features to 2D
    print("Reducing features to 2D...")
    pca = PCA(n_components=len(leaflist))
    pca.fit(features)
    x = pca.transform(features)
    # cluster the features
    print("Clustering features...")
    cluster(x, n, leaflist)