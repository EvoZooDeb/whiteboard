#!/usr/bin/python
import cv2
import numpy as np
import os
import csv
from matplotlib import pyplot as plt
import math
import pandas as pd

edge_detection_output = '/home/golah/edge_detection/images/'
crop_template_output  = '/home/golah/template_match/test_templates/'
input_path = '/home/golah/COCO/TEST/'
crop_output = '/home/golah/crop_res/test/'
height_to_width_ratio = 0.70
top_left_coords    = []
top_right_coords   = []
image_names_1      = []
coords_cut         = []
save_image_results = True

for file in os.listdir(edge_detection_output):
    white_pixels_top = []
    white_pixels_left = []
    white_pixels_right = []
    i_coords         = []
    rotated = False 
    image_full_path = os.path.join(edge_detection_output, file)
    orig_image_full_path = os.path.join(input_path, file)
    cropped_image_full_path = os.path.join(crop_output, file)
    image = cv2.imread(image_full_path, 0)
    orig_image = cv2.imread(orig_image_full_path, 0)
    cropped_image_nd = cv2.imread(cropped_image_full_path, 0)

### Find the top of the table

    for i in range(1, 250, 3):
        cropped_image = image[i:i+15, :]
        n_white_pix_top = np.sum(cropped_image == 255)
        white_pixels_top.append(n_white_pix_top)

    max_white_pixels_top = np.sort(np.array(white_pixels_top))[-10:]

    for i in range(1, 250, 3):
        cropped_image = image[i:i+15, :]
        n_white_pix_top = np.sum(cropped_image == 255)
        if n_white_pix_top == max_white_pixels_top.max():
            indices = np.where(cropped_image != [0])
            coordinates = np.array(list(zip(indices[1], indices[0])))
            if len(coordinates) < 250:
                top_righty = 0
                top_lefty  = 0
                print("Not enought pixel in line: Corrected top line")
            top_detected_image = image[i:, :]
            i_coords.append(i)
            # Line fitting - itt szükséges, diff miatt
            rows,cols = top_detected_image.shape[:2]
            [vx,vy,x,y] = cv2.fitLine(coordinates, cv2.DIST_L2,0,0.01,0.01)
            top_lefty = int((-x*vy/vx) + y)
            top_righty = int(((cols-x)*vy/vx)+y)
            #top_coord_max = coordinates.max()
            #top_coord_min = coordinates.min()
            if top_lefty > top_righty:
                top_diff_left  = top_lefty - top_righty
                top_diff_right = 0
            else:
                top_diff_right = top_righty - top_lefty
                top_diff_left  = 0
            break

    
### Find left side
    for i in range(1, 125, 3):
        cropped_image = top_detected_image[0:625, i:i+48]
        n_white_pix_left = np.sum(cropped_image == 255)
        white_pixels_left.append(n_white_pix_left)

    max_white_pixels_left = np.sort(np.array(white_pixels_left))[-10:]

    for i in range(1, 125, 3):
        cropped_image = top_detected_image[0:625, i:i+48]
        n_white_pix_left = np.sum(cropped_image == 255)
        if n_white_pix_left == max_white_pixels_left.max():
            indices = np.where(cropped_image != [0])
            coordinates = np.array(list(zip(indices[1], indices[0])))
            if len(coordinates) == 0:
                print("Not enought pixel in line")
                i_coords         = []
                break
            top_left_detected_image = top_detected_image[:, i:]
            rows,cols = top_left_detected_image.shape[:2]
            i_coords.append(i)
            break

    if len(i_coords) == 0:
        continue
