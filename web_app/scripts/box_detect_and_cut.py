from ultralytics import YOLO
from PIL import Image
import cv2
import os
import numpy as np
import csv
import pandas as pd

### Detection on images
## Description:
# Runs the object detection of image_path, draws the bounding box and saves the resulting images to output_full_path. If there was no object detection, appends the name of the image to the error_image list.

## Parameters:
# image_path: full path  of input images (directory + filename)
# output_full_path: full path of output (directory + filename)
# error_images: a list containing the names of images without detectable object
# image_name: name of the image file

def detection_on_image(image_full_path,output_full_path, error_images, image_name):
    print("DETECTING ON IMAGE:", image_name)
    # Run model prediction
    results = model(image_full_path)

    # If no object found
    if len(results) == 0:
        print(file, ": NO BOX")
        outlier_images.append(file)
        new_boxes.append(np.array([0,0,0,0]))

        # If box found with high enough confidence
    elif results[0].boxes.conf > min_score:
        r = results[0] 
        print("Confidence_score:", r.boxes.conf)
        # Get box coords
        box_coords = [int(x) for x in r.boxes.xyxy[0].tolist()]
        new_boxes.append(box_coords)
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        im.save(output_full_path)  # save image

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
    #model_path                   = os.path.join("model", "converted_model_train_9_100.h5")
    model_path                   = os.path.join(project_dir, "model", "classic.pt")

    # Load model and label properties
    globals()["model"]           = YOLO(model_path)
    
    # Placeholder for box parameters
    globals()["new_boxes"]       = []
    input_path  = orig_path

    # Create relative output paths
    output_path           = os.path.join(project_dir, 'images', 'box_images')
    crop_output           = os.path.join(project_dir, 'images','cropped_images')    ## output containing crop results ("box images")
    #box_coords_path       = os.path.join(project_dir, 'results', 'box_coords.csv')    ## your path to the csv file containing box coordinates
    cut_coords_path       = os.path.join(project_dir, 'results', 'cut_coords.csv')    ## your path to the csv file containing cut coordinates

    # H/W ration in case of rotating pictures
    height_to_width_ratio = 0.70

    # Placeholder lists
    coords_data           = []
    error_images          = []

    # RUN DETECTION ON ALL IMAGES IN THE INPUT FOLDER
    for file in os.listdir(input_path):
        
        # Define for paths
        input_full_path  = os.path.join(input_path,file)
        output_full_path = os.path.join(output_path,file)

        # Call detection_on_image function on each image
        detection_on_image(input_full_path,output_full_path, error_images, image_name = file)

    print("Box detection results saved to:" + output_path)
    #np.savetxt(box_coords_path, new_boxes, delimiter=',')  ### SAVE COORDS TO CSV
    #print("Box coordinates saved to:", box_coords_path)

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
                    coords_data.append([file[1], image.shape[1] - last_row, first_col, last_col])
                else:
                    cropped_image = image[first_col:last_col, last_row:first_row]
                    cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
                    coords_data.append([file[1], image.shape[1] - first_row, first_col, last_col])
    
            else:
                # Crop image based on box coordinates
                cropped_image = image[first_col:last_col, first_row:last_row]

                # Append cut coordinates to list
                coords_data.append([file[1], first_col, first_row, last_row])

            # Save "box image" to the relative output path
            crop_output_full_path = os.path.join(crop_output, file[1])
            cv2.imwrite(crop_output_full_path, cropped_image)
    
    # Save cut coordinates with the corresponding image name to a CSV file
    coords_df = pd.DataFrame(coords_data, columns =['img', 'top_y', 'top_left_x', 'top_right_x'])
    coords_df.to_csv(cut_coords_path, sep = ',', encoding = 'utf-8')
    
    #for i in range(0,len(image_names),1):
    #    coords_dict[image_names[i]] = coords[i]
    #
    #with open(cut_coords_path, 'w') as f_1:
    #    for key in coords_dict.keys():
    #        f_1.write("%s;%s\n"%(key,coords_dict[key]))
    
    print("Image cropping results saved to:" + crop_output)
    print("Cut coordinates saved to:", cut_coords_path)
    return error_images

if __name__ == '__main__':
    detect_and_cut("/home/eram/python_venv/images/original_images/", "/home/eram/python_venv/")
