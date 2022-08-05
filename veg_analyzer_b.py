#!/usr/bin/python
import cv2
import numpy as np
import os
import math
import csv
import pandas as pd


transform_output  = '/home/golah/template_match/line_drawn/type_b' 
#transform_output  = '/home/golah/debug' 
analyze_output   = '/home/golah/analyze'
image_names_2 = []
str_data = []
orig_table_height = 130
orig_table_width  = 58.5
# Load coords from csv data
shortening_csv = pd.read_csv("shortening.csv", sep = ",", header = None, index_col = 0, squeeze = True).to_dict()
narrowing_csv = pd.read_csv("narrowing_cm.csv", sep = ",", header = None, index_col = 0, squeeze = True).to_dict()

# For every image
for file in os.listdir(transform_output):
    image_full_path = os.path.join(transform_output, file)
    #image = cv2.imread(image_full_path, 0)
    orig_image_cut = cv2.imread(image_full_path)
    #narrowing  = table_width / 11  # Kb 5 cm
    #shortening = table_height / 12.5
    shortening_cm = shortening_csv[file]
    narrowing_cm  = narrowing_csv[file]
    l = 20
    m = l / 2
    # Calculate average white shade
    h, w = orig_image_cut.shape[:2]
    print(file)
    shade_image = orig_image_cut.copy()
    for k in range(0, h, int(m)):
        #print(k)
        #for i in range(int(narrowing), w-2*int(narrowing),int(m)):
        for i in range(w, 0, -int(m)):
            #sample = orig_image_cut[0 : l, -int(narrowing) -10 -i -l: -int(narrowing) - 10 -i ]
            sample = shade_image[0 : l, i: i + l]
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
                #print(255 - average_R)
                #print(255 - average_G)
                #print(255 - average_B)
                if 255 - average_R  < 160 and 255 - average_G < 160 and 255 - average_B < 160:
                    if max(sample_R) - min(sample_R) < 25 and max(sample_G) - min(sample_G) < 25  and max(sample_B) - min( sample_B) < 25:
                        R_val = average_R
                        G_val = average_G
                        B_val = average_B
                        break
        if R_val == average_R and G_val == average_G and B_val == average_B:
            break
        else:
            shade_image = shade_image[int(m):, : ]
            

    R_err = 90
    G_err = 110
    B_err = 120
    R_low_lim = R_val - R_err
    G_low_lim = G_val - G_err
    B_low_lim = B_val - B_err
    #R_up_lim  = R_val + R_err / 2.5
    R_up_lim  = R_val + 35
    #G_up_lim  = G_val + G_err / 2.4
    G_up_lim  = R_val + 40
    #B_up_lim  = B_val + B_err / 3
    B_up_lim  = R_val + 45
    #if R_val > 240:
    # R_up_lim = 255
    #if G_val > 240:
    # G_up_lim = G_val
    #if B_val > 240:
    # B_up_lim = B_val
    # Calculate target area
    # Identify the borders by their color and evaluate type
    veg_str = []
    white_rows = 0
    h, w = orig_image_cut.shape[:2]
    for i in range(h-1,-1,-1):
        white_pixel = 0
        for j in range(0, w, 1):
            if white_rows < 20:
                #if 230 < orig_image_cut[i][j][0] and 214 < orig_image_cut[i][j][1] and 214 < orig_image_cut[i][j][2]:
                if 220 < orig_image_cut[i][j][0] and 200 < orig_image_cut[i][j][1] and 210 < orig_image_cut[i][j][2]:
                    if orig_image_cut[i][j][1] > orig_image_cut[i][j][0] and orig_image_cut[i][j][1] > orig_image_cut[i][j][2]:
                        if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(R_val) + 10:
                            veg_str.append([i, j, 0])
                            orig_image_cut[i, j] = (0,0,0)
                            white_pixel = white_pixel + 1
                        elif R_up_lim > orig_image_cut[i][j][0] > R_low_lim and G_up_lim > orig_image_cut[i][j][1] > G_low_lim and B_up_lim > orig_image_cut[i][j][2] > B_low_lim:
                            if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) > 5:
                                if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(R_val) + 30:
                                    veg_str.append([i, j, 0])
                                    orig_image_cut[i, j] = (0,0,0)
                                    white_pixel = white_pixel + 1
                                else:
                                    veg_str.append([i, j, 1])
                            else:
                                veg_str.append([i, j, 0])
                                orig_image_cut[i, j] = (0,0,0)
                                white_pixel = white_pixel + 1
                        else:
                            veg_str.append([i, j, 1])
                    else:
                        veg_str.append([i, j, 0])
                        orig_image_cut[i, j] = (0,0,0)
                        white_pixel = white_pixel + 1
                
                elif R_up_lim > orig_image_cut[i][j][0] > R_low_lim and G_up_lim > orig_image_cut[i][j][1] > G_low_lim and B_up_lim > orig_image_cut[i][j][2] > B_low_lim:
                    if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) > 5:
                        if int(orig_image_cut[i][j][1]) - int(orig_image_cut[i][j][0]) < int(G_val) - int(R_val) + 30:
                            veg_str.append([i, j, 0])
                            orig_image_cut[i, j] = (0,0,0)
                            white_pixel = white_pixel + 1
                        else:
                            veg_str.append([i, j, 1])
                    else:
                        veg_str.append([i, j, 0])
                        orig_image_cut[i, j] = (0,0,0)
                        white_pixel = white_pixel + 1
                else:
                    veg_str.append([i, j, 1])
                if j == w-1:
                    if white_pixel >= j-w/150:
                        white_rows = white_rows + 1
                    else:
                        white_rows = 0
                    break
            else:
                veg_str.append([i, j, 0])
                orig_image_cut[i, j] = (255,0,0)
                if j == w-1:
                    break

    # Analyze vegetation structure
    veg_str_df = pd.DataFrame(veg_str, columns = ['y','x', 'value'])
    veg_str_df['y'] = veg_str_df['y']/h * (orig_table_height - shortening_cm)
    veg_str_df['y'] = orig_table_height-veg_str_df['y'] - shortening_cm
    veg_str_df['x'] = veg_str_df['x']/w * orig_table_width 
    #veg_str_df = veg_str_df.sort_values(by = 'y', axis = 0, ascending = True)
    # Rows where pixel isn't white 
    nrow_1 = veg_str_df[veg_str_df['value'] == 1].shape[0]
    # Rownumber
    nrow_all = veg_str_df.shape[0]
    # Calculate leaf-area
    la = nrow_1/nrow_all*(orig_table_width - narrowing_cm * 2)*(orig_table_height - shortening_cm)
    print("LA:", la)
    target_area = (orig_table_width - narrowing_cm * 2) * (orig_table_height - shortening_cm)
    coverage_percent = la / target_area *100
    #veg_str_df = veg_str_df.drop("x", axis = 1)
    print("Coverage percentage:", coverage_percent, "%")
    vor_df = veg_str_df.groupby(['y'], as_index = False).sum()
    vor_df = vor_df.drop("x", axis = 1)
    nrow_max = veg_str_df['y'][veg_str_df['y'] == veg_str_df['y'].max()].shape[0]
    vor_df['value'] = vor_df['value'] /nrow_max
    hcv = vor_df['y'][vor_df['value'] > 0.90].max()
    if math.isnan(hcv):
        hcv = 0 
    print("HCV:", hcv)
    mhc = vor_df['y'][vor_df['value'] > 0].max()
    print("MHC:", mhc)
    vor = (hcv + mhc) / 2
    print("VOR:", vor)
    #fhd =
    #print("FHD:", fhd)
    str_data.append([file, la, coverage_percent,hcv,  mhc, vor])
    #str_df = pd.DataFrame(str_data, columns = ['img', 'la', 'hcv', 'mhc', 'vor'])
    #str_df.to_csv("veg_str.csv", sep = ',', encoding = 'utf-8')
    # Draw lines at HCV and MHC
    hcv_pix = h-(hcv * h)/(orig_table_height - shortening_cm)
    mhc_pix = h-( mhc * h)/ (orig_table_height - shortening_cm)
    orig_image_cut  = cv2.line(orig_image_cut,(0, int(hcv_pix)), (int(w), int(hcv_pix)), (0, 0, 255) ,3) # HCV
    orig_image_cut  = cv2.line(orig_image_cut,(0, int(mhc_pix)), (int(w), int(mhc_pix)), (255, 0, 255), 3) # MHC

    print(file, "DONE!")
    analyze_full_output = os.path.join(analyze_output, file)
    cv2.imwrite(analyze_full_output, orig_image_cut)

# Save veg_str results
str_df = pd.DataFrame(str_data, columns = ['img', 'la','coverage_percent', 'hcv', 'mhc', 'vor'])
str_df.to_csv("veg_str_B.csv", sep = ',', encoding = 'utf-8')

