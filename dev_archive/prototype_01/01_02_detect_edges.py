#!/usr/bin/python
# Import packages2
import cv2
import numpy as np
import os
crop_output           = '/home/golah/whiteboard_project/projects/roland/images/cropped_images/'  ## output containing crop results
edge_detection_output = '/home/golah/whiteboard_project/projects/roland/images/edge_detected_images/'
save_results          = True

#### RUN CANNY EDGE DETECTION ON ALL CROPPED IMAGE
for file in os.listdir(crop_output):
    image_full_path = os.path.join(crop_output, file)
    # Make the image greyscale for better edge-detection
    image = cv2.imread(image_full_path, flags = 0)
    # Blurr the image
    #image_blurred = cv2.GaussianBlur(image,(3,3), cv2.BORDER_DEFAULT)
    image_blurred =  cv2.medianBlur(image, 7)
    # Canny edge detection
    print("Edge detection in progress....")
    image_edge = cv2.Canny(image=image_blurred, threshold1=00, threshold2=250)
    # One more blur + detection 
    image_edge      = cv2.cvtColor(image_edge, cv2.COLOR_GRAY2RGB)
    # Save results
    if save_results == True:
        edge_detection_full_output = os.path.join(edge_detection_output, file)
        cv2.imwrite(edge_detection_full_output, image_edge)

print("Edge detection results saved to:" + edge_detection_output)
