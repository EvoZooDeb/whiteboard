#!/usr/bin/python
import cv2
import numpy as np
import os
import csv
from matplotlib import pyplot as plt
import math
import pandas as pd

edge_detection_output = '/home/golah/whiteboard_project/projects/roland/images/edge_detected_images/'
crop_template_output  = '/home/golah/whiteboard_project/projects/roland/images/template_images/'
input_path            = '/home/golah/whiteboard_project/projects/roland/images/original_images/'
crop_output           = '/home/golah/whiteboard_project/projects/roland/images/cropped_images/'
height_to_width_ratio = 0.70
top_left_coords       = []
top_right_coords      = []
image_names_1         = []
coords_cut            = []
save_image_results    = True
# Load coords from csv data
c_coords = pd.read_csv("/home/golah/whiteboard_project/projects/roland/results/cut_coords.csv", sep = ";", header = None, index_col = 0, squeeze = True).to_dict()

# Run on each edge detected image
for file in os.listdir(edge_detection_output):
    print(file)
    cc                  = c_coords[file].split(',')
    cc[0]               = cc[0][1:]
    cc[2]               = cc[2][:-1]
    i_coords            = []
    white_rows_top      = []
    white_rows_left     = []   
    white_rows_right    = []
    image_full_path     = os.path.join(edge_detection_output, file)
    image               = cv2.imread(image_full_path)

### Find the top of the table
# Find part with maximum white pixel
    for i in range(1, 150, 5):
        cropped_image = image[i:i + 10, :]
        h, w          = cropped_image.shape[:2]
        x_top         = []
        for x in range(0, int(w), 1):
            for y in range(0, h, 1):
                if cropped_image[y][x][0] > 250:
                    x_top.append(x)
                    break
        white_rows_top.append(len(x_top))
    max_white_rows_top   = np.array(white_rows_top).max()


    for t in range(1, 150, 5):
        cropped_image = image[t:t + 10, :]
        h, w          = cropped_image.shape[:2]
        n_x_top       = []
        n_y_top       = []
        for x in range(0, int(w), 1):
            for y in range(0, h, 1):
                if cropped_image[y][x][0] > 250:
                    n_x_top.append(x)
                    n_y_top.append(y)
                    break
        n_white_rows_top = len(n_x_top)
        if n_white_rows_top == max_white_rows_top:
            if n_white_rows_top < 10:
                print("Not enough pixel in topline")
                i_coords         = []
                break
# Determine top corners
            y_min_t            = np.array(n_y_top).min()
            y_max_t            = np.array(n_y_top).max()
            max_i              = n_y_top.index(max(n_y_top))
            min_i              = n_y_top.index(min(n_y_top))
            i_top              = t + y_min_t
            i_top_max          = t + y_max_t
            top_detected_image = image[i_top:, :]
            i_coords.append(i_top)
            x_at_y_max = n_x_top[max_i]
            x_at_y_min = n_x_top[min_i]
            if x_at_y_max > x_at_y_min:
                top_left   = [x_at_y_min + int(cc[1]), i_top + int(cc[0])]
                top_right  = [int(cc[2]) - x_at_y_max, i_top_max + int(cc[0])]
            else:
                top_right  = [int(cc[2]) - x_at_y_min, i_top + int(cc[0])]
                top_left   = [x_at_y_max + int(cc[1]), i_top_max + int(cc[0])]
            break

