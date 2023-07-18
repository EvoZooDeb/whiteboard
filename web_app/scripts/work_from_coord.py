import cv2
import numpy as np
import os
import math
import csv
import pandas as pd



def transform_by_coord(file_path, sep, header, x, y, label, image_name, old_points):
    corners  = pd.read_csv(file_path, sep = sep, header = header, squeeze = True)
    corners  = corners[corners[label] == image_name]
    # Red
    red         = corners.sort_values(x)[:4]
    r_left      = red.sort_values(x)[:2]
    r_top_left  = r_left.sort_values(y)[:1].iloc[0]
    r_bot_left  = r_left.sort_values(y)[1:].iloc[0]
    r_right     = red.sort_values(x)[2:]
    r_top_right = r_right.sort_values(y)[:1].iloc[0]
    r_bot_right = r_right.sort_values(y)[1:].iloc[0]

    # Blue
    blue   = corners.sort_values(x)[8:]
    b_left      = blue.sort_values(x)[:2]
    b_top_left  = b_left.sort_values(y)[:1].iloc[0]
    b_bot_left  = b_left.sort_values(y)[1:].iloc[0]
    b_right     = blue.sort_values(x)[2:]
    b_top_right = b_right.sort_values(y)[:1].iloc[0]
    b_bot_right = b_right.sort_values(y)[1:].iloc[0]

    # Purple
    purple = corners.sort_values(x)[4:8]
    p_left      = purple.sort_values(x)[:2]
    p_top_left  = p_left.sort_values(y)[:1].iloc[0]
    p_bot_left  = p_left.sort_values(y)[1:].iloc[0]
    p_right     = purple.sort_values(x)[2:]
    p_top_right = p_right.sort_values(y)[:1].iloc[0]
    p_bot_right = p_right.sort_values(y)[1:].iloc[0]
    
    # Add points
    old_points.append([r_top_left[2], r_top_left[3]])
    old_points.append([r_top_right[2], r_top_right[3]])
    old_points.append([r_bot_left[2], r_bot_left[3]])
    old_points.append([r_bot_right[2], r_bot_right[3]])
    old_points.append([b_top_left[2], b_top_left[3]])
    old_points.append([b_top_right[2], b_top_right[3]])
    old_points.append([b_bot_left[2], b_bot_left[3]])
    old_points.append([b_bot_right[2], b_bot_right[3]])
    old_points.append([p_top_left[2], p_top_left[3]])
    old_points.append([p_top_right[2], p_top_right[3]])
    old_points.append([p_bot_left[2], p_bot_left[3]])
    old_points.append([p_bot_right[2], p_bot_right[3]])

def work_from_coord(orig_path, coords_path, project_dir, board_height = 105, board_width = 35, rect_l = 5, r_gap_top = 0, r_gap_side = 2, b_gap_top = 0, b_gap_side = 2, p_gap_top = 15, p_gap_side = 15, sep = ",", header = 0, x_colname = "X", y_colname = "Y", img_colname = "Label"):
    input_path = orig_path
    coords_path = coords_path
    transform_output   = project_dir + 'images/transformed_images/'
    board_height  = float(board_height) # in cm
    board_width   = float(board_width)  # in cm
    new_h         = board_height * 10
    new_w         = board_width  * 10
    rect_l        = float(rect_l) * 10     # in cm
    r_gap_top     = float(r_gap_top) * 10  # in cm
    r_gap_side    = float(r_gap_side) * 10 # in cm
    b_gap_top     = float(b_gap_top) * 10  # in cm
    b_gap_side    = float(b_gap_side) * 10 # in cm
    p_gap_top     = float(p_gap_top) * 10  # in cm
    p_gap_side    = float(p_gap_side) * 10 # in cm
    table_shape   = [round(new_w), round(new_h)]
    header        = int(header)

# For every image
    for file in os.listdir(input_path):
        image_full_path = os.path.join(input_path, file)
        image = cv2.imread(image_full_path)
        new_points = []
        old_points = []
        transform_by_coord(file_path = coords_path, sep = sep, header = header, x = x_colname, y = y_colname, label = img_colname, image_name = file, old_points = old_points)
        
        # Reference points
        # Red
        new_points.append([r_gap_side, r_gap_top + 0])
        new_points.append([r_gap_side + rect_l, r_gap_top + 0])
        new_points.append([r_gap_side, r_gap_top + rect_l])
        new_points.append([r_gap_side + rect_l, r_gap_top + rect_l])

        # Blue
        new_points.append([table_shape[0] - b_gap_side - rect_l, b_gap_top + 0])
        new_points.append([table_shape[0] - b_gap_side, b_gap_top + 0])
        new_points.append([table_shape[0] - b_gap_side - rect_l, b_gap_top + rect_l])
        new_points.append([table_shape[0] - b_gap_side, b_gap_top + rect_l])

        # Purple
        new_points.append([p_gap_side, p_gap_top])
        new_points.append([p_gap_side + rect_l, p_gap_top])
        new_points.append([p_gap_side, p_gap_top + rect_l])
        new_points.append([p_gap_side + rect_l, p_gap_top + rect_l])

        # Transform
        old_points = np.array(old_points)
        new_points = np.array(new_points)
        M, mask = cv2.findHomography(old_points.astype(np.float32), new_points.astype(np.float32))
        orig_image_cut = cv2.warpPerspective(image, M, table_shape)
        #cv2.imshow("Top_detected", orig_image_cut)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        crop_template_full_output = os.path.join(transform_output, file)
        cv2.imwrite(crop_template_full_output, orig_image_cut)
        print(file, "DONE!")

#work_from_coord(orig_path, coords_path, project_dir, board_height = 105, board_width = 35, rect_l = 5, r_gap_top = 0, r_gap_side = 2, b_gap_top = 0, b_gap_side = 2, p_gap_top = 15, p_gap_side = 15, sep = ",", header = 0, x_colname = "X", y_colname = "Y", img_colname = "Label"):
if __name__ == '__main__':
    work_from_coord("/home/eram/python_venv/images/original_images/","/home/eram/python_venv/coords.csv" ,"/home/eram/python_venv/")
