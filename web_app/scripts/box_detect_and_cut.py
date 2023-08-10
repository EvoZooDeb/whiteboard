import keras
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
import cv2
import os
import numpy as np
import time
import tensorflow as tf
import math
import csv

### Detection on images
## Description:
# Runs the object detection of image_path, draws the bounding box and saves the resulting images to output_full_path. If there was no object detection, appends the name of the image to the error_image list.

## Parameters:
# image_path: full path  of input images (directory + filename)
# output_full_path: full path of output (directory + filename)
# error_images: a list containing the names of images without detectable object
# image_name: name of the image file

def detection_on_image(image_path,output_full_path, error_images, image_name):
        print("DETECTING ON IMAGE:", image_name)
        # Load and preprocess image
        image                 = cv2.imread(image_path)
        draw                  = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image                 = preprocess_image(image)

        # Get parameters
        h, w                  = image.shape[:2]
        image, scale          = resize_image(image)

        # Run model prediction
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

        # Select prediction with best score
        max_score             = scores.max()
        boxes /= scale

        # If no score sufficent:
        if np.all(scores[0] < min_score):
            print(image_name, ": NO BOX")
            error_images.append(image_name)
            new_boxes.append(np.array([0,0,0,0]))
        else:    
           # Select the best box
           for box, score, label in zip(boxes[0], scores[0], labels[0]):
                if score < max_score:
                    break
                if score < min_score:
                    break
                
                print("Confidence_score:", score)
                print("Label:", labels_to_names[label])
                
                # Draw box
                color   = label_color(label)
                b       = box.astype(int)
                draw_box(draw, b, color=color)
                caption = "{} {:.3f}".format(labels_to_names[label], score)
                draw_caption(draw, b, caption)
                new_boxes.append(b.copy())
                detected_img = cv2.cvtColor(draw, cv2.COLOR_RGB2BGR)
                cv2.imwrite(output_full_path, detected_img)

### Detection and cut
## Description:
# Runs the detection_on_images on orig_path, then crops out the part of the image inside the bounding box resulting in "box images". Saves box and cut coords to project_dir/results and result images to project_dir/images/...

## Parameters:
# orig_path: full path  of input images (directory + filename)
# project_dir: project directory path, read documentation at https://github.com/EvoZooDeb/whiteboard. 

## Returns:
# error_images: a list containing the names of images without detectable object

def detect_and_cut(orig_path, project_dir):
    # Define parameters:

    # Minimum confidence score of object detection
    globals()["min_score"]       = 0.6

    # The models relative path to project dir
    model_path                   = os.path.join(project_dir, "model", "converted_model_train_9_100.h5")

    # Load model and label properties
    globals()["model"]           = models.load_model(model_path, backbone_name='resnet50')
    globals()["labels_to_names"] = {0:'whiteboard'}                    ##  labels and its index val
    
    # Placeholder for box parameters
    globals()["new_boxes"]       = []

    input_path  = orig_path

    # Create relative output paths
    output_path           = os.path.join(project_dir, 'images', 'box_images')
    crop_output           = os.path.join(project_dir, 'images','cropped_images')    ## output containing crop results ("box images")
    box_coords_path       = os.path.join(project_dir, 'results', 'box_coords.csv')    ## your path to the csv file containing box coordinates
    cut_coords_path       = os.path.join(project_dir, 'results', 'cut_coords.csv')    ## your path to the csv file containing cut coordinates

    # H/W ration in case of rotating pictures
    height_to_width_ratio = 0.70

    # Placeholder lists
    image_names           = []
    error_images          = []
    coords                = []

    # RUN DETECTION ON ALL IMAGES IN THE INPUT FOLDER
    for file in os.listdir(input_path):
        
        # Define for paths
        input_full_path  = os.path.join(input_path,file)
        output_full_path = os.path.join(output_path,file)

        # Call detection_on_image function on each image
        detection_on_image(input_full_path,output_full_path, error_images, image_name = file)

    print("Box detection results saved to:" + output_path)
    np.savetxt(box_coords_path, new_boxes, delimiter=',')  ### SAVE COORDS TO CSV
    print("Box coordinates saved to:", box_coords_path)

### CUT OUT THE TABLES ACCORDING TO THE BOX COORDINATES
    # For each image in input_path
    for file in enumerate(os.listdir(input_path)):
            print("Cropping the images...")

            # Load image
            output_full_path = os.path.join(input_path, file[1])
            image            = cv2.imread(output_full_path)

            # If there is no corresponding box coordinate for the image, try next image.
            if new_boxes[file[0]][0] == 0:
                print(file[1], ": NO BOX")
                continue

            # Get coordinates
            first_row  = new_boxes[file[0]][0] ## x-max
            first_col  = new_boxes[file[0]][1] ## y-max
            last_row   = new_boxes[file[0]][2] ## x-min
            last_col   = new_boxes[file[0]][3] ## y-min
            
            # Check image's height to width ratio.
            h, w       = image.shape[:2]
            if h / w < height_to_width_ratio:

                # Rotate image if needed (and crop afterwards)
                if first_row > w / 2:
                    cropped_image = image[first_col:last_col, first_row:last_row]
                    cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    coords.append([image.shape[1] - last_row, first_col, last_col])
                else:
                    cropped_image = image[first_col:last_col, last_row:first_row]
                    cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
                    coords.append([image.shape[1] - first_row, first_col, last_col])
    
            else:
                # Crop image based on box coordinates
                cropped_image = image[first_col:last_col, first_row:last_row]

                # Append cut coordinates to list
                coords.append([first_col, first_row, last_row])

            image_names.append(file[1])

            # Save "box image" to the relative output path
            crop_output_full_path = os.path.join(crop_output, file[1])
            cv2.imwrite(crop_output_full_path, cropped_image)
    
    # Save cut coordinates with the corresponding image name to a CSV file
    coords_dict = {}
    
    for i in range(0,len(image_names),1):
        coords_dict[image_names[i]] = coords[i]
    
    with open(cut_coords_path, 'w') as f_1:
        for key in coords_dict.keys():
            f_1.write("%s;%s\n"%(key,coords_dict[key]))
    
    print("Image cropping results saved to:" + crop_output)
    print("Cut coordinates saved to:", cut_coords_path)
    return error_images

if __name__ == '__main__':
    detect_and_cut("/home/eram/python_venv/images/original_images/", "/home/eram/python_venv/")
