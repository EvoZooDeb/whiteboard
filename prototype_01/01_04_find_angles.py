#!/usr/bin/python
import cv2
import numpy as np
import os
import math
import csv
import pandas as pd

# Define parameters
corner_detection_output  = '/home/golah/whiteboard_project/projects/roland/images/template_images/' 
transform_output         = '/home/golah/whiteboard_project/projects/roland/images/transformed_images/'
input_path               = '/home/golah/whiteboard_project/projects/roland/images/original_images/'
height_to_width_ratio    = 0.70
angles_left              = []
angles_right             = []
image_names_2            = []
str_data                 = []
orig_table_height        = 130
orig_table_width         = 58.5
shortening_cm_ar         = []
narrowing_cm_ar          = []

# Load coords from csv data
c_coords = pd.read_csv("/home/golah/whiteboard_project/projects/roland/results/cut_coords.csv", sep = ";", header = None, index_col = 0, squeeze = True).to_dict()
i_coords = pd.read_csv("/home/golah/whiteboard_project/projects/roland/results/i_coords.csv", sep = ";", header = None, index_col = 0, squeeze = True).to_dict()

# For every corner-detected image
for file in os.listdir(corner_detection_output):
    white_rows_top      = []
    white_rows_left     = []
    white_rows_right    = []
    cc                  = c_coords[file].split(',')
    cc[0]               = cc[0][1:]
    cc[2]               = cc[2][:-1]
    ic                  = i_coords[file].split(',')
    ic[0]               = ic[0][1:]
    ic[2]               = ic[2][:-1]
    image_full_path     = os.path.join(corner_detection_output, file)
    image               = cv2.imread(image_full_path, 0)

    # One more blur + detection
    image_edge_blur      = cv2.medianBlur(image,7)
    image_edge_rep       = cv2.Canny(image_edge_blur, threshold1=00, threshold2=0)
    indices              = np.where(image_edge_rep != [0])
    coords               = np.array(list(zip(indices[1], indices[0])))
    image                = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    orig_image_full_path = os.path.join(input_path, file) 
    orig_image           = cv2.imread(orig_image_full_path)
    orig_rows,orig_cols  = orig_image.shape[:2]
    for i in coords:
        image[i[1]-0:i[1]+1, i[0]-5:i[0]+5] = (0, 0, 0)
### Draw the top line
    for i in range(1, 150, 5):
        cropped_image = image[i:i+10, :]
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
        cropped_image = image[t:t+10, :]
        h, w          = cropped_image.shape[:2]
        n_x_top       = []
        for x in range(0, int(w), 1):
            for y in range(0, h, 1):
                if cropped_image[y][x][0] > 250:
                    n_x_top.append(x)
                    break
        n_white_rows_top = len(n_x_top)
        if n_white_rows_top == max_white_rows_top:
            indices = np.where(cropped_image != [0])
            coordinates = np.array(list(zip(indices[1], indices[0])))
            if len(coordinates) < 250:
                top_righty = 0
                top_lefty  = 0
                print("Not enought pixel in line: Corrected top line")
            top_detected_image = image[:, :]
            rows,cols          = top_detected_image.shape[:2]
            # Line fitting
            [vx,vy,x,y] = cv2.fitLine(coordinates, cv2.DIST_L2,0,0.01,0.01)
            top_lefty   = int((-x*vy/vx) + y)
            top_righty  = int(((cols-x)*vy/vx)+y)
            x_axis      = np.array([1, 0])                  # unit vector in the same direction as the x axis
            top_line    = np.array([float(vx), float(vy)])  # unit vector in the same direction as top line
            dot_product = np.dot(x_axis, top_line)
            # Get angle
            angle_x     = np.arccos(dot_product)
            print("Top line's angle in degrees:", angle_x * 180 / math.pi)
            detected_image = cv2.line(top_detected_image,(cols-1,top_righty+t),(0,top_lefty+t),(255,0,0),2)
            break 


