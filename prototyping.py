import cv2
from google.colab.patches import cv2_imshow

# Read the TIFF image
img = cv2.imread("Xg_irrigated_2.tif", cv2.IMREAD_UNCHANGED)

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply a binary threshold to the image
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# Display the image
cv2_imshow(thresh)