### Find right side
    for i in range(-1, -125, -3):
        cropped_image = top_left_detected_image[0:625, i-48:i]
        n_white_pix_right = np.sum(cropped_image == 255)
        white_pixels_right.append(n_white_pix_right)

    max_white_pixels_right = np.sort(np.array(white_pixels_right))[-10:]

    for i in range(-1, -125, -3):
        cropped_image = top_left_detected_image[0:625, i-48:i]
        n_white_pix_right = np.sum(cropped_image == 255)
        if n_white_pix_right == max_white_pixels_right.max():            
            detected_image = top_left_detected_image[:, :i]
            rows,cols = detected_image.shape[:2]
            indices = np.where(cropped_image != [0])
            coordinates = np.array(list(zip(indices[1], indices[0])))
            if len(coordinates) == 0:
                print("Not enought pixel in line")
                i_coords         = []
                break
            i_coords.append(i)
            break
    
    ### Template matching
    img2 = image.copy()
    template = detected_image
    w, h = template.shape[::-1]

    # All the 6 methods for comparison in a list
    #methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
    #        'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    
    #for meth in methods:
    img = img2.copy()
    #method = eval(meth)
    method = eval('cv2.TM_CCOEFF')
    # Apply template Matching
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        #if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        #    top_left = min_loc
        #else:
    top_left = max_loc
    top_right = (top_left[0] + w, top_left[1])
    #cv2.rectangle(img,top_left, bottom_right, 255, 2)
    #plt.subplot(121),plt.imshow(res,cmap = 'gray')
    #plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    #plt.subplot(122),plt.imshow(img,cmap = 'gray')
    #plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    #plt.suptitle('cv.TM_CCOEFF')
    #plt.show()

    ### Cut cropped image according to template coords and make a new template out of it
    cropped_image_nd = cropped_image_nd[top_left[1]:, top_left[0]:top_left[0] + w] 
    template2 = cropped_image_nd
    w, h = template2.shape[::-1]
   
   ### Template match on the original picture using the new template
    # Check original image's height to width ratio.
    if orig_image.shape[0] / orig_image.shape[1] < height_to_width_ratio:
            # Then rotate
        orig_image = cv2.rotate(orig_image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
        rotated = True
    img3 = orig_image.copy()
    method = eval('cv2.TM_CCOEFF')
    # Apply template Matching
    res = cv2.matchTemplate(img3,template2,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left  = max_loc
    top_right = (top_left[0] + w, top_left[1])
    #cv2.rectangle(img3,top_left, bottom_right, 255, 2)
    #plt.subplot(121),plt.imshow(res,cmap = 'gray')
    #plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    #plt.subplot(122),plt.imshow(img3,cmap = 'gray')
    #plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    #plt.suptitle('cv.TM_CCOEFF')
    #plt.show()
    
    # Append corners and image names into a dictionary
    coords_cut.append([i_coords[0], i_coords[1], i_coords[2]])
    top_left_coords.append([top_left[0], top_left[1] + top_diff_left])
    image_names_1.append(file)
    top_right_coords.append([top_right[0], top_right[1] + top_diff_right])
    
    # Save results
    if save_image_results == True:
        if rotated == False:
            crop_template_full_output = os.path.join((crop_template_output + "/type_b/"), file)
            print("Corner finding results saved to:" + crop_template_full_output)
            cv2.imwrite(crop_template_full_output, detected_image)
        else:
            crop_template_full_output = os.path.join((crop_template_output + "/type_a/"), file)
            print("Corner finding results saved to:" + crop_template_full_output)
            cv2.imwrite(crop_template_full_output, detected_image)
    
    # Orignal image cut by the upper corners
    #orig_image_cut = orig_image[top_left[1]:, top_left[0] : top_left[0] + w]
    #cv2.imwrite(crop_template_full_output, orig_image_cut)

# Save corners and image names into csv
top_left_dict  = {}
top_right_dict = {}

for i in range(0,len(image_names_1),1):
    top_left_dict[image_names_1[i]]  = top_left_coords[i]

for i in range(0,len(image_names_1),1):
    top_right_dict[image_names_1[i]] = top_right_coords[i]

with open('top_left.csv', 'w') as f:
    for key in top_left_dict.keys():
        f.write("%s,%s\n"%(key,top_left_dict[key]))

with open('top_right.csv', 'w') as f_2:
    for key in top_right_dict.keys():
        f_2.write("%s,%s\n"%(key,top_right_dict[key]))

cut_coords = {}

for i in range(0,len(image_names_1),1):
    cut_coords[image_names_1[i]] = coords_cut[i]

with open('i_coords.csv', 'w') as f_3:
    for key in cut_coords.keys():
        f_3.write("%s;%s\n"%(key,cut_coords[key]))