### Draw left line
    for i in range(1, 100, 6):
        cropped_image = top_detected_image[t+100:650, i:i+42]
        h, w          = cropped_image.shape[:2]
        y_left        = []
        for y in range(0, int(h), 1):
            for x in range(w-1, -1, -1):
                if cropped_image[y][x][0] > 250:
                    y_left.append(y+t+100)
                    break
        white_rows_left.append(len(y_left))
    max_white_rows_left   = np.array(white_rows_left).max()

    for l in range(1, 100, 6):
        cropped_image    = top_detected_image[t+100:650, l:l+42]
        n_white_pix_left = np.sum(cropped_image == 255)
        h, w             = cropped_image.shape[:2]
        n_y_left         = []
        n_x_left         = []
        for y in range(0, int(h), 1):
            for x in range(w-1, -1, -1):
                if cropped_image[y][x][0] > 250:
                    n_y_left.append(y+t+100)
                    n_x_left.append(x+l)
                    break
        n_white_rows_left = len(n_y_left)
        if n_white_rows_left == max_white_rows_left:
            if len(n_y_left) > 20:
                angles_test = []
                for i in range(0, int(len(n_y_left)/4), 1):
                    yminl     = n_y_left[i]
                    ymaxl     = n_y_left[-i-1]
                    xminl     = n_x_left[i]
                    xmaxl     = n_x_left[-i-1]
                    atan      = math.atan2(ymaxl - yminl, xmaxl - xminl)
                    angle     = math.degrees(atan)
                    angle_rad = angle * math.pi / 180
                    angles_test.append(angle_rad)
                angles_avg = np.mean(angles_test)
                y_min_l    = np.array(n_y_left).min()
                y_max_l    = np.array(n_y_left).max()
                x_min_l    = n_x_left[0]
                x_max_l    = n_x_left[-1]
                atan       = math.atan2(y_max_l -y_min_l, x_max_l - x_min_l)
                top_left_detected_image = top_detected_image[:, :]
                angle_left = math.degrees(atan)
                print("Left's line angle in degrees", angle_left)
                angle_left_rad = angle_left * math.pi / 180
                x_l, y_l       = int(x_min_l + (cols-y_min_l) * math.cos(angle_left_rad)), int(y_min_l + (cols-y_min_l) * math.sin(angle_left_rad))
                detected_image = cv2.line(detected_image, (x_l, y_l), (x_min_l, y_min_l), (0, 255, 0), 2)
                x_t, y_t       = int(x_min_l + (cols-y_min_l) * math.cos(angles_avg)), int(y_min_l + (cols-y_min_l) * math.sin(angles_avg))
                detected_image = cv2.line(detected_image, (x_t, y_t), (x_min_l, y_min_l), (0, 255, 255), 2)
            else:
                print("Warning at:", file, "Not enough pixel in left side.")
            break

