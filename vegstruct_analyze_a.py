#!/usr/bin/python
import cv2
import numpy as np
import os
import math
import csv
import pandas as pd

edge_detection_output  = '/home/golah/template_match/test_templates/type_a' 
crop_template_output   = '/home/golah/template_match/line_drawn/type_a'
input_path = '/home/golah/COCO/TEST/'
height_to_width_ratio = 0.70
angles_left   = []
angles_right  = []
image_names_2 = []
str_data = []

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
    QR_left  = False
    QR_right = False
    orig_table_height = 105
    orig_table_width  = 35
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
        image[i[1]-2:i[1]+2, i[0]-2:i[0]+2] = (0, 0, 0)

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
            top_coord_max = coordinates.max()
            top_coord_min = coordinates.min()
            detected_image = cv2.line(top_detected_image,(int(cols-1),int(top_righty)),(int(0),int(top_lefty)),(255,0,0),2)
            break
            


### Draw left line

    for i in range(1, 200, 1):
        cropped_image = top_detected_image[150:1000, i:i+24]
        n_white_pix_left = np.sum(cropped_image == 255)
        white_pixels_left.append(n_white_pix_left)

    max_white_pixels_left = np.sort(np.array(white_pixels_left))[-10:]

    for i in range(1, 200, 1):
        cropped_image = top_detected_image[150:1000, i:i+24]
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
                QR_left = True
                print("Warning at:", file, "Not enought pixel in line: Corrected left line")
            left_line   = np.array([vx, vy])  # unit vector in the same direction as your line
            dot_product = np.dot(top_line, left_line)
            angle_left   = np.arccos(dot_product)
            print("Left's line angle in degrees", angle_left * 180 / math.pi)
            detected_image = cv2.line(detected_image,(int(cols-1),int(left_righty)),(int(0),int(left_lefty)),(0,255,0),2)
            angle_right = 3.14159265 - angle_left # 180 fokból kivonjuk
            print("Right's line angle in degrees", angle_right * 180 / math.pi)
            length = rows
            x, y = int(cols + length * math.cos(angle_right)), int(0 + length * math.sin(angle_right))
            detected_image = cv2.line(detected_image, (cols, 0), (x, y), (0, 0, 255), 2)
            break

### Check if QR code is fine
    for i in range(-1, -200, -1):
        cropped_image = image[0:200, i-100:i]
        n_white_pix_right = np.sum(cropped_image == 255)
        white_pixels_right.append(n_white_pix_right)

    max_white_pixels_right = np.sort(np.array(white_pixels_right))[-10:]

    for i in range(-1, -200, -1):
        cropped_image = image[0:200, i-100:i]
        n_white_pix_right = np.sum(cropped_image == 255)
        if n_white_pix_right == max_white_pixels_right.max():
            indices = np.where(cropped_image != [0])
            coordinates = np.array(list(zip(cols - indices[1] + i, indices[0])))
            if len(coordinates) < 4000:
                QR_right = True

