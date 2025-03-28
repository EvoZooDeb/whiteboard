#!/usr/bin/python
import cv2
import numpy as np
import os
import math
import csv
import pandas as pd
import skbio

# Defome parameters
transform_output = '/home/golah/whiteboard_project/projects/miki/images/01_test_images_low_res_old_board/transformed_images/' 
analyze_output   = '/home/golah/whiteboard_project/projects/miki/images/01_test_images_low_res_old_board/result_images/'
image_names_2 = []
str_data = []
orig_table_height = 105
orig_table_width  = 35

# For every transformed image
for file in os.listdir(transform_output):
    image_full_path = os.path.join(transform_output, file)
    orig_image_cut = cv2.imread(image_full_path)
    shortening_cm = 6
    narrowing_cm  = 2
    orig_image_cut = orig_image_cut[shortening_cm*10:,narrowing_cm*10:-narrowing_cm*10]
    l = 20
    m = l / 2

    # Calculate average white shade
    h, w = orig_image_cut.shape[:2]
    shade_image = orig_image_cut.copy()
    for k in range(0, int(h), int(m)):
        if k+l > h:
            R_val = None
            break
        for i in range(w, l, -int(m)):
            sample = shade_image[0 : l, i- l: i]
            sample_h, sample_w = sample.shape[:2]
            #cv2.imshow("Top_detected", sample)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()
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
                if 255 - average_R  < 160 and 255 - average_G < 160 and 255 - average_B < 160 and average_G < average_R + 25 and average_G < average_B + 35 :
                    if max(sample_R) - min(sample_R) < 25 and max(sample_G) - min(sample_G) < 25  and max(sample_B) - min( sample_B) < 25:
                        R_val = average_R
                        G_val = average_G
                        B_val = average_B
                        break
        if R_val == average_R and G_val == average_G and B_val == average_B:
            break
        else:
            shade_image = shade_image[int(m):, : ]
     
    if R_val == None:
        print(file, ": couldn't calculate average shade")
        continue
    R_err = 90
    G_err = 110
    B_err = 120

    R_low_lim = R_val - R_err
    G_low_lim = G_val - G_err
    B_low_lim = B_val - B_err
    R_up_lim  = R_val + 35
    G_up_lim  = R_val + 40
    B_up_lim  = R_val + 45
    
    # Calculate target area
    #print("RVAL: ", R_val, R_up_lim, R_low_lim)
    #print("GVAL: ", G_val, G_up_lim, G_low_lim)
    #print("BVAL: ", B_val, B_up_lim, B_low_lim)
    veg_str = []
    white_rows = 0
    h, w = orig_image_cut.shape[:2]
    border = 0
    for i in range(h-1,-1,-1):
        white_pixel = 0
        if white_rows < 50:
            for j in range(0, w, 1):
                if 220 < orig_image_cut[i][j][0] and 200 < orig_image_cut[i][j][1] and 200 < orig_image_cut[i][j][2]:
                    if orig_image_cut[i][j][1] > orig_image_cut[i][j][0] and orig_image_cut[i][j][1] > orig_image_cut[i][j][2]:
                        if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(B_val) + 10:
                            veg_str.append([i, j, 0])
                            orig_image_cut[i, j] = (0,0,0)
                            white_pixel = white_pixel + 1
                        elif R_up_lim > orig_image_cut[i][j][0] > R_low_lim and G_up_lim > orig_image_cut[i][j][1] > G_low_lim and B_up_lim > orig_image_cut[i][j][2] > B_low_lim:
                            if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) > 5:
                                if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(B_val) + 30:
                                    veg_str.append([i, j, 0])
                                    orig_image_cut[i, j] = (0,0,0)
                                    white_pixel = white_pixel + 1
                                else:
                                    veg_str.append([i, j, 1])
                                    #orig_image_cut[i, j] = (255,0,255)
                            else:
                                veg_str.append([i, j, 0])
                                orig_image_cut[i, j] = (0,0,0)
                                white_pixel = white_pixel + 1
                        else:
                            veg_str.append([i, j, 1])
                            #orig_image_cut[i, j] = (0,0,255)
                    else:
                        veg_str.append([i, j, 0])
                        orig_image_cut[i, j] = (0,0,0)
                        white_pixel = white_pixel + 1
                # Reference rectangle
                elif (orig_image_cut[i][j][0] > orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][0] > orig_image_cut[i][j][2] + 10) or (orig_image_cut[i][j][0] < 100 and orig_image_cut[i][j][0] > orig_image_cut[i][j][1] and orig_image_cut[i][j][0] > orig_image_cut[i][j][2] and orig_image_cut[i][j][2]+10 > orig_image_cut[i][j][1]):
               # elif orig_image_cut[i][j][0] > orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][0] > orig_image_cut[i][j][2] + 10:
                    veg_str.append([i, j, 0])
                    orig_image_cut[i, j] = (0,0,0)
                    white_pixel = white_pixel + 1
                
                elif R_up_lim > orig_image_cut[i][j][0] > R_low_lim and G_up_lim > orig_image_cut[i][j][1] > G_low_lim and B_up_lim > orig_image_cut[i][j][2] > B_low_lim:
                    if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) > 5:
                        if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(B_val) + 30:
                            veg_str.append([i, j, 0])
                            orig_image_cut[i, j] = (0, 0, 0)
                            white_pixel = white_pixel + 1
                        else:
                            veg_str.append([i, j, 1])
                            #orig_image_cut[i, j] = (255,0,255)
                    else:
                        veg_str.append([i, j, 0])
                        orig_image_cut[i, j] = (0,0,0)
                        white_pixel = white_pixel + 1
                elif orig_image_cut[i][j][0] < orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][1] < orig_image_cut[i][j][0] +30 and orig_image_cut[i][j][0] < orig_image_cut[i][j][2] + 30 and orig_image_cut[i][j][2] < orig_image_cut[i][j][0] + 30 and orig_image_cut[i][j][2] < orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][1] < orig_image_cut[i][j][2] + 30 and orig_image_cut[i][j][0] > 70 and orig_image_cut[i][j][1] > 70 and orig_image_cut[i][j][2] > 70:
                        veg_str.append([i, j, 0])
                        orig_image_cut[i, j] = (0,0,0)
                        white_pixel = white_pixel + 1
                else:
                    veg_str.append([i, j, 1])
                    #orig_image_cut[i, j] = (255,0,0)
                if j == w-1:
                    if white_pixel >= w-5:
                        white_rows = white_rows + 1
                    else:
                        white_rows = 0
                    break
        else:
            border = i
            break
    #cv2.imshow("Top_detected", orig_image_cut)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #break
    print("BORDER", border)            
    if border != 0:
        x_max = []
        white_rows = 0
        last_row = int(border) + 51
        if last_row != h:
            for i in range(int(last_row), int(border), -1):
                for j in range(0, w, 1):
                    if 0 < orig_image_cut[i][j][0] or 0 < orig_image_cut[i][j][1] or 0 < orig_image_cut[i][j][2]:
                        x_max.append(j)
            x_max = np.unique(x_max)
            r = 3
            for i in range(int(border),-1, -1):
                    white_pixel = 0 
                    r = r + 2
                    min_x_max = min(x_max) - r
                    if min_x_max < 0:
                        min_x_max = 0
                    max_x_max = max(x_max) + r
                    if max_x_max > w:
                        max_x_max = w
                    for j in range(0, w, 1):
                        if white_rows < 50:
                            if min_x_max <= j <= max_x_max:
                                if 220 < orig_image_cut[i][j][0] and 200 < orig_image_cut[i][j][1] and 200 < orig_image_cut[i][j][2]:
                                    if orig_image_cut[i][j][1] > orig_image_cut[i][j][0] and orig_image_cut[i][j][1] > orig_image_cut[i][j][2]:
                                        if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(B_val) + 10:
                                            veg_str.append([i, j, 0])
                                            orig_image_cut[i, j] = (0,0,0)
                                            white_pixel = white_pixel + 1
                                        elif R_up_lim > orig_image_cut[i][j][0] > R_low_lim and G_up_lim > orig_image_cut[i][j][1] > G_low_lim and B_up_lim > orig_image_cut[i][j][2] > B_low_lim:
                                            if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) > 5:
                                                if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(B_val) + 30:
                                                    veg_str.append([i, j, 0])
                                                    orig_image_cut[i, j] = (0,0,0)
                                                    white_pixel = white_pixel + 1
                                                else:
                                                    veg_str.append([i, j, 1])
                                                    #orig_image_cut[i, j] = (0,0,255)
                                            else:
                                                veg_str.append([i, j, 0])
                                                orig_image_cut[i, j] = (0,0,0)
                                                white_pixel = white_pixel + 1
                                        else:
                                            veg_str.append([i, j, 1])
                                            #orig_image_cut[i, j] = (0,0,255)
                                    else:
                                        veg_str.append([i, j, 0])
                                        orig_image_cut[i, j] = (0,0,0)
                                        white_pixel = white_pixel + 1
                                # Reference rectangle
                                elif (orig_image_cut[i][j][0] > orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][0] > orig_image_cut[i][j][2] + 10) or (orig_image_cut[i][j][0] < 100 and orig_image_cut[i][j][0] > orig_image_cut[i][j][1] and orig_image_cut[i][j][0] > orig_image_cut[i][j][2] and orig_image_cut[i][j][2]+10 > orig_image_cut[i][j][1]):
                       #         elif orig_image_cut[i][j][0] > orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][0] > orig_image_cut[i][j][2] + 10:
                                    veg_str.append([i, j, 0])
                                    orig_image_cut[i, j] = (0,0,0)
                                    white_pixel = white_pixel + 1
                                
                                elif R_up_lim > orig_image_cut[i][j][0] > R_low_lim and G_up_lim > orig_image_cut[i][j][1] > G_low_lim and B_up_lim > orig_image_cut[i][j][2] > B_low_lim:
                                    if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) > 5:
                                        if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(B_val) + 30:
                                            veg_str.append([i, j, 0])
                                            orig_image_cut[i, j] = (0, 0, 0)
                                            white_pixel = white_pixel + 1
                                        else:
                                            veg_str.append([i, j, 1])
                                           # orig_image_cut[i, j] = (0,0,255)
                                    else:
                                        veg_str.append([i, j, 0])
                                        orig_image_cut[i, j] = (0,0,0)
                                        white_pixel = white_pixel + 1
                                elif orig_image_cut[i][j][0] < orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][1] < orig_image_cut[i][j][0] +30 and orig_image_cut[i][j][0] < orig_image_cut[i][j][2] + 30 and orig_image_cut[i][j][2] < orig_image_cut[i][j][0] + 30 and orig_image_cut[i][j][2] < orig_image_cut[i][j][1] + 30 and orig_image_cut[i][j][1] < orig_image_cut[i][j][2] + 30 and orig_image_cut[i][j][0] > 70 and orig_image_cut[i][j][1] > 70 and orig_image_cut[i][j][2] > 70:
                                    veg_str.append([i, j, 0])
                                    orig_image_cut[i, j] = (0,0,0)
                                    white_pixel = white_pixel + 1
                                else:
                                    veg_str.append([i, j, 1])
                                   # orig_image_cut[i, j] = (0,0,255)
                                if j == max_x_max-1:
                                    if white_pixel >= (max_x_max - min_x_max)-5:
                                        white_rows = white_rows + 1
                                    else:
                                        white_rows = 0
                            else:
                                veg_str.append([i, j, 0])
                                orig_image_cut[i, j] = (0,0,0)
                        else:
                            veg_str.append([i, j, 0])
                            orig_image_cut[i, j] = (0,0,0)

    # Analyze vegetation structure
    veg_str_df = pd.DataFrame(veg_str, columns = ['y','x', 'value'])
    veg_str_df['y'] = veg_str_df['y']/h * (orig_table_height - shortening_cm)
    veg_str_df['y'] = orig_table_height-veg_str_df['y'] - shortening_cm
    veg_str_df['x'] = veg_str_df['x']/w * orig_table_width 
    # Rows where pixel isn't white 
    nrow_1 = veg_str_df[veg_str_df['value'] == 1].shape[0]
    # Rownumber
    nrow_all = veg_str_df.shape[0]
    # Calculate leaf-area
    la = nrow_1/nrow_all*(orig_table_width - narrowing_cm * 2)*(orig_table_height - shortening_cm)
    print("LA:", la)
    target_area = (orig_table_width - narrowing_cm * 2) * (orig_table_height - shortening_cm)
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
    fhd = skbio.diversity.alpha.shannon(vor_df['value'], 2)
    print("FHD:", fhd)
    str_data.append([file, la, coverage_percent,hcv,  mhc, vor, fhd])
    
    # Draw lines at HCV and MHC
    hcv_pix = h-(hcv * h)/(orig_table_height - shortening_cm)
    mhc_pix = h-( mhc * h)/ (orig_table_height - shortening_cm)
    if math.isnan(hcv_pix):
        hcv_pix = h
    if math.isnan(mhc_pix):
        mhc_pix = h
    orig_image_cut  = cv2.line(orig_image_cut,(0, int(hcv_pix)), (int(w), int(hcv_pix)), (0, 0, 255) ,3) # HCV
    orig_image_cut  = cv2.line(orig_image_cut,(0, int(mhc_pix)), (int(w), int(mhc_pix)), (255, 0, 255), 3) # MHC

    print(file, "DONE!")
    analyze_full_output = os.path.join(analyze_output, file)
    #cv2.imshow("Top_detected", orig_image_cut)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    cv2.imwrite(analyze_full_output, orig_image_cut)

# Save veg_str results
str_df = pd.DataFrame(str_data, columns = ['img', 'la','coverage_percent', 'hcv', 'mhc', 'vor', 'fhd'])
str_df.to_csv("/home/golah/whiteboard_project/projects/roland/results/veg_str_22.csv", sep = ',', encoding = 'utf-8')

