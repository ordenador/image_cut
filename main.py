import cv2
import numpy as np
import os

# Ensure the output directory exists
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Path to the input image
input_image_path = 'images/74.png'

# Read the original high-resolution image
original_image = cv2.imread(input_image_path)

# Check if the image was loaded properly
if original_image is None:
    print(f"Error: Unable to load image at {input_image_path}")
    exit(1)

# Get the dimensions of the original image
orig_height, orig_width = original_image.shape[:2]

# Resize the image to have a height of 500px while maintaining aspect ratio
resize_height = 500
aspect_ratio = resize_height / float(orig_height)
resize_width = int(orig_width * aspect_ratio)

# Resize and convert to grayscale for processing
processed_image = cv2.resize(original_image, (resize_width, resize_height))
gray_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian Blur to the grayscale image
blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

# Apply thresholding to create a binary image
_, thresh_image = cv2.threshold(blurred_image, 0, 255,
                                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Find contours on the thresholded image
contours, _ = cv2.findContours(thresh_image.copy(), cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)

# Calculate the area limits based on the resized image
image_area = resize_width * resize_height
min_area = image_area * 0.05  # 5% of the image area
max_area = image_area * 0.66  # 66% of the image area

# Initialize a list to store bounding rectangles of valid contours
bounding_rects = []

for contour in contours:
    area = cv2.contourArea(contour)
    if min_area < area < max_area:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_rects.append((x, y, w, h))

# If no contours found, exit
if not bounding_rects:
    print("No individual photos detected.")
    exit(1)

# Sort the bounding rectangles (optional, based on your preference)
bounding_rects = sorted(bounding_rects, key=lambda r: (r[1], r[0]))

# Scale the bounding rectangles back to original image size
scale_x = orig_width / float(resize_width)
scale_y = orig_height / float(resize_height)

for idx, (x, y, w, h) in enumerate(bounding_rects):
    # Scale the coordinates
    x_orig = int(x * scale_x)
    y_orig = int(y * scale_y)
    w_orig = int(w * scale_x)
    h_orig = int(h * scale_y)

    # Crop the original image
    cropped_image = original_image[y_orig:y_orig + h_orig, x_orig:x_orig + w_orig]

    # Save the cropped image
    output_path = os.path.join(output_dir, f'cropped_{idx + 1}.png')
    cv2.imwrite(output_path, cropped_image)
    print(f"Saved cropped image to {output_path}")

print("Processing complete.")
