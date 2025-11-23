
#### REMOVING LINES ####

import cv2
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import AgglomerativeClustering
from PIL import Image # Ensure PIL Image is imported if not already

class eisko_extract:
    def __init__(self, cropped, n):
        img_symbols = eisko_extract.remove_lines(cropped)
        bboxes, img_with_boxes = eisko_extract.clustering(img_symbols)

        merged_bboxes = merge_bounding_boxes(bboxes, prox_threshold=10)
        merged_bboxes = merge_bounding_boxes(merged_bboxes, prox_threshold=20)
        merged_bboxes = merge_bounding_boxes(merged_bboxes, prox_threshold=20)
        print("Merged Bounding Boxes:", merged_bboxes)

        # Draw the merged bounding boxes on the image
        for bbox in merged_bboxes:
            x, y, w, h = bbox
            cv2.rectangle(img_with_boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle


        # Optionally, save the image with bounding boxes
        cv2.imwrite(f'image_with_merged_bboxes{n}.png', img_with_boxes)  # Save the image with bounding boxes

        pass

    def remove_lines(cropped):

        # Convert PIL Image to NumPy array for OpenCV operations.
        img_np_rgb = np.array(cropped)

        # Step 2: Convert to grayscale
        test_img_gray = cv2.cvtColor(img_np_rgb, cv2.COLOR_RGB2GRAY)

        # Step 1: Apply Gaussian Blur to smooth the image and reduce noise
        blurred_img = cv2.GaussianBlur(test_img_gray, (5, 5), 0)

        # Step 2: Apply Canny edge detection
        edges = cv2.Canny(blurred_img, 50, 150)

        # Step 6: Detect lines using Hough Line Transform on the preprocessed edges
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=108, maxLineGap=20)

        img_symbols = img_np_rgb.copy()  # Copy the original image to modify

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Draw white line to "erase" the detected lines
                cv2.line(img_symbols, (x1, y1), (x2, y2), (255, 255, 255), 2)

            return img_symbols


#### Bounding boxes: Clustering  #####

    def clustering(img_symbols):
        # Load the image
        img = img_symbols

        # Convert PIL Image to NumPy array and then to grayscale
        # PIL images are usually RGB, so convert from RGB to GRAY
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

        # Apply thresholding to get a binary image (white objects on black background)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Find contours (mode is RETR_EXTERNAL, method is CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Step 1: Calculate the centroids of each contour
        centroids = []

        for cnt in contours:
            # Get the bounding box for each contour
            x, y, w, h = cv2.boundingRect(cnt)

            # Calculate the centroid of the bounding box
            cx = x + w // 2
            cy = y + h // 2

            centroids.append([cx, cy])  # Store centroids as (x, y)

        centroids = np.array(centroids)
        cl_treshold = 80
        # Step 2: Apply Agglomerative Clustering to group the centroids
        agg_clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=cl_treshold)
        labels = agg_clustering.fit_predict(centroids)

        bounding_boxes = []  # List to store bounding boxes of each cluster

        # Step 3: Draw bounding boxes around each cluster
        # Convert PIL Image to NumPy array for OpenCV drawing operations
        img_with_boxes = np.array(img.copy())
        # Convert to BGR format for OpenCV drawing (if image is RGB initially)
        img_with_boxes = cv2.cvtColor(img_with_boxes, cv2.COLOR_RGB2BGR)

        # For each cluster, find all contours in that cluster and draw the bounding box
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:
                continue  # Skip noise points if they exist (not applicable in AgglomerativeClustering, no noise by default)

            # Find all contours belonging to this label
            cluster_contours = [contours[i] for i in range(len(contours)) if labels[i] == label]

            # Combine bounding boxes of all contours in the cluster
            # The previous error occurred here, attempting to use cv2.boundingRect on stacked (x,y,w,h) tuples.
            # Instead, we will directly compute the overall bounding box from individual contour bounding boxes.
            if cluster_contours:
                all_x = [cv2.boundingRect(c)[0] for c in cluster_contours]
                all_y = [cv2.boundingRect(c)[1] for c in cluster_contours]
                all_w = [cv2.boundingRect(c)[2] for c in cluster_contours]
                all_h = [cv2.boundingRect(c)[3] for c in cluster_contours]

                min_x = min(all_x)
                min_y = min(all_y)
                max_x = max([x + w for x, w in zip(all_x, all_w)])
                max_y = max([y + h for y, h in zip(all_y, all_h)])

                # Append the bounding box to the list in (x, y, w, h) format
                bounding_boxes.append((min_x, min_y, max_x - min_x, max_y - min_y))

                # Draw the bounding box around the cluster of contours on the image
                cv2.rectangle(img_with_boxes, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)  # Green rectangle

            return bounding_boxes, img_with_boxes


## OUTPUT: bounding_boxes
### END OF CLUSTERS ###



# Output the bounding boxes list

###  Bounding boxes: MERGE ####

#  Function to merge overlapping or touching bounding boxes
def merge_bounding_boxes(bboxes, prox_threshold):
    merged_boxes = []

    # Sort the bounding boxes by the x-coordinate
    bboxes = sorted(bboxes, key=lambda x: x[0])  # Sorting by x (left-most edge)

    while bboxes:
        # Start with the first bounding box
        current_bbox = bboxes.pop(0)
        x1, y1, w1, h1 = current_bbox

        # Try to merge with other bounding boxes
        merged = False
        for i in range(len(bboxes)):
            x2, y2, w2, h2 = bboxes[i]

            # Check if the bounding boxes are touching or overlapping
            if (x1 < x2 + w2 + prox_threshold and x1 + w1 + prox_threshold > x2 and
                y1 < y2 + h2 + prox_threshold and y1 + h1 + prox_threshold > y2):
                # Merge them by calculating the new bounding box that covers both
                x1 = min(x1, x2)
                y1 = min(y1, y2)
                w1 = max(x1 + w1, x2 + w2) - x1
                h1 = max(y1 + h1, y2 + h2) - y1

                # Remove the merged box
                bboxes.pop(i)
                merged = True
                break

            if (x2 < x1 + w1 + prox_threshold and x2 + w2 + prox_threshold > x1 and
                y2 < y1 + h1 + prox_threshold and y2 + h2 + prox_threshold > y1):
                # Merge them by calculating the new bounding box that covers both
                w1 = max(x1 + w1, x2 + w2)
                h1 = max(y1 + h1, y2 + h2)
                x1 = min(x1, x2)
                y1 = min(y1, y2)
                w1 = w1 - x1
                h1 = h1 - y1

                # Remove the merged box
                bboxes.pop(i)
                merged = True
                break

        # Append the merged box
        merged_boxes.append((x1, y1, w1, h1))

    return merged_boxes
## END OF THE FUNCTION BUT NOT WHOLE END ###

# Merge overlapping bounding boxes


## OUTPUT merged_bboxes
### END OF MERGING ####

## REST NOTEBOOK FLUFF HERE ##
# Output the merged bounding boxes


