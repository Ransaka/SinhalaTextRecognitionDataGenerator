import cv2
import numpy as np

# Load the image
image = cv2.imread('/home/ransaka/opensource/computer_vision/testing/out/sin01.png')

# Define the four corners of the region you want to skew
# Format: (top-left, top-right, bottom-right, bottom-left)
original_points = np.float32([[50, 50], [200, 50], [250, 300], [100, 300]])

# Define the new positions of the corners after skewing
# You can adjust these values to achieve the desired skewing effect
skewed_points = np.float32([[0, 0], [200, 0], [250, 300], [50, 300]])

# Calculate the perspective transformation matrix
matrix = cv2.getPerspectiveTransform(original_points, skewed_points)

# Apply the perspective transformation to the image
skewed_image = cv2.warpPerspective(image, matrix, (image.shape[1], image.shape[0]))

# save image
cv2.imwrite("out/sin02_skewed.png", skewed_image)
