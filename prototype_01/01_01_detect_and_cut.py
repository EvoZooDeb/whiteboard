
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
from matplotlib import pyplot as plt
import csv
from PIL import ExifTags

def get_session():
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.compat.v1.Session(config=config)

### Define parameters
min_score             = 0.6
model_path            = '/home/golah/whiteboard_project/machine_learning/converted_neural_models/converted_model_train_5_100.h5'  ## replace this with your model path
model                 = models.load_model(model_path, backbone_name='resnet50')
labels_to_names       = {0:'whiteboard'}                    ## replace with your model labels and its index val
input_path            = '/home/golah/whiteboard_project/projects/roland/images/original_images/'
output_path           = '/home/golah/whiteboard_project/projects/roland/images/box_images/'
new_boxes             = []
box_coords_path       = '/home/golah/whiteboard_project/projects/roland/results/box_coords.csv'     ## your path to the csv file containing box coordinates
outlier_images_path   = '/home/golah/whiteboard_project/projects/roland/results/outlier_names.csv'  ## your path to the csv file containing outlier names
cut_coords_path       = '/home/golah/whiteboard_project/projects/roland/results/cut_coords.csv'     ## your path to the csv file containing cut coordinates
crop_output           = '/home/golah/whiteboard_project/projects/roland/images/cropped_images/'     ## output containing crop results
height_to_width_ratio = 0.70
image_names           = []
outlier_images        = []
coords                = []
save_results = True

### Detection on images
def detection_on_image(image_path,output_full_path):
        image = cv2.imread(image_path)
        draw  = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = preprocess_image(image)
        h, w  = image.shape[:2]

        # Resize based on image position
        if  h/w > 1.34:
            image, scale = resize_image(image, min_side = 1425, max_side = 800)
        elif w/h > 1.34:
            image, scale = resize_image(image, min_side = 800, max_side = 1425)
        else:
            image, scale = resize_image(image)

        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
        max_score             = scores.max()
        boxes /= scale

        if np.all(scores[0] < min_score):
            print(file, ": NO BOX")
            outlier_images.append(file)
            new_boxes.append(np.array([0,0,0,0]))
        else:    
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
                if save_results == True:
                    cv2.imwrite(output_full_path, detected_img)
        #cv2.imshow('Detection',detected_img)
        #cv2.waitKey(0)

### RUN DETECTION ON ALL IMAGES IN THE INPUT FOLDER

for file in os.listdir(input_path):
    input_full_path = os.path.join(input_path,file)
    output_full_path = os.path.join(output_path, file)
    detection_on_image(input_full_path,output_full_path)
    print(file + " DONE")

if save_results == True:
    print("Box detection results saved to:" + output_path)
np.savetxt(box_coords_path, new_boxes, delimiter=',')  ### SAVE COORDS TO CSV
print("Box coordinates saved to:", box_coords_path)
### Save outlier names
with open(outlier_images_path, 'w') as f_0:
    for i in outlier_images:
        f_0.write("%s\n"% i)
print("List of images without detected box saved to:", outlier_images_path)


# Csak ha az újonnan előállíttott outputtal akarunk dolgozni
# Get list of all files only in the given directory. ## output_path ha a "négyzetes" képekkel akarunk dolgozni, input_path ha a simával.
#list_of_files = filter( lambda x: os.path.isfile(os.path.join(input_path, x)),
#                        os.listdir(input_path) )
# Sort list of files based on last modification time in ascending order
#list_of_files = sorted( list_of_files,
#                        key = lambda x: os.path.getmtime(os.path.join(input_path, x))
#                        )

### CUT OUT THE TABLES ACCORDING TO THE BOX COORDINATES

#for file in enumerate(list_of_files):
for file in enumerate(os.listdir(input_path)):
        print("Cropping the images...")
        output_full_path = os.path.join(input_path, file[1])
        image = cv2.imread(output_full_path)
        if new_boxes[file[0]][0] == 0:
            print(file, ": NO BOX")
            continue
        first_row  = new_boxes[file[0]][0] ## x-max
        first_col  = new_boxes[file[0]][1] ## y-max
        last_row   = new_boxes[file[0]][2] ## x-min
        last_col   = new_boxes[file[0]][3] ## y-min
        # Check image's height to width ratio.
        h, w = image.shape[:2]
        if h / w < height_to_width_ratio:
            print("ROTATE")
            if first_row > w / 2:
                cropped_image = image[first_col:last_col, :last_row]
                cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                coords.append([image.shape[1] - last_row, first_col, last_col])
            else:
                cropped_image = image[first_col:last_col, :first_row]
                cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
                coords.append([image.shape[1] - first_row, first_col, last_col])

        else:
            cropped_image = image[first_col:, first_row:last_row]
            coords.append([first_col, first_row, last_row])
        image_names.append(file[1])
        if save_results == True:
            crop_output_full_path = os.path.join(crop_output, file[1])
            cv2.imwrite(crop_output_full_path, cropped_image)

coords_dict = {}

### Save cut coordinates
for i in range(0,len(image_names),1):
    coords_dict[image_names[i]] = coords[i]

with open(cut_coords_path, 'w') as f_1:
    for key in coords_dict.keys():
        f_1.write("%s;%s\n"%(key,coords_dict[key]))

print("Image cropping results saved to:" + crop_output)
print("Cut coordinates saved to:", cut_coords_path)
