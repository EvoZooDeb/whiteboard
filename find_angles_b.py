#!/usr/bin/python
import cv2
import numpy as np
import os
import math
import csv
import pandas as pd


edge_detection_output  = '/home/golah/template_match/test_templates/type_b' 
crop_template_output   = '/home/golah/template_match/line_drawn/type_b'
input_path = '/home/golah/COCO/TEST/'
height_to_width_ratio = 0.70
angles_left   = []
angles_right  = []
image_names_2 = []
str_data = []
orig_table_height = 130
orig_table_width  = 58.5
shortening_cm_ar = []
narrowing_cm_ar  = []
# Load coords from csv data
c_coords = pd.read_csv("cut_coords.csv", sep = ";", header = None, index_col = 0, squeeze = True).to_dict()
i_coords = pd.read_csv("i_coords.csv", sep = ";", header = None, index_col = 0, squeeze = True).to_dict()

# For every edge-detected image
for file in os.listdir(edge_detection_output):
    white_pixels_top   = []
    white_pixels_left  = []
    white_pixels_right = []
    cc    = c_coords[file].split(',')
    cc[0] = cc[0][1:]
    cc[2] = cc[2][:-1]
    ic    = i_coords[file].split(',')
    ic[0] = ic[0][1:]
    ic[2] = ic[2][:-1]
    image_full_path = os.path.join(edge_detection_output, file)
    image = cv2.imread(image_full_path, 0)

    # One more blur + detection
    image_edge_blur = cv2.medianBlur(image,7)
    image_edge_rep  = cv2.Canny(image_edge_blur, threshold1=00, threshold2=0)
    indices         = np.where(image_edge_rep != [0])
    coords          = np.array(list(zip(indices[1], indices[0])))
    image           = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    orig_image_full_path = os.path.join(input_path, file) 
    orig_image = cv2.imread(orig_image_full_path)
    orig_rows,orig_cols = orig_image.shape[:2]

    for i in coords:
        image[i[1]-3:i[1]+3, i[0]-3:i[0]+3] = (0, 0, 0)

### Draw the top line
    for i in range(1, 250, 1):
        cropped_image = image[i:i+15, :]
        n_white_pix_top = np.sum(cropped_image == 255)
        white_pixels_top.append(n_white_pix_top)

    max_white_pixels_top = np.sort(np.array(white_pixels_top))[-10:]

    for i in range(1, 250, 1):
        cropped_image = image[i:i+15, :]
        n_white_pix_top = np.sum(cropped_image == 255)
        if n_white_pix_top == max_white_pixels_top.max():
            indices = np.where(cropped_image != [0])
            coordinates = np.array(list(zip(indices[1], indices[0])))
            if len(coordinates) < 250:
                top_righty = 0
                top_lefty  = 0
                print("Not enought pixel in line: Corrected top line")
            top_detected_image = image[:, :]
            rows,cols = top_detected_image.shape[:2]
            # Line fitting
            [vx,vy,x,y] = cv2.fitLine(coordinates, cv2.DIST_L2,0,0.01,0.01)
            top_lefty = int((-x*vy/vx) + y)
            top_righty = int(((cols-x)*vy/vx)+y)
            x_axis      = np.array([1, 0])    # unit vector in the same direction as the x axis
            top_line    = np.array([float(vx), float(vy)])  # unit vector in the same direction as your line
            dot_product = np.dot(x_axis, top_line)
            angle_x   = np.arccos(dot_product)
            print("Top line's angle in degrees:", angle_x * 180 / math.pi)
            #top_coord_max = coordinates.max()
            #top_coord_min = coordinates.min()
            detected_image = cv2.line(top_detected_image,(cols-1,top_righty),(0,top_lefty),(255,0,0),2)
            break 