### Find left side
# Find part with maximum white pixel
    for i in range(1, 100, 6):
        cropped_image = top_detected_image[t + 100:650, i:i + 42]
        h, w          = cropped_image.shape[:2]
        y_left        = []
        for y in range(0, int(h), 1):
            for x in range(0, w, 1):
                if cropped_image[y][x][0] > 250:
                    y_left.append(y + t + 100)
                    break
        white_rows_left.append(len(y_left))
    max_white_rows_left   = np.array(white_rows_left).max()


    for l in range(1, 100, 6):
        cropped_image = top_detected_image[t + 100:650, l:l + 42]
        h, w          = cropped_image.shape[:2]
        n_y_left      = []
        n_x_left      = []
        for y in range(0, int(h), 1):
            for x in range(0, w, 1):
                if cropped_image[y][x][0] > 250:
                    n_y_left.append(y + t + 100)
                    n_x_left.append(x + l)
                    break
        n_white_rows_left = len(n_y_left)
        if n_white_rows_left == max_white_rows_left:
            if n_white_rows_left < 20:
                print("Warning at:", file, "Not enough pixel in left side.")
                i_coords         = []
                break
            x_min_l = np.array(n_x_left).min()
            i_left  = l + x_min_l
            i_coords.append(i_left)
            top_left_detected_image = top_detected_image[:, i_left:]
            break
    if len(i_coords) < 2:
        continue

### Find right side
# Find part with maximum white pixel
    for i in range(-1, -100, -6):
        cropped_image = top_left_detected_image[t + 100:650, i - 30:i]
        h, w          = cropped_image.shape[:2]
        y_right       = []
        for y in range(0, int(h), 1):
            for x in range (w-1, -1, -1):
                if cropped_image[y][x][0] > 250:
                    y_right.append(y + t + 100)
                    break
        white_rows_right.append(len(y_right))
    max_white_rows_right   = np.array(white_rows_right).max()

    for r in range(-1, -100, -6):
        cropped_image = top_left_detected_image[t + 100:650, r - 30:r]
        h, w          = cropped_image.shape[:2]
        n_y_right     = []
        n_x_right     = []
        for y in range(0, int(h), 1):
            for x in range(w-1, -1, -1):
                if cropped_image[y][x][0] > 250:
                    n_y_right.append(y + t + 100)
                    n_x_right.append(w - x)
                    break
        n_white_rows_right = len(n_y_right)
        if n_white_rows_right == max_white_rows_right:
            if n_white_rows_right < 20:
                print("Warning at:", file, "Not enough pixel in right side.")
                i_coords         = []
                break
            x_max_r  = np.array(n_x_right).max()
            i_right  = r - x_max_r
            if i_right == 0:
                i_right = w
            i_coords.append(i_right)
            detected_image = top_left_detected_image[:, :i_right]
            #cv2.imshow("Top_detected", detected_image)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()
            break
    if len(i_coords) < 3:
        continue
    # Append corners and image names into a dictionary
    coords_cut.append([i_coords[0], i_coords[1], i_coords[2]])
    top_left_coords.append(top_left)
    image_names_1.append(file)
    top_right_coords.append(top_right)
    
    # Save results
    if save_image_results == True:
            crop_template_full_output = os.path.join(crop_template_output + file)
            cv2.imwrite(crop_template_full_output, detected_image)
    
print("Corner finding results saved to:" + crop_template_output)

# Save corners and image names into csv
top_left_dict  = {}
top_right_dict = {}

for i in range(0,len(image_names_1),1):
    top_left_dict[image_names_1[i]]  = top_left_coords[i]

for i in range(0,len(image_names_1),1):
    top_right_dict[image_names_1[i]] = top_right_coords[i]

with open('/home/golah/whiteboard_project/projects/roland/results/top_left.csv', 'w') as f:
    for key in top_left_dict.keys():
        f.write("%s,%s\n"%(key,top_left_dict[key]))

with open('/home/golah/whiteboard_project/projects/roland/results/top_right.csv', 'w') as f_2:
    for key in top_right_dict.keys():
        f_2.write("%s,%s\n"%(key,top_right_dict[key]))

cut_coords = {}

for i in range(0,len(image_names_1),1):
    cut_coords[image_names_1[i]] = coords_cut[i]

with open('/home/golah/whiteboard_project/projects/roland/results/i_coords.csv', 'w') as f_3:
    for key in cut_coords.keys():
        f_3.write("%s;%s\n"%(key,cut_coords[key]))
