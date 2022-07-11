
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


def get_session():
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.compat.v1.Session(config=config)

### Detection on images

min_score = 0.6
model_path = '/home/golah/converted_neural_models/converted_model_epoch_99.h5'  ## replace this with your model path
model = models.load_model(model_path, backbone_name='resnet50')
labels_to_names = {0:'whiteboard'}                    ## replace with your model labels and its index val

input_path = '/home/golah/COCO/TEST/'
output_path = '/home/golah/whiteboard_test_results/box_cord_test/'
unique_identifier = 'box_cord_test_'

new_boxes = []
csv_path = '/home/golah/box_coords_csv/converted_model_epoch_99/box_coords.csv'     ## your path to the csv file containing coordinates
crop_output = '/home/golah/crop_res/test/'            ## output containing crop results
height_to_width_ratio = 0.70
image_names = []
coords = []
save_results = True
def detection_on_image(image_path,output_full_path):
    
        image = cv2.imread(image_path)

        draw = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = preprocess_image(image)
        image, scale = resize_image(image)
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
        max_score = scores.max()
        boxes /= scale
        if np.all(scores[0] < min_score):
            print("NO BOX")
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
                color = label_color(label)
                b = box.astype(int)
                draw_box(draw, b, color=color)
                caption = "{} {:.3f}".format(labels_to_names[label], score)
                draw_caption(draw, b, caption)
                new_boxes.append(b.copy())
                detected_img =cv2.cvtColor(draw, cv2.COLOR_RGB2BGR)
                if save_results == True:
                    print("Box detection results saved to:" +output_full_path)
                    cv2.imwrite(output_full_path, detected_img)
        #cv2.imshow('Detection',detected_img)
        #cv2.waitKey(0)

### RUN DETECTION ON ALL IMAGES IN THE INPUT FOLDER

for file in os.listdir(input_path):
    input_full_path = os.path.join(input_path,file)
    output_full_path = os.path.join(output_path,(unique_identifier+file))
    detection_on_image(input_full_path,output_full_path)
    print(file + " DONE")

np.savetxt(csv_path, new_boxes, delimiter=',')  ### SAVE COORDS TO CSV

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
        print(new_boxes[file[0]])
        if new_boxes[file[0]][0] == 0:
            print("NO BOX")
            continue
        first_row = new_boxes[file[0]][0]  ## x-min
        first_col  = new_boxes[file[0]][1] ## y-min
        last_row = new_boxes[file[0]][2]   ## x-max
        last_col  = new_boxes[file[0]][3]  ## y-max
        # Check image's height to width ratio.
        # Más megoldással lehetne szűrni álló/fekvő képhelyzetet??
        print(image.shape[0], image.shape[1])
        if image.shape[0] / image.shape[1] < height_to_width_ratio:
            # Then rotate
            cropped_image = image[first_col:last_col, :last_row]
            cropped_image = cv2.rotate(cropped_image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            coords.append([image.shape[1] - last_row, first_col, last_col])
        else:
            cropped_image = image[first_col:, first_row:last_row]
            coords.append([first_col, first_row, last_row])
        image_names.append(file[1])
        if save_results == True:
            crop_output_full_path = os.path.join(crop_output, file[1])
            print("Image cropping results saved to:" + crop_output_full_path)
            cv2.imwrite(crop_output_full_path, cropped_image)

coords_dict = {}

for i in range(0,len(image_names),1):
    coords_dict[image_names[i]] = coords[i]

with open('cut_coords.csv', 'w') as f_1:
    for key in coords_dict.keys():
        f_1.write("%s;%s\n"%(key,coords_dict[key]))

print("Cut coordinates save to: cut_coords.csv")