### Draw left line

    for i in range(1, 150, 1):
        cropped_image = top_detected_image[60:650, i:i+18]
        n_white_pix_left = np.sum(cropped_image == 255)
        white_pixels_left.append(n_white_pix_left)

    max_white_pixels_left = np.sort(np.array(white_pixels_left))[-10:]

    for i in range(1, 150, 1):
        cropped_image = top_detected_image[60:650, i:i+18]
        n_white_pix_left = np.sum(cropped_image == 255)
        if n_white_pix_left == max_white_pixels_left.max():
            indices = np.where(cropped_image != [0])
            coordinates = np.array(list(zip(indices[1], indices[0])))
            top_left_detected_image = top_detected_image[:, :]
            rows,cols = top_left_detected_image.shape[:2]
            if len(coordinates) != 0:
         # Line fitting
                [vx,vy,x,y] = cv2.fitLine(coordinates, cv2.DIST_L2,0,0.01,0.01)
                left_lefty  = int((-x*vy/vx) + y)
                left_righty = int(((cols-x)*vy/vx)+y)
            if len(coordinates) < 250:
                left_righty = 50000
                vy = [1]
                vx = [0]
                print("Warning at:", file, "Not enought pixel in line: Corrected left line")
            left_line   = np.array([vx, vy])  # unit vector in the same direction as your line
            dot_product = np.dot(top_line, left_line)
            angle_left   = np.arccos(dot_product)
            print("Left's line angle in degrees", angle_left * 180 / math.pi)
            if left_righty < 0:
                left_righty = left_righty * -1
            detected_image = cv2.line(detected_image,(cols-1,left_righty),(0,0),(0,255,0),2)
            angle_right = 3.14159265 - angle_left # 180 fokból kivonjuk
            print("Right's line angle in degrees", angle_right * 180 / math.pi)
            length = rows
            x, y = int(cols + length * math.cos(angle_right)), int(0 + length * math.sin(angle_right))
            detected_image = cv2.line(detected_image, (cols, 0), (x, y), (0, 0, 255), 2)

            ### Draw bottom line
            length = 2 * cols
            x1, y1 = int(0 + length * math.cos(angle_left)), int(0 + length * math.sin(angle_left))
            x2, y2 = int(cols + length * math.cos(angle_right)), int(0 + length * math.sin(angle_right))
            detected_image = cv2.line(detected_image, (x1, y1), (x2, y2), (150, 150, 0), 2)
            # Check original image's height to width ratio.
            # Más megoldással lehetne szűrni álló/fekvő képhelyzetet??
            if orig_image.shape[0] / orig_image.shape[1] < height_to_width_ratio:
                # Then rotate
                orig_image = cv2.rotate(orig_image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            # Transform the coordinates according the original image size
            X1    = 0 + int(cc[1]) + int(ic[1])
            X2    = X1 + cols
            Y1    = 0 + int(cc[0]) + int(ic[0])
            if y2 > y1:
                Y2 = Y1 + y2
            else:
                Y2 = Y1 + y2

            # Calculate width and height
            table_width = X2 - X1
            table_height = Y2 - Y1
            # Draw lines to original image
            length = table_width * 2
            x3, y1 = int(X1 + length * math.cos(angle_left)), int(Y1 + length * math.sin(angle_left))
            x4, y2 = int(X2 + length * math.cos(angle_right)), int(Y1 + length * math.sin(angle_right))
            #orig_image = cv2.line(orig_image, (X2, Y1), (X1, Y1), (255, 0, 0), 3) # Top
            #orig_image     = cv2.line(orig_image,(int(X1+x1),int(y1)), (int(X1), int(Y1)), (255, 0, 0) ,3) # Left
            #orig_image     = cv2.line(orig_image,(int(X2),int(y2)), (int(X2), int(Y1)), (255, 0, 0), 3) # Right
            #orig_image     = cv2.line(orig_image, (X1+x1, y1), (X2, y2), (255, 0, 0), 3)

            # Straight lines
            #orig_image = cv2.line(orig_image, (X1, Y2), (X1, Y1), (0, 0, 255), 3)
            #orig_image = cv2.line(orig_image, (X1, Y2), (X2, Y2), (0, 0, 255), 3)
            #orig_image = cv2.line(orig_image, (X2, Y1), (X2, Y2), (0, 0, 255), 3)
            
            # Tábla szűkebb belső sávjára vonal 
            narrowing  = table_width / 11  # Kb 5 cm
            shortening = table_height / 12.5
            #shortening = narrowing
            orig_image_cut_test = orig_image[Y1+int(shortening) : Y2, X1 : X2]
            #orig_image  = cv2.line(orig_image,(int(X1+x1+narrowing),int(y1)), (int(X1+narrowing), int(Y1+shortening)), (0, 0, 255) ,3) # Left
            #orig_image  = cv2.line(orig_image,(int(X2-narrowing),int(y2)), (int(X2-narrowing), int(Y1+shortening)), (255, 0, 0), 3) # Right
            orig_image_cut = orig_image[Y1 + int(shortening): Y2, X1 : X2]

            # Save angles (in deegre) and image names into csv file
            image_names_2.append(file)
            angles_left.append(angle_left * 180 / math.pi)
            angles_right.append(angle_right * 180 / math.pi)
            l = 20
            m = l / 2
            # Calculate average white shade
            h, w = orig_image_cut.shape[:2]
            print(file)
            
            # Transform
            tape_correction = 100
            narrowing_cm  = (narrowing + tape_correction) / w * orig_table_width
            shortening_cm = shortening / h * orig_table_height
            narrowing_cm_ar.append(narrowing_cm)
            shortening_cm_ar.append(shortening_cm)
            old_points  = np.array([[int(narrowing)+tape_correction, 0], [int(w-narrowing)-tape_correction, 0], [int(w-narrowing)-tape_correction, int(h)], [int(x1+narrowing)+tape_correction, int(h)]])
            table_shape = (int(w)-2*int(narrowing)-2*int(tape_correction), int(h))
            new_points  = np.array([[0,0], [table_shape[0]-1, 0], [table_shape[0]-1, table_shape[1]-1], [0, table_shape[1]-1]])
            M = cv2.getPerspectiveTransform(old_points.astype(np.float32), new_points.astype(np.float32))
            orig_image_cut = cv2.warpPerspective(orig_image_cut, M, table_shape)
            print(file, "DONE!")
            break


    crop_template_full_output = os.path.join(crop_template_output, file)
    cv2.imwrite(crop_template_full_output, orig_image_cut)

# Save angles and image names into csv
angles_left_dict  = {}
angles_right_dict = {}

for i in range(0,len(image_names_2),1):
    angles_left_dict[image_names_2[i]]  = angles_left[i]

for i in range(0,len(image_names_2),1):
    angles_right_dict[image_names_2[i]] = angles_right[i]

with open('left_angles_B.csv', 'w') as f:
    for key in angles_left_dict.keys():
        f.write("%s,%s\n"%(key,angles_left_dict[key]))

with open('right_angles_B.csv', 'w') as f_2:
    for key in angles_right_dict.keys():
        f_2.write("%s,%s\n"%(key,angles_right_dict[key]))

narrowing_cm_dict  = {}
shortening_cm_dict = {}

for i in range(0,len(image_names_2),1):
    narrowing_cm_dict[image_names_2[i]]  = narrowing_cm_ar[i]

for i in range(0,len(image_names_2),1):
    shortening_cm_dict[image_names_2[i]]  = shortening_cm_ar[i]

with open('narrowing_cm.csv', 'w') as f_3:
    for key in narrowing_cm_dict.keys():
        f_3.write("%s,%s\n"%(key,narrowing_cm_dict[key]))

with open('shortening.csv', 'w') as f_4:
    for key in shortening_cm_dict.keys():
        f_4.write("%s,%s\n"%(key,shortening_cm_dict[key]))
