#!/usr/bin/python
import cv2
import numpy as np
import os
import math
import csv
import pandas as pd

# Functions imported from sk.bio read more at: https://github.com/biocore/scikit-bio
def _validate_counts_vector(counts, suppress_cast=False):
    """Validate and convert input to an acceptable counts vector type.

    Note: may not always return a copy of `counts`!

    """
    counts = np.asarray(counts)
    try:
        if not np.all(np.isreal(counts)):
            raise Exception
    except Exception:
        raise ValueError("Counts vector must contain real-valued entries.")
    if counts.ndim != 1:
        raise ValueError("Only 1-D vectors are supported.")
    elif (counts < 0).any():
        raise ValueError("Counts vector cannot contain negative values.")

    return counts

def skbio_shannon(counts, base):
    counts = _validate_counts_vector(counts)
    freqs = counts / counts.sum()
    nonzero_freqs = freqs[freqs.nonzero()]
    return -(nonzero_freqs * np.log(nonzero_freqs)).sum() / np.log(base)

### Pixel analyze
## Description:
# Examines the RGB color code of each pixel on image and based on that classifies them into two categories: board pixel or plant pixel. Based on the pixel positions and classes the function calculates the following parameters: LA, HCV, MHC, VOR, FHD. The function saves the results to a CSV file to project_dir/results.

## Parameters:
# project_dir: project directory path, read documentation at https://github.com/EvoZooDeb/whiteboard. 
# board_height: Height of the whiteboard in cm.
# board_width: Width of the whiteboard in cm.
# rect_l: Sidelength of reference square in cm.

## Returns:
# error_images: a list containing the names of images without detectable object