### Draw bottom line
            length = 3 * cols
            x1, y1 = int(0 + length * math.cos(angle_left)), int(0 + length * math.sin(angle_left))
            x2, y2 = int(cols + length * math.cos(angle_right)), int(0 + length * math.sin(angle_right))
            detected_image = cv2.line(detected_image, (x1, y1), (x2, y2), (150, 150, 0), 2)
            # Check original image's height to width ratio.
            if orig_image.shape[0] / orig_image.shape[1] < height_to_width_ratio:
                # Then rotate
                orig_image = cv2.rotate(orig_image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            # Transform the coordinates according the original image size
            # If QR code is cut in half make the x axis wider 
            if QR_left == True:
                X1    = 0 + int(cc[1]) + int(ic[1]) - 50
                X2    = X1 + cols + 50
            else:
                X1    = 0 + int(cc[1]) + int(ic[1]) 
                X2    = X1 + cols

            if QR_right == True and QR_left == True:
                X2    = X1 + cols + 150
            elif QR_right == True and QR_left == False:
                X2    = X1 + cols + 100

            Y1    = 0 + int(cc[0]) + int(ic[0])
            # Calculate table width
            table_width = X2 - X1

            # Draw outlines of board to original image
            length = table_width * 3
            x3, y1 = int(X1 + length * math.cos(angle_left)), int(Y1 + length * math.sin(angle_left))
            x4, y2 = int(X2 + length * math.cos(angle_right)), int(Y1 + length * math.sin(angle_right))
            #orig_image = cv2.line(orig_image, (X2, Y1), (X1, Y1), (0, 0, 255), 3) # Top
            #orig_image     = cv2.line(orig_image,(int(X1+x1),int(y1)), (int(X1), int(Y1)), (255, 0, 0) ,3) # Left
            #orig_image     = cv2.line(orig_image,(int(X2),int(y2)), (int(X2), int(Y1)), (255, 0, 0), 3) # Right
            #orig_image     = cv2.line(orig_image, (X1+x1, y1), (X2, y2), (0, 0, 255), 3) # bottom

           # Calculate board height 
            if y2 > y1:
                Y2 = y2
            else:
                Y2 = y1
            table_height = Y2 - Y1
            # Tábla szűkebb belső sávjára vonal 
            narrowing  = table_width / 6  # Kb 5 cm
            #shortening = table_height / 100
            shortening = narrowing

            orig_image  = cv2.line(orig_image,(int(X1+x1+narrowing),int(y1)), (int(X1+narrowing), int(Y1+shortening)), (0, 0, 255) ,3) # Left
            orig_image  = cv2.line(orig_image,(int(X2-narrowing),int(y2)), (int(X2-narrowing), int(Y1+shortening)), (255, 0, 0), 3) # Right
            orig_image_cut = orig_image[Y1+int(shortening) : Y2, X1 : X2]
            # Straight lines
            #orig_image = cv2.line(orig_image, (X1, Y2), (X1, Y1), (0, 0, 255), 3) 
            #orig_image = cv2.line(orig_image, (X1, Y2), (X2, Y2), (0, 0, 255), 3)
            #orig_image = cv2.line(orig_image, (X2, Y1), (X2, Y2), (0, 0, 255), 3) 
            
            # Save angles (in deegre) and image names into csv file
            image_names_2.append(file)
            angles_left.append(angle_left * 180 / math.pi)
            angles_right.append(angle_right * 180 / math.pi)
            
            # Calculate average white shade
            l = 20
            h, w = orig_image_cut.shape[:2]
            narrowing_cm  = narrowing / w * orig_table_width
            shortening_cm = shortening / h * orig_table_height
            for k in range(0, h, l):
                for i in range(0, w-2*int(narrowing), l):
                    sample = orig_image_cut[0 : l, int(narrowing) + 10 + i: int(narrowing) + 10 + i + l]
                    sample_h, sample_w = sample.shape[:2]
                    R_val = 255
                    G_val = 255
                    B_val = 255
                    sample_R = []
                    sample_G = []
                    sample_B = []
                    for y in range(0, l, 1):
                        for x in range(0, sample_w, 1):
                            sample_R.append(sample[y][x][0])
                            sample_G.append(sample[y][x][1])
                            sample_B.append(sample[y][x][2])
                    if len(sample_R) > 0 and len(sample_G) > 0 and len(sample_B) > 0:
                        average_R = sum(sample_R) / len(sample_R)
                        average_G = sum(sample_G) / len(sample_G)
                        average_B = sum(sample_B) / len(sample_B)
                        if 255 - average_R  < 135 and 255 - average_G < 135 and 255 - average_B < 135:
                            if max(sample_R) - min(sample_R) < 25 and max(sample_G) - min(sample_G) < 25  and max(sample_B) - min( sample_B) < 25:
                                R_val = average_R
                                G_val = average_G
                                B_val = average_B
                                print(R_val)
                                print(G_val)
                                print(B_val)
                                break
                if R_val == average_R and G_val == average_G and B_val == average_B:
                    break
                else:
                    orig_image_cut = orig_image_cut[l:, : ]

            R_err = 40
            G_err = 40
            B_err = 40
            R_lim = R_val - R_err
            G_lim = G_val - G_err
            B_lim = B_val - B_err

            # Calculate target area
            # Identify the borders by their color
            h, w = orig_image_cut.shape[:2]
            veg_str = []
            white_rows = 0
            for i in range(h-1,0,-1):
                x = w
                white_pixel = 0
                for j in range(0, w-1, 1):
                    if white_rows < 20:
                        if orig_image_cut[i][j][0] < 5 and orig_image_cut[i][j][1] < 5 and orig_image_cut[i][j][2] > 250:
                            x = j
                        if j > x:
                            if orig_image_cut[i][j][0] < 250 or orig_image_cut[i][j][1] > 5 or orig_image_cut[i][j][2] > 5:
                                if orig_image_cut[i][j][0] > R_lim and orig_image_cut[i][j][1] > G_lim and orig_image_cut[i][j][2] > B_lim:
                                    veg_str.append([i, j, 0])
                                    orig_image_cut[i, j] = (0,0,0)
                                    white_pixel = white_pixel + 1
                                else:
                                    veg_str.append([i, j, 1])
                                #orig_image_cut[i, j] = (0,0,0)
                            elif orig_image_cut[i][j][0] > 250 and orig_image_cut[i][j][1] < 5 and orig_image_cut[i][j][2] < 5:
                                if white_pixel >= (j-x)-3:
                                    white_rows = white_rows + 1
                                else:
                                    white_rows = 0
                                break
                    else:
                        if orig_image_cut[i][j][0] < 5 and orig_image_cut[i][j][1] < 5 and orig_image_cut[i][j][2] > 250:
                            x = j
                        if j > x:
                            if orig_image_cut[i][j][0] < 250 or orig_image_cut[i][j][1] > 5 or orig_image_cut[i][j][2] > 5:
                                veg_str.append([i, j, 0])
                                #orig_image_cut[i, j] = (255,0,0)
                            elif orig_image_cut[i][j][0] > 250 and orig_image_cut[i][j][1] < 5 and orig_image_cut[i][j][2] < 5:
                                break

            # Analyze vegetation structure 
            veg_str_df = pd.DataFrame(veg_str, columns = ['y','x', 'value'])
            #veg_str_df = veg_str_df.sort_values(by = 'y', axis = 0, ascending = True)
            veg_str_df['y'] = veg_str_df['y']/h * (orig_table_height - shortening_cm)
            veg_str_df['y'] = orig_table_height -veg_str_df['y'] - shortening_cm
            veg_str_df['x'] = veg_str_df['x']/w * orig_table_width 
            #veg_str_df = veg_str_df.sort_values(by = 'y', axis = 0, ascending = True)
            # Rows where pixel isn't white 
            nrow_1 = veg_str_df[veg_str_df['value'] == 1].shape[0]
            # Rownumber
            nrow_all = veg_str_df.shape[0]
            # Calculate leaf-area
            la = nrow_1/nrow_all*(orig_table_width -narrowing_cm *2) * (orig_table_height - shortening_cm)
            print("LA:", la)
            target_area = (orig_table_width - narrowing_cm*2) * (orig_table_height - shortening_cm)
            coverage_percent = la / target_area *100
            print("Coverage percentage:", coverage_percent, "%")
            vor_df = veg_str_df.groupby(['y'], as_index = False).sum()
            vor_df = vor_df.drop("x", axis = 1)
            nrow_max = veg_str_df['y'][veg_str_df['y'] == veg_str_df['y'].max()].shape[0]
            vor_df['value'] = vor_df['value'] /nrow_max
            hcv = vor_df['y'][vor_df['value'] > 0.95].max()
            if math.isnan(hcv):
                hcv = 0
            print("HCV:", hcv)
            mhc = vor_df['y'][vor_df['value'] > 0].max()
            print("MHC:", mhc)
            vor = (hcv + mhc) / 2
            print("VOR:", vor)
            #fhd =
            #print("FHD:", fhd)
            str_data.append([file, la, coverage_percent, hcv, mhc, vor])
            #str_df = pd.DataFrame(str_data, columns = ['img', 'la', 'hcv', 'mhc', 'vor'])
            #str_df.to_csv("veg_str.csv", sep = ',', encoding = 'utf-8')
            print(file, "DONE!")
            break

    crop_template_full_output = os.path.join(crop_template_output, file)
    cv2.imwrite(crop_template_full_output, orig_image_cut)

# Save veg_str results
str_df = pd.DataFrame(str_data, columns = ['img', 'la', 'coverage_percent', 'hcv', 'mhc', 'vor'])
str_df.to_csv("veg_str_A.csv", sep = ',', encoding = 'utf-8')
# Save angles and image names into csv
angles_left_dict  = {}
angles_right_dict = {}

for i in range(0,len(image_names_2),1):
    angles_left_dict[image_names_2[i]]  = angles_left[i]

for i in range(0,len(image_names_2),1):
    angles_right_dict[image_names_2[i]] = angles_right[i]

with open('left_angles_A.csv', 'w') as f:
    for key in angles_left_dict.keys():
        f.write("%s,%s\n"%(key,angles_left_dict[key]))

with open('right_angles_A.csv', 'w') as f_2:
    for key in angles_right_dict.keys():
        f_2.write("%s,%s\n"%(key,angles_right_dict[key]))

