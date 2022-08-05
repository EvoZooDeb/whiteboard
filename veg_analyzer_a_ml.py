#!/usr/bin/python
import cv2
import numpy as np
import os
import math
import csv
import pandas as pd

transform_output  = '/home/golah/angles'
analyze_output   = '/home/golah/analyze_a'
str_data = []
orig_table_height = 105
orig_table_width  = 35

# Load coords from csv data
shortening_csv = pd.read_csv("shortening.csv", sep = ",", header = None, index_col = 0, squeeze = True).to_dict()
narrowing_csv = pd.read_csv("narrowing_cm.csv", sep = ",", header = None, index_col = 0, squeeze = True).to_dict()

# For every image
for file in os.listdir(transform_output):
    image_full_path = os.path.join(transform_output, file)
    #image = cv2.imread(image_full_path, 0)
    orig_image_cut = cv2.imread(image_full_path)
    shortening_cm = shortening_csv[file]
    narrowing_cm  = narrowing_csv[file]            
    # Calculate average white shade
    l = 20
    h, w = orig_image_cut.shape[:2]
    shade_image = orig_image_cut.copy()
    for k in range(0, h, l):
        for i in range(0, w, l):
            sample = shade_image[0 : l, i: i + l]
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
                        break
        if R_val == average_R and G_val == average_G and B_val == average_B:
            break
        else:
            shade_image = shade_image[l:, : ]

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
    #border = h
    white_rows = 0
    for i in range(h-1,-1,-1):
        white_pixel = 0
        for j in range(0, w, 1):
            if white_rows < 20:
                if orig_image_cut[i][j][0] > R_lim and orig_image_cut[i][j][1] > G_lim and orig_image_cut[i][j][2] > B_lim:
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

            # Raster - 2 indent!
            #x_max = []
            #last_row = int(border) + 19
            #for j in range(0, w-1, 1):
            #    if orig_image_cut[last_row][j][0] < 5 and orig_image_cut[last_row][j][1] < 5 and orig_image_cut[last_row][j][2] > 250:
            #        x = j
            #    if j > x:
            #        if orig_image_cut[last_row][j][0] < 250 or orig_image_cut[last_row][j][1] > 5 or orig_image_cut[last_row][j][2] > 5:
            #            if orig_image_cut[last_row][j][0] < R_lim and orig_image_cut[last_row][j][1] < G_lim and orig_image_cut[last_row][j][2] < B_lim:
            #                x_max.append(j)
            #        elif orig_image_cut[i][j][0] > 250 and orig_image_cut[i][j][1] < 5 and orig_image_cut[i][j][2] < 5:
            #            break
            #
            #l = 4
            #h, w = orig_image_cut.shape[:2]
            #for k in range(int(border),0+l, -l):
            #    for i in range(0, w, l):
            #        sample = orig_image_cut[k-l : k, i: i + l]
            #        sample_h, sample_w = sample.shape[:2]
            #        sample_R = []
            #        sample_G = []
            #        sample_B = []
            #        for y in range(0, l, 1):
            #            for x in range(0, sample_w, 1):
            #                sample_R.append(sample[y][x][0])
            #                sample_G.append(sample[y][x][1])
            #                sample_B.append(sample[y][x][2])
            #        if len(sample_R) > 0 and len(sample_G) > 0 and len(sample_B) > 0:
            #            average_R = sum(sample_R) / len(sample_R)
            #            average_G = sum(sample_G) / len(sample_G)
            #            average_B = sum(sample_B) / len(sample_B)
            #            #print(average_R, R_val)
            #            if average_R  < R_val +5 and average_G < G_val+5 and average_B < B_val+5:
            #             #Fordított logika ha nagy a kontraszt akkor növény legyen
            #                if max(sample_R) - min(sample_R) > 25 and max(sample_G) - min(sample_G) > 25  and max(sample_B) - min( sample_B) > 25:
            #                    # Ezt normalizálni!
            #                    orig_image_cut[k-l:k, i-l:i] = (0,0,255)
            #                    #orig_image_cut[k-l:k, int(narrowing) +10 +i: int(narrowing) +10 + i +l] = (0,0,255)
            #                    #orig_image_cut[sample] = (0,0,255)
            #    #if R_val == average_R and G_val == average_G and B_val == average_B:
                #    break
                #else:
            
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
    # Draw lines at HCV and MHC
    hcv_pix = h-(hcv * h)/(orig_table_height - shortening_cm)
    mhc_pix = h-( mhc * h)/ (orig_table_height - shortening_cm)
    orig_image_cut  = cv2.line(orig_image_cut,(0, int(hcv_pix)), (int(w), int(hcv_pix)), (0, 0, 255) ,3) # HCV
    orig_image_cut  = cv2.line(orig_image_cut,(0, int(mhc_pix)), (int(w), int(mhc_pix)), (255, 0, 255), 3) # MHC
    print(file, "DONE!")
    analyze_full_output = os.path.join(analyze_output, file)
    cv2.imwrite(analyze_full_output, orig_image_cut)

# Save veg_str results
str_df = pd.DataFrame(str_data, columns = ['img', 'la', 'coverage_percent', 'hcv', 'mhc', 'vor'])
str_df.to_csv("veg_str_A.csv", sep = ',', encoding = 'utf-8')