def pixel_analyze(project_dir, board_height = 105, board_width = 35, rect_l = 5):
    
    # Define parameters 
    # Create relative paths
    transform_output = project_dir + 'images/transformed_images/' 
    analyze_output   = project_dir + 'images/result_images/'
    
    # Placeholder lists
    image_names_2 = []
    str_data      = []
    error_images  = []

    # Convert table params to type: float.
    orig_table_height = float(board_height)
    orig_table_width  = float(board_width)
    rect_l            = float(rect_l)

    # For every transformed image
    for file in os.listdir(transform_output):
        print("Pixel analysis of image:", file)

        # Load image
        image_full_path = os.path.join(transform_output, file)
        orig_image_cut = cv2.imread(image_full_path)

        # Define sample area by cutting a few centimeters from each side and the top of the image.
        shortening_cm = round(rect_l + 1)
        narrowing_cm  = round(rect_l / 2)
        orig_image_cut = orig_image_cut[shortening_cm*10:,narrowing_cm*10:-narrowing_cm*10]
        
    
        # Calculate average white shade
        # Define variables
        l = 20
        m = l / 2
        h, w = orig_image_cut.shape[:2]
        shade_image = orig_image_cut.copy()

        # Starting from the top right corner of the image, crop out squares with the sidelength of l.
        for k in range(0, int(h), int(m)):
            if k+l > h:
                R_val = None
                break
            for i in range(w, l, -int(m)):
                sample = shade_image[0 : l, i- l: i]
                sample_h, sample_w = sample.shape[:2]
                R_val = 255
                G_val = 255
                B_val = 255
                sample_R = []
                sample_G = []
                sample_B = []
                # Append the color values found in the pixels of sample image to unique lists.
                for y in range(0, l, 1):
                    for x in range(0, sample_w, 1):
                        sample_R.append(sample[y][x][0])
                        sample_G.append(sample[y][x][1])
                        sample_B.append(sample[y][x][2])

                # Examine color values
                if len(sample_R) > 0 and len(sample_G) > 0 and len(sample_B) > 0:

                    # Calculate average value of each color channel
                    average_R = sum(sample_R) / len(sample_R)
                    average_G = sum(sample_G) / len(sample_G)
                    average_B = sum(sample_B) / len(sample_B)
                    
                    # Substract average values from the theoretical white value (255). If all of the results are below the threshold (160) it may indicate a white                        (or greyish in reality) shade.
                    if 255 - average_R  < 160 and 255 - average_G < 160 and 255 - average_B < 160 and average_G < average_R + 25 and average_G < average_B + 35:

                        # If there is little (< 25) difference between the lowest and highest values in each color channel, it may indicate that the sample picture co                        ntains similar pixels, depicting a uniform object. 
                        if max(sample_R) - min(sample_R) < 25 and max(sample_G) - min(sample_G) < 25  and max(sample_B) - min( sample_B) < 25:
                            R_val = average_R
                            G_val = average_G
                            B_val = average_B
                            break

            # We found the sufficient values
            if R_val == average_R and G_val == average_G and B_val == average_B:
                break
            else:
            
            # Crop out another sample rectangle, next to the previous one with m overlap.
                shade_image = shade_image[int(m):, : ]
        
        # If no sufficent values are found move to the next image
        if R_val == None:
            print(file, ": couldn't calculate average shade")
            continue
        
        # Define errors and limits
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

        # Calculate x, y values
        veg_str_df['y'] = veg_str_df['y']/h * (orig_table_height - shortening_cm)
        veg_str_df['y'] = orig_table_height-veg_str_df['y'] - shortening_cm
        veg_str_df['x'] = veg_str_df['x']/w * orig_table_width 
        
        # Rows where pixel isn't white 
        nrow_1 = veg_str_df[veg_str_df['value'] == 1].shape[0]

        # Rownumber
        nrow_all = veg_str_df.shape[0]

        # Calculate leaf-area and coverage percent
        la = nrow_1/nrow_all*(orig_table_width - narrowing_cm * 2)*(orig_table_height - shortening_cm)
        if math.isnan(la):
            la = 0 
            error_images.append([file, "leaf area (la)"])
        print("LA:", la)
        target_area = (orig_table_width - narrowing_cm * 2) * (orig_table_height - shortening_cm)
        coverage_percent = la / target_area *100
        print("Coverage percentage:", coverage_percent, "%")

        # Calculate HCV
        vor_df = veg_str_df.groupby(['y'], as_index = False).sum()
        vor_df = vor_df.drop("x", axis = 1)

        # Rownumber where y = max
        nrow_max = veg_str_df['y'][veg_str_df['y'] == veg_str_df['y'].max()].shape[0]
        vor_df['value'] = vor_df['value'] /nrow_max

        # HCV: The y value where the > 95% of the pixels are part of the vegetation
        hcv = vor_df['y'][vor_df['value'] > 0.95].max()
        if math.isnan(hcv):
            #hcv = 0 
            error_images.append([file, "height of closed vegetation (hcv)"])
        print("HCV:", hcv)

        # MHC: The maximum Y value
        mhc = vor_df['y'][vor_df['value'] > 0].max()
        if math.isnan(mhc):
            #mhc = 0 
            error_images.append([file, "maximum height of vegetation (mhc)"])
        print("MHC:", mhc)

        # VOR
        vor = (hcv + mhc) / 2
        if math.isnan(vor):
            #vor = 0 
            error_images.append([file, "visual obstruction readings (vor)"])
        print("VOR:", vor)

        # Shanon-diversity of pixels.
        fhd = skbio_shannon(vor_df['value'], 2)
        if math.isnan(fhd):
            #fhd = 0 
            error_images.append([file, "foliage height diversity (fhd)"])
        print("FHD:", fhd)

        # Add image name and structural parameters to structure data
        str_data.append([file, la, coverage_percent,hcv,  mhc, vor, fhd])
        
        # Draw lines at HCV and MHC on the image (for visualization)
        if not math.isnan(hcv) and  not math.isnan(mhc):
            hcv_pix = h-(hcv * h)/(orig_table_height - shortening_cm)
            mhc_pix = h-( mhc * h)/ (orig_table_height - shortening_cm)
            if math.isnan(hcv_pix):
                hcv_pix = h
            if math.isnan(mhc_pix):
                mhc_pix = h
            orig_image_cut  = cv2.line(orig_image_cut,(0, int(hcv_pix)), (int(w), int(hcv_pix)), (0, 0, 255) ,3) # HCV
            orig_image_cut  = cv2.line(orig_image_cut,(0, int(mhc_pix)), (int(w), int(mhc_pix)), (255, 0, 255), 3) # MHC
    
        print(file, "DONE!")

        # Save resulting image: black pixels indicate table pixels, vegetation pixels remain unchanged
        analyze_full_output = os.path.join(analyze_output, file)
        cv2.imwrite(analyze_full_output, orig_image_cut)
    
    # Save veg_str results to CSV file
    str_df = pd.DataFrame(str_data, columns = ['img', 'la','coverage_percent', 'hcv', 'mhc', 'vor', 'fhd'])
    str_df.to_csv((project_dir + "results/veg_str_22.csv"), sep = ',', encoding = 'utf-8')
    return error_images

#pixel_analyse(project_dir, board_height = 105, board_width = 35, rect_l):
if __name__ == '__main__':
    pixel_analyze("/home/eram/python_venv/")