### Draw right line
    for i in range(-1, -100, -6):
        cropped_image = top_left_detected_image[t+100:650, i-30:i]
        h, w          = cropped_image.shape[:2]
        y_right       = []
        for y in range(0, int(h), 1):
            for x in range (0, w, 1):
                if cropped_image[y][x][0] > 250:
                    y_right.append(y+t+100)
                    break
        white_rows_right.append(len(y_right))
    max_white_rows_right   = np.array(white_rows_right).max()

    for r in range(-1, -100, -6):
        cropped_image = detected_image[t+100:650, r-30:r]
        h, w          = cropped_image.shape[:2]
        n_y_right     = []
        n_x_right     = []
        for y in range(0, int(h), 1):
            for x in range(0, w, 1):
                if cropped_image[y][x][0] > 250:
                    n_y_right.append(y+t+100)
                    n_x_right.append(w-x-r)
                    break
        n_white_rows_right = len(n_y_right)
        if n_white_rows_right == max_white_rows_right:
            if len(n_y_right) > 20:
                angles_test_2 = []
                for i in range(0, int(len(n_y_right)/4), 1):
                    yminr     = n_y_right[i]
                    ymaxr     = n_y_right[-i-1]
                    xminr     = n_x_right[i]
                    xmaxr     = n_x_right[-i-1]
                    atan      = math.atan2(ymaxr - yminr, xmaxr - xminr)
                    angle     = 180 - math.degrees(atan)
                    angle_rad = angle * math.pi / 180
                    angles_test_2.append(angle_rad)
                angles_avg_2 = np.mean(angles_test_2)
                y_min_r      = np.array(n_y_right).min()
                y_max_r      = np.array(n_y_right).max()
                x_min_r      = n_x_right[0]
                x_max_r      = n_x_right[-1]
                atan         = math.atan2(y_max_r -y_min_r, (cols-x_max_r) - (cols-x_min_r))
                angle_right  = math.degrees(atan)
                print("Right's line angle in degrees", angle_right)
                angle_right_rad = angle_right * math.pi / 180
                x_r, y_r        = int((cols-x_min_r) + (cols-y_min_r) * math.cos(angle_right_rad)), int(y_min_r + (cols-y_min_r) * math.sin(angle_right_rad))
                detected_image  = cv2.line(detected_image, (x_r, y_r), (cols-x_min_r, y_min_r), (0, 0, 255), 2)
                x_tr, y_tr      = int(cols-x_min_r + (cols-y_min_r) * math.cos(angles_avg_2)), int(y_min_r + (cols-y_min_r) * math.sin(angles_avg_2))
                detected_image  = cv2.line(detected_image, (x_tr, y_tr), (cols-x_min_r, y_min_r), (255, 0, 255), 2)
            else:
                print("Warning at:", file, "Not enough pixel in right side.")

            ### Draw bottom line
            length = cols
            detected_image = cv2.line(detected_image, (x_t, y_t), (x_tr, y_tr), (150, 150, 0), 2)
            #cv2.imshow("Top_detected", detected_image)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()
            new_x1 = x_t
            new_x2 = x_tr
            new_y1 = y_t
            new_y2 = y_tr
            # Check original image's height to width ratio.
            if orig_image.shape[0] / orig_image.shape[1] < height_to_width_ratio:
                # Then rotate
                orig_image = cv2.rotate(orig_image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            # Transform the coordinates according the original image size
            X1    = 0 + int(cc[1]) + int(ic[1]) + x_min_l
            X2    = X1 + cols - x_min_r
            Y1    = 0 + int(cc[0]) + int(ic[0]) + t

            # Calculate width and height
            table_width = X2 - X1
            table_height = table_width * 2.22
            length = table_height
            # Draw lines to original image
            #length         = table_width * 2
            #x3, y1         = int(X1 + length * math.cos(angle_left)), int(Y1 + length * math.sin(angle_left))
            #x4, y2         = int(X2 + length * math.cos(angle_right)), int(Y1 + length * math.sin(angle_right))
            #orig_image     = cv2.line(orig_image, (X2, Y1), (X1, Y1), (255, 0, 0), 3) # Top
            #orig_image     = cv2.line(orig_image,(int(X1+x1),int(y1)), (int(X1), int(Y1)), (255, 0, 0) ,3) # Left
            #orig_image     = cv2.line(orig_image,(int(X2),int(y2)), (int(X2), int(Y1)), (255, 0, 0), 3) # Right
            #orig_image     = cv2.line(orig_image, (X1+x1, y1), (X2, y2), (255, 0, 0), 3)

            # Straight lines
            #orig_image = cv2.line(orig_image, (X1, Y2), (X1, Y1), (0, 0, 255), 3)
            #orig_image = cv2.line(orig_image, (X1, Y2), (X2, Y2), (0, 0, 255), 3)
            #orig_image = cv2.line(orig_image, (X2, Y1), (X2, Y2), (0, 0, 255), 3)
            
            # Tábla szűkebb belső sávjára vonal 
            narrowing       = table_width / 11  # Kb 5 cm
            shortening      = table_height / 12.5
            tape_correction = 100
            orig_image_cut = orig_image[Y1: , X1 : X2]
            # Save angles (in deegre) and image names into csv file
            image_names_2.append(file)
            angles_left.append(angle_left * 180 / math.pi)
            angles_right.append(angle_right * 180 / math.pi)
            
            # Transform
            h, w = orig_image_cut.shape[:2]
            tape_correction = 100
            old_points  = np.array([[0, 0], [int(table_width), 0], [int(new_x2), int(new_y2)], [int(new_x1), int(new_y1)]])
            new_w = (int(table_width) - 20) / 2
            new_h = new_w * 2.22 - new_w/12
            narrowing = new_w / 6
            narrowing_cm = narrowing / new_w * orig_table_width
            narrowing_cm_ar.append(narrowing_cm)
            shortening_cm_ar.append(narrowing_cm)
            table_shape = (int(new_w), int(new_h))
            new_points  = np.array([[0,0], [table_shape[0]-1, 0], [table_shape[0]-1, table_shape[0]-1], [0, table_shape[0]-1]])
            M, mask = cv2.findHomography(old_points.astype(np.float32), new_points.astype(np.float32))
            orig_image_cut = cv2.warpPerspective(orig_image_cut, M, table_shape)
            orig_image_cut = orig_image_cut[int(narrowing):, int(narrowing):-int(narrowing)]
            print(file, "DONE!")
            break


    crop_template_full_output = os.path.join(transform_output, file)
    cv2.imwrite(crop_template_full_output, orig_image_cut)
    #cv2.imwrite(crop_template_full_output, detected_image)


# Save angles and image names into csv
angles_left_dict  = {}
angles_right_dict = {}

for i in range(0,len(image_names_2),1):
    angles_left_dict[image_names_2[i]]  = angles_left[i]

for i in range(0,len(image_names_2),1):
    angles_right_dict[image_names_2[i]] = angles_right[i]

with open('/home/golah/whiteboard_project/projects/roland/results/left_angles_B.csv', 'w') as f:
    for key in angles_left_dict.keys():
        f.write("%s,%s\n"%(key,angles_left_dict[key]))

with open('/home/golah/whiteboard_project/projects/roland/results/right_angles_B.csv', 'w') as f_2:
    for key in angles_right_dict.keys():
        f_2.write("%s,%s\n"%(key,angles_right_dict[key]))

# Save table (sampling unit) correction measures to csv
narrowing_cm_dict  = {}
shortening_cm_dict = {}

for i in range(0,len(image_names_2),1):
    narrowing_cm_dict[image_names_2[i]]  = narrowing_cm_ar[i]

for i in range(0,len(image_names_2),1):
    shortening_cm_dict[image_names_2[i]]  = shortening_cm_ar[i]

with open('/home/golah/whiteboard_project/projects/roland/results/narrowing_cm.csv', 'w') as f_3:
    for key in narrowing_cm_dict.keys():
        f_3.write("%s,%s\n"%(key,narrowing_cm_dict[key]))

with open('/home/golah/whiteboard_project/projects/roland/results/shortening.csv', 'w') as f_4:
    for key in shortening_cm_dict.keys():
        f_4.write("%s,%s\n"%(key,shortening_cm_dict[key]))
