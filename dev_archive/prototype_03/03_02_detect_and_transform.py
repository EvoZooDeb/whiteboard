#!/usr/bin/python
# Import packages2
import cv2
import numpy as np
import os
import math
import pandas as pd
from itertools import combinations

crop_output           = '/home/golah/whiteboard_project/projects/miki/images/01_test_images_low_res_old_board/cropped_images/'  ## output containing crop results
edge_detection_output = '/home/golah/whiteboard_project/projects/miki/images/01_test_images_low_res_old_board/edge_detected_images/'
transform_output      = '/home/golah/whiteboard_project/projects/miki/images/01_test_images_low_res_old_board/transformed_images/'
original_image_input  = '/home/golah/whiteboard_project/projects/miki/images/01_test_images_low_res_old_board/original_images/'

#crop_output           = '/home/golah/whiteboard_project/projects/miki/images/02_test_images_high_res_old_board/cropped_images/'  ## output containing crop results
#edge_detection_output = '/home/golah/whiteboard_project/projects/miki/images/02_test_images_high_res_old_board/edge_detected_images/'
#transform_output      = '/home/golah/whiteboard_project/projects/miki/images/02_test_images_high_res_old_board/transformed_images/'
#original_image_input  = '/home/golah/whiteboard_project/projects/miki/images/02_test_images_high_res_old_board/original_images/'

#crop_output           = '/home/golah/whiteboard_project/projects/miki/images/03_test_images_low_res_new_board/cropped_images/'  ## output containing crop results
#edge_detection_output = '/home/golah/whiteboard_project/projects/miki/images/03_test_images_low_res_new_board/edge_detected_images/'
#transform_output      = '/home/golah/whiteboard_project/projects/miki/images/03_test_images_low_res_new_board/transformed_images/'
#original_image_input  = '/home/golah/whiteboard_project/projects/miki/images/03_test_images_low_res_new_board/original_images/'

#crop_output           = '/home/golah/whiteboard_project/projects/miki/images/04_test_images_high_res_new_board/cropped_images/'  ## output containing crop results
#edge_detection_output = '/home/golah/whiteboard_project/projects/miki/images/04_test_images_high_res_new_board/edge_detected_images/'
#transform_output      = '/home/golah/whiteboard_project/projects/miki/images/04_test_images_high_res_new_board/transformed_images/'
#original_image_input  = '/home/golah/whiteboard_project/projects/miki/images/04_test_images_high_res_new_board/original_images/'

save_results = True
use_correction = False


# Create function to calculate Manhattan distance 
def manhattan(a, b):
    return sum(abs(val1-val2+val1/1000) for val1, val2 in zip(a,b))

# Create a function to calculate closest value 
def closest_value(input_list, input_value):
    arr = np.asarray(input_list) 
    i = (np.abs(arr - input_value)).argmin()
    return arr[i]

# Create a function to determine points form a Rectangle
def isRect(points, threshold):
    p1, p2, p3, p4 = points[0], points[1], points[2], points[3]
    cx = (p1[0] + p2[0] + p3[0] + p4[0]) / 4
    cy = (p1[1] + p2[1] + p3[1] + p4[1]) / 4
# Distances from center
    d1 = math.dist(p1, [cx,cy])
    d2 = math.dist(p2, [cx,cy])
    d3 = math.dist(p3, [cx,cy])
    d4 = math.dist(p4, [cx,cy])
    distances      = [d1, d2, d3, d4]
    distances_diff = max(distances) - min(distances)
    distances_mean = sum(distances) / len(distances)
    if (distances_diff < distances_mean * threshold ):
        # Annotate coordinates
        all_points = np.array([p1, p2, p3, p4])
        x_axis     = np.array([p1[0], p2[0], p3[0], p4[0]])
        #sorted_points = sorted([(p1[0][0], p1[0][1]), (p2[0][0], p2[0][1]), (p3[0][0], p3[0][1]), (p4[0][0], p4[0][1])])
        sorted_points = x_axis.argsort()
        right_corners = sorted_points[2:4]
        if all_points[right_corners[0]][1] > all_points[right_corners[1]][1]:
            up_right  = all_points[right_corners[1]]
            bot_right = all_points[right_corners[0]]
        else:
            up_right  = all_points[right_corners[0]]
            bot_right = all_points[right_corners[1]]
        left_corners  = sorted_points[0:3]
        if all_points[left_corners[0]][1] > all_points[left_corners[1]][1]:
            up_left  = all_points[left_corners[1]]
            bot_left = all_points[left_corners[0]]
        else:
            up_left  = all_points[left_corners[0]]
            bot_left = all_points[left_corners[1]]
        #d_left  = manhattan(up_left, bot_left)
        #d_right = manhattan(up_right, bot_right)
        #d_top   = manhattan(up_left, up_right)
        #d_bot   = manhattan(bot_left,bot_right)
        d_left  = math.dist(up_left, bot_left)
        d_right = math.dist(up_right, bot_right)
        d_top   = math.dist(up_left, up_right)
        d_bot   = math.dist(bot_left,bot_right)
        distances_from_other_corners      = [d_left, d_right, d_top, d_bot]
        distances_from_other_corners_diff = max(distances_from_other_corners) - min(distances_from_other_corners)  
        distances_from_other_corners_mean = sum(distances_from_other_corners) / len(distances_from_other_corners)
        relative_distances_from_other_corners_diff = ((distances_from_other_corners_diff/ 4.4) +  (distances_from_other_corners_mean) + distances_diff * distances_mean) 
        if (distances_from_other_corners_diff < distances_from_other_corners_mean * (threshold * 2.35 )) and w /7.7 < distances_from_other_corners_mean < w / 6.95:
            #print("DISTANCES", d_left, d_right, d_top, d_bot)
            print("DIFF", distances_from_other_corners_diff, "THRESH", distances_from_other_corners_mean * (threshold *2.35), "MEAN", distances_from_other_corners_mean, "RELATIVE MEAN", relative_distances_from_other_corners_diff, "CENTROID_DIST", distances_diff, "CENTROID_MEAN", distances_mean)
            if cx < w/3:
                diff_values.append([relative_distances_from_other_corners_diff, "R"])
            elif w/3 < cx < w*2/3:
                diff_values.append([relative_distances_from_other_corners_diff, "P"])
            elif w*2/3 < cx:
                diff_values.append([relative_distances_from_other_corners_diff, "B"])
            return True
    return False

# Load coords from csv data
c_coords = pd.read_csv("/home/golah/whiteboard_project/projects/miki/results/cut_coords.csv", sep = ";", header = None, index_col = 0, squeeze = True).to_dict()

for file in os.listdir(crop_output):
    ## Define base params
    image_full_path          = os.path.join(crop_output, file)
    image                    = cv2.imread(image_full_path)
    h, w                     = image.shape[:2]
    original_image_full_path = os.path.join(original_image_input, file)
    orig_image               = cv2.imread(original_image_full_path)
    cc                       = c_coords[file].split(',')
    cc[0]                    = cc[0][1:]
    cc[2]                    = cc[2][:-1]
    print("Image:", file)
    border        = h / 2.5
    R             = False
    B             = False
    P             = False
    final_coord_r = None
    final_coord_b = None
    final_coord_p = None
    board_height  = 105 # in cm
    board_width   = 35  # in cm
    new_h         = board_height * 10
    divider       = board_height / board_width
    new_w         = new_h / divider
    new_border    = new_h * 0.20
    rect_l        = new_w / 7
    gap           = rect_l * 0.40
    gap_p         = rect_l * 3
    table_shape   = [round(new_w), round(new_h)]

# Examine table shade
    l           = 20
    m           = l / 2
    h, w        = image.shape[:2]
    shade_image = image.copy()
    for k in range(10, int(h), int(m)):
        if k+l > h:
            R_val = None
            break
        for i in range(w, l, -int(m)):
            sample             = shade_image[0 : l, i- l: i]
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
    
    print(R_val, G_val, B_val)

# Blurr the image
    # 2D filtering
    #kernel = np.ones((5,5),np.float32)/25
    #image = cv2.filter2D(image,-1,kernel)
    
    # Averaging
    #image = cv2.blur(image,(3,5))
    #image = cv2.boxFilter(image,(5,5))

    # Gaussian
    #image = cv2.GaussianBlur(image,(5,1), cv2.BORDER_DEFAULT)
    #image = cv2.GaussianBlur(image,(5,1), 0)

    # Median
    #image =  cv2.medianBlur(image, 3)

    # Bilateral filtering
    #image = cv2.bilateralFilter(image, 3,100,10)
    # Repeat
    #image = cv2.bilateralFilter(image, 3,100,10)

## ORB detector
#    #Initiate ORB detector
#    orb = cv2.ORB_create(125, 	scoreType = 0, edgeThreshold = 9)
#    # find the keypoints with ORB
#    kp = orb.detect(image,None)
#    # compute the descriptors with ORB
#    kp, des = orb.compute(image, kp)
#    # draw only keypoints location,not size and orientation
#    img2 = cv2.drawKeypoints(image, kp, None, color=(0,255,0), flags=0)
#    corrected_corners = np.int0(cv2.KeyPoint_convert(kp))
#    print(corrected_corners)
#    print(len(corrected_corners))
#    cv2.imshow('dst',img2)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

# Sharpen the image
    #kernel = np.array([[-1, 0, -1],
    #                   [0, 4.75, 0],
    #                   [-1, 0, -1]])
    #image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

# Lighten dark picures
    if (R_val + G_val + B_val) / 3 < 180 and 175 > R_val > 100 and 175 > G_val > 100 and 175 > B_val > 100: 
        kernel = np.array([[0, 0, 0],
                           [0, 2.5, 0],
                           [0, 0, 0]])
        image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
# Sharpen light pictures
    else:
        kernel = np.array([[-1, 0, -1],
                           [0, 5.15, 0],
                           [-1, 0, -1]])
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

# Harris detector
#    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#    gray = np.float32(gray)
#    dst = cv2.cornerHarris(gray,2,3,0.04)
#    #result is dilated for marking the corners, not important
#    dst = cv2.dilate(dst,None)
#    # Threshold for an optimal value, it may vary depending on the image.
#    image[dst>0.125*dst.max()]=[0,0,255]
#   cv2.imshow('dst',image)
#   cv2.waitKey(0)
#  cv2.destroyAllWindows()

# Grayscale image 
#    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

# Edge detection
    #gray  = cv2.Canny(image=gray, threshold1=100, threshold2=250)
    #gray  =  cv2.medianBlur(gray, 5)
    #cv2.imshow('dst',black)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #black  = cv2.Canny(black, threshold1=00, threshold2=0)
    #indices         = np.where(black != [0])
    #coords          = np.array(list(zip(indices[1], indices[0])))
    #gray            = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    #for i in coords:
    #    gray[i[1]-1:i[1]+1, i[0]-1:i[0]+1] = (0, 0, 0)

    #cv2.imshow('dst',gray)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

### SubPixel accuracy corner finding using Shi_Thomasi detector
#   Split box image then detect keypoints
#   Red
    red = gray[:int(h/3.15), int(w*0.02):int(w/4)]
    corners_r = cv2.goodFeaturesToTrack(image = red, maxCorners = 41, qualityLevel = 0.20, minDistance = 5, blockSize = 6)
    corners_r = np.int0(corners_r)
    # Draw found points
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corrected_corners_r = cv2.cornerSubPix(red,np.float32(corners_r),(3,3),(-1,-1),criteria)
    #corrected_corners_r = corners_r
    corner_dummy_r      = []
    for n, i in enumerate(corrected_corners_r):
        x,y = i.ravel()
        corner_dummy_r.append([x+w*0.02, y])
        # Draw subpixel corrected points
        cv2.circle(image,(round(x+w*0.02),round(y)),1,(255,0,0),-1)
    corrected_corners_r = corner_dummy_r

#   Blue
    blue = gray[:int(h/3.15), int(w*0.75):-int(w*0.02)]
    corners_b = cv2.goodFeaturesToTrack(image = blue, maxCorners = 25, qualityLevel = 0.325, minDistance = 3, blockSize = 6)
    corners_b = np.int0(corners_b)
    # Draw found points
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corrected_corners_b = cv2.cornerSubPix(blue,np.float32(corners_b),(3,6),(-1,-1),criteria)
    #corrected_corners_b = corners_b
    corner_dummy_b      = []
    for n, i in enumerate(corrected_corners_b):
        x,y = i.ravel()
        corner_dummy_b.append([x+w*0.75, y])
        # Draw subpixel corrected points
        cv2.circle(image,(round(x+w*0.75),round(y)),1,(0,255,0),-1)
    corrected_corners_b = corner_dummy_b


#   Purple
    purple = gray[int(h*0.625):, int(w*0.4):int(w*0.66)]
    corners_p = cv2.goodFeaturesToTrack(image = purple, maxCorners = 7, qualityLevel = 0.25, minDistance = 5, blockSize = 3)
    corners_p = np.int0(corners_p)
    # Draw found points
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corrected_corners_p = cv2.cornerSubPix(purple,np.float32(corners_p),(3,3),(-1,-1),criteria)
    corner_dummy_p = []
    for n, i in enumerate(corrected_corners_p):
        x,y = i.ravel()
        corner_dummy_p.append([x+w*0.4, y+h*0.625])
        # Draw subpixel corrected points
        cv2.circle(image,(round(x+w*0.4),round(y+h*0.625)),1,(255,0,255),-1)
    corrected_corners_p = corner_dummy_p  
    #cv2.imshow('dst', image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

# ORB detector
    #Initiate ORB detector
#    orb = cv2.ORB_create(1000)
#    # find the keypoints with ORB
#    kp = orb.detect(image,None)
#    # compute the descriptors with ORB
#    kp, des = orb.compute(image, kp)
#    # draw only keypoints location,not size and orientation
#    img2 = cv2.drawKeypoints(image, kp, None, color=(0,255,0), flags=0)
#    cv2.imshow('dst',img2)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

# FAST detector
    # Initiate FAST object with default values
    #fast = cv2.FastFeatureDetector_create(55)
    ## find and draw the keypoints
    #kp = fast.detect(image,None)
    #img2 = cv2.drawKeypoints(image, kp, None, color=(255,0,0))
    #cv2.imshow('dst',img2)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #corrected_corners = np.int0(cv2.KeyPoint_convert(kp))
    #print(corrected_corners)
    #print(len(corrected_corners))


    ## Disable nonmaxSuppression
    #fast.setNonmaxSuppression(0)
    #kp = fast.detect(image, None)
    #img3 = cv2.drawKeypoints(image, kp, None, color=(255,0,0))
    #cv2.imshow('dst',img3)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

# Using color channels - not effective
    #gray = image[:,:,2]
    #cv2.imshow('dst', gray)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #green_img = np.zeros(image.shape)
    #green_img[:,:,0] = green
    #cv2.imshow('dst', green_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

## SubPixel accuracy corner finding using Harris corner detector
    # find Harris corners
    # gray     = np.float32(gray)
    # dst      = cv2.cornerHarris(gray,2,3,0.04)
    # dst      = cv2.dilate(dst,None)
    # ret, dst = cv2.threshold(dst,0.04*dst.max(),255,0)
    # dst      = np.uint8(dst)
    # print(ret, dst)
# find centroids
    # ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
# define the criteria to stop and refine the corners
    #criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    #corners  = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
# Now draw them
    #res = np.hstack((centroids,corners))
    #res = np.int0(res)
    #image[res[:,1],res[:,0]] = [0,0,255]
    #image[res[:,3],res[:,2]] = [0,255,0]
    #found_corners            = res[:, 0:2]
    #corrected_corners        = res[:, 2:4]
    #cv2.imshow('dst',image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    final_corners = []
    diff_values   = []
    r_corners = []
    b_corners = []
    p_corners = []
    index_r_corner = []
    index_b_corner = []
    index_p_corner = []
    r_diff_values = []
    b_diff_values = []
    p_diff_values = []
    
    # Find rectangles  
    for points in combinations(corrected_corners_b, 4):
        if isRect(points, threshold = 0.075) == True:
            final_corners.append(points)
    for points in combinations(corrected_corners_r, 4):
        if isRect(points, threshold = 0.075) == True:
            final_corners.append(points)
    for points in combinations(corrected_corners_p, 4):
        if isRect(points, threshold = 0.070) == True:
            final_corners.append(points)
    print("DIFF VALUES:", diff_values)
    for d, c in diff_values: 
        if c == 'R':
            index_r_corner.append(diff_values.index([d,c]))
        elif c == 'B':
            index_b_corner.append(diff_values.index([d,c]))
        elif c == 'P':
            index_p_corner.append(diff_values.index([d,c]))

    # Find best Red corner
    if len(index_r_corner) > 1:
        for i in index_r_corner:
            r_diff_values.append(diff_values[i][0])
        print("INDEX_R", index_r_corner)
        r_diff_values_min = sorted(r_diff_values)[0]
        print("RDIFF", r_diff_values)
        print("RMIN", r_diff_values_min)
        index_r_corner = index_r_corner[r_diff_values.index(r_diff_values_min)]
        #index_r_corner = index_r_corner[6]
        print("INDEX_R", index_r_corner)

        r_corners = final_corners[index_r_corner]
    elif len(index_r_corner) == 1:
        r_corners = final_corners[index_r_corner[0]]
    
    # Find best Blue corner
    if len(index_b_corner) > 1:
        for i in index_b_corner:
            b_diff_values.append(diff_values[i][0])
        print("INDEX_B", index_b_corner)
        b_diff_values_min = sorted(b_diff_values)[0]
        print("BDIFF", b_diff_values)
        print("BMIN", b_diff_values_min)
        index_b_corner = index_b_corner[b_diff_values.index(b_diff_values_min)]
        #index_b_corner = index_b_corner[0]
        print("INDEX_b", index_b_corner)
        b_corners = final_corners[index_b_corner]
    elif len(index_b_corner) == 1:
        b_corners = final_corners[index_b_corner[0]]

    # Find best Purple corner
    if len(index_p_corner) > 1:
        for i in index_p_corner:
            p_diff_values.append(diff_values[i][0])
        print("INDEX_P", index_p_corner)
        p_diff_values_min = sorted(p_diff_values)[0]
        print("PDIFF", p_diff_values)
        print("PMIN", p_diff_values_min)
        index_p_corner = index_p_corner[p_diff_values.index(p_diff_values_min)]
        #index_p_corner = index_p_corner[2]
        print("INDEX_P", index_p_corner)
        p_corners = final_corners[index_p_corner]
    elif len(index_p_corner) == 1:
        p_corners = final_corners[index_p_corner[0]]
    
    print("CORNERS", r_corners, b_corners, p_corners)
    print("DIFF_VALUES", diff_values)
    print("FINAL", final_corners, "LEN", len(final_corners)) 
    # Determine corner positions
    # If red rectangle found
    if r_corners != []:
        r_x_axis = np.array([r_corners[0][0], r_corners[1][0], r_corners[2][0], r_corners[3][0]])
        r_sorted_points = r_x_axis.argsort()
        r_right_corners = r_sorted_points[2:4]
        if r_corners[r_right_corners[0]][1] > r_corners[r_right_corners[1]][1]:
            r_up_right  = r_corners[r_right_corners[1]]
            r_bot_right = r_corners[r_right_corners[0]]
        else:
            r_up_right  = r_corners[r_right_corners[0]]
            r_bot_right = r_corners[r_right_corners[1]]
        r_left_corners = r_sorted_points[0:2]
        if r_corners[r_left_corners[0]][1] > r_corners[r_left_corners[1]][1]:
            r_up_left  = r_corners[r_left_corners[1]]
            r_bot_left = r_corners[r_left_corners[0]]
        else:
            r_up_left  = r_corners[r_left_corners[0]]
            r_bot_left = r_corners[r_left_corners[1]]

        #image = cv2.line(image, (round(r_up_right[0]), round(r_up_right[1])), (round(r_up_left[0]), round(r_up_left[1])), (255,255,0), 1)
        #image = cv2.line(image, (round(r_bot_right[0]), round(r_bot_right[1])), (round(r_bot_left[0]), round(r_bot_left[1])), (255,255,0), 1)
        #image = cv2.line(image, (round(r_up_right[0]), round(r_up_right[1])), (round(r_bot_right[0]), round(r_bot_right[1])), (255,255,0), 1)
        #image = cv2.line(image, (round(r_up_left[0]), round(r_up_left[1])), (round(r_bot_left[0]), round(r_bot_left[1])), (255,255,0), 1)
        final_coord_r           = [r_up_left, r_up_right, r_bot_left, r_bot_right]
        atan_r                  = math.atan2(r_bot_left[1] - r_up_left[1], r_bot_left[0] - r_up_left[0])
        angle_r                 = 180 - math.degrees(atan_r)
        angle_r_rad             = -angle_r * math.pi / 180 
        manhattan_weight_r      = abs(90 - abs(angle_r)) * 0.01111111111
        r_vert_l                = manhattan(r_up_left, r_bot_left)
        r_vert_l_2              = manhattan(r_up_right, r_bot_right)
        r_vert_l                = r_vert_l * (1 - manhattan_weight_r)
        atan_r_hor              = math.atan2(r_up_left[1] - r_up_right[1], r_up_left[0] - r_up_right[0])
        angle_r_hor             = 180 - abs(math.degrees(atan_r_hor))
        angle_r_rad_hor         = -angle_r_hor * math.pi / 180
        manhattan_weight_r_hor  = abs(0 - abs(angle_r_hor)) * 0.01111111111
        r_hor_l                 = manhattan(r_up_left, r_up_right)
        r_hor_l_2               = manhattan(r_bot_left, r_bot_right)
        r_hor_l                 = r_hor_l * (1 - manhattan_weight_r_hor)
        R = True


    # If blue rectangle found
    if b_corners != []:
        b_x_axis = np.array([b_corners[0][0], b_corners[1][0], b_corners[2][0], b_corners[3][0]])
        b_sorted_points = b_x_axis.argsort()
        b_right_corners = b_sorted_points[2:4]
        if b_corners[b_right_corners[0]][1] > b_corners[b_right_corners[1]][1]:
            b_up_right  = b_corners[b_right_corners[1]]
            b_bot_right = b_corners[b_right_corners[0]]
        else:
            b_up_right  = b_corners[b_right_corners[0]]
            b_bot_right = b_corners[b_right_corners[1]]
        b_left_corners = b_sorted_points[0:2]
        if b_corners[b_left_corners[0]][1] > b_corners[b_left_corners[1]][1]:
            b_up_left  = b_corners[b_left_corners[1]]
            b_bot_left = b_corners[b_left_corners[0]]
        else:
            b_up_left  = b_corners[b_left_corners[0]]
            b_bot_left = b_corners[b_left_corners[1]]

        #image = cv2.line(image, (b_up_right), (b_up_left), (255,255,0), 1)
        #image = cv2.line(image, (b_bot_right), (b_bot_left), (255,255,0), 1)
        #image = cv2.line(image, (b_up_right), (b_bot_right), (255,255,0), 1)
        #image = cv2.line(image, (b_up_left), (b_bot_left), (255,255,0), 1)
        final_coord_b           = [b_up_left, b_up_right, b_bot_left, b_bot_right]
        atan_b                  = math.atan2(b_bot_left[1] - b_up_left[1], b_bot_left[0] - b_up_left[0])
        angle_b                 = 180-math.degrees(atan_b)
        angle_b_rad             = -angle_b * math.pi / 180 
        manhattan_weight_b      = abs(90 - abs(angle_b)) * 0.01111111111
        b_vert_l                = manhattan(b_up_left, b_bot_left)
        b_vert_l                = b_vert_l * (1 - manhattan_weight_b)
        atan_b_hor              = math.atan2(b_up_left[1] - b_up_right[1], b_up_left[0] - b_up_right[0])
        angle_b_hor             = 180 - abs(math.degrees(atan_b_hor))
        angle_b_rad_hor         = -angle_b_hor * math.pi / 180
        manhattan_weight_b_hor  = abs(0 - abs(angle_b_hor)) * 0.01111111111
        b_hor_l                 = manhattan(b_up_left, b_up_right)
        b_hor_l                 = b_hor_l * (1 - manhattan_weight_b_hor)
        B = True


    # If purple rectangle found
    if p_corners != []:
        p_x_axis = np.array([p_corners[0][0], p_corners[1][0], p_corners[2][0], p_corners[3][0]])
        p_sorted_points = p_x_axis.argsort()
        p_right_corners = p_sorted_points[2:4]
        if p_corners[p_right_corners[0]][1] > p_corners[p_right_corners[1]][1]:
            p_up_right  = p_corners[p_right_corners[1]]
            p_bot_right = p_corners[p_right_corners[0]]
        else:
            p_up_right  = p_corners[p_right_corners[0]]
            p_bot_right = p_corners[p_right_corners[1]]
        p_left_corners = p_sorted_points[0:2]
        if p_corners[p_left_corners[0]][1] > p_corners[p_left_corners[1]][1]:
            p_up_left  = p_corners[p_left_corners[1]]
            p_bot_left = p_corners[p_left_corners[0]]
        else:
            p_up_left  = p_corners[p_left_corners[0]]
            p_bot_left = p_corners[p_left_corners[1]]
        
        #image = cv2.line(image, (p_up_right), (p_up_left), (255,255,0), 1)
        #image = cv2.line(image, (p_bot_right), (p_bot_left), (255,255,0), 1)
        #image = cv2.line(image, (p_up_right), (p_bot_right), (255,255,0), 1)
        #image = cv2.line(image, (p_up_left), (p_bot_left), (255,255,0), 1)
        final_coord_p           = [p_up_left, p_up_right, p_bot_left, p_bot_right]
        atan_p                  = math.atan2(p_bot_left[1] - p_up_left[1], p_bot_left[0] - p_up_left[0])
        angle_p                 = 180-math.degrees(atan_p)
        angle_p_rad             = -angle_p * math.pi / 180 
        manhattan_weight_p      = abs(90 - abs(angle_p)) * 0.01111111111
        p_vert_l                = manhattan(p_up_left, p_bot_left)
        p_vert_l                = p_vert_l * (1 - manhattan_weight_p)
        atan_p_hor              = math.atan2(p_up_left[1] - p_up_right[1], p_up_left[0] - p_up_right[0])
        angle_p_hor             = 180 - abs(math.degrees(atan_p_hor))
        angle_p_rad_hor         = -angle_p_hor * math.pi / 180
        manhattan_weight_p_hor  = abs(0 - abs(angle_p_hor)) * 0.01111111111
        p_hor_l                 = manhattan(p_up_left, p_up_right)
        P                       = True

### Transformation
    old_points = []
    new_points = []
    # Rectangle reference points
    if final_coord_r != None:
        image = cv2.line(image, (round(final_coord_r[0][0]), round(final_coord_r[0][1])), (round(final_coord_r[1][0]), round(final_coord_r[1][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_r[0][0]), round(final_coord_r[0][1])), (round(final_coord_r[2][0]), round(final_coord_r[2][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_r[3][0]), round(final_coord_r[3][1])), (round(final_coord_r[2][0]), round(final_coord_r[2][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_r[3][0]), round(final_coord_r[3][1])), (round(final_coord_r[1][0]), round(final_coord_r[1][1])), (0,255,255), 1)
        final_coord_r[0][0] = final_coord_r[0][0] + float(cc[1])
        final_coord_r[0][1] = final_coord_r[0][1] + float(cc[0])
        final_coord_r[1][0] = final_coord_r[1][0] + float(cc[1])
        final_coord_r[1][1] = final_coord_r[1][1] + float(cc[0])
        final_coord_r[2][0] = final_coord_r[2][0] + float(cc[1])
        final_coord_r[2][1] = final_coord_r[2][1] + float(cc[0])
        final_coord_r[3][0] = final_coord_r[3][0] + float(cc[1])
        final_coord_r[3][1] = final_coord_r[3][1] + float(cc[0])
        old_points.append(final_coord_r[0])
        old_points.append(final_coord_r[1])
        old_points.append(final_coord_r[2])
        old_points.append(final_coord_r[3])
        new_points.append([gap, 0])
        new_points.append([gap + rect_l, 0])
        new_points.append([gap, rect_l])
        new_points.append([gap+rect_l, rect_l])
    if final_coord_b != None:
        image = cv2.line(image, (round(final_coord_b[0][0]), round(final_coord_b[0][1])), (round(final_coord_b[1][0]), round(final_coord_b[1][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_b[0][0]), round(final_coord_b[0][1])), (round(final_coord_b[2][0]), round(final_coord_b[2][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_b[3][0]), round(final_coord_b[3][1])), (round(final_coord_b[2][0]), round(final_coord_b[2][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_b[3][0]), round(final_coord_b[3][1])), (round(final_coord_b[1][0]), round(final_coord_b[1][1])), (0,255,255), 1)
        final_coord_b[0][0] = final_coord_b[0][0] + float(cc[1])
        final_coord_b[0][1] = final_coord_b[0][1] + float(cc[0])
        final_coord_b[1][0] = final_coord_b[1][0] + float(cc[1])
        final_coord_b[1][1] = final_coord_b[1][1] + float(cc[0])
        final_coord_b[2][0] = final_coord_b[2][0] + float(cc[1])
        final_coord_b[2][1] = final_coord_b[2][1] + float(cc[0])
        final_coord_b[3][0] = final_coord_b[3][0] + float(cc[1])
        final_coord_b[3][1] = final_coord_b[3][1] + float(cc[0])
        old_points.append(final_coord_b[0])
        old_points.append(final_coord_b[1])
        old_points.append(final_coord_b[2])
        old_points.append(final_coord_b[3])
        new_points.append([table_shape[0] - gap - rect_l, 0])
        new_points.append([table_shape[0] - gap, 0])
        new_points.append([table_shape[0] - gap - rect_l, rect_l])
        new_points.append([table_shape[0] - gap, rect_l])
    if final_coord_p != None:
        image = cv2.line(image, (round(final_coord_p[0][0]), round(final_coord_p[0][1])), (round(final_coord_p[1][0]), round(final_coord_p[1][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_p[0][0]), round(final_coord_p[0][1])), (round(final_coord_p[2][0]), round(final_coord_p[2][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_p[3][0]), round(final_coord_p[3][1])), (round(final_coord_p[2][0]), round(final_coord_p[2][1])), (0,255,255), 1)
        image = cv2.line(image, (round(final_coord_p[3][0]), round(final_coord_p[3][1])), (round(final_coord_p[1][0]), round(final_coord_p[1][1])), (0,255,255), 1)
        final_coord_p[0][0] = final_coord_p[0][0] + float(cc[1])
        final_coord_p[0][1] = final_coord_p[0][1] + float(cc[0])
        final_coord_p[1][0] = final_coord_p[1][0] + float(cc[1])
        final_coord_p[1][1] = final_coord_p[1][1] + float(cc[0])
        final_coord_p[2][0] = final_coord_p[2][0] + float(cc[1])
        final_coord_p[2][1] = final_coord_p[2][1] + float(cc[0])
        final_coord_p[3][0] = final_coord_p[3][0] + float(cc[1])
        final_coord_p[3][1] = final_coord_p[3][1] + float(cc[0])
        old_points.append(final_coord_p[0])
        old_points.append(final_coord_p[1])
        old_points.append(final_coord_p[2])
        old_points.append(final_coord_p[3])
        new_points.append([gap_p, gap_p])
        new_points.append([gap_p + rect_l, gap_p])
        new_points.append([gap_p, gap_p + rect_l])
        new_points.append([gap_p+rect_l, gap_p+rect_l])
    
    # Perspective transformation
    h, w = orig_image.shape[:2]
    old_points = np.array(old_points)
    new_points = np.array(new_points)
    if old_points != []:
        if use_correction == False:
            M, mask = cv2.findHomography(old_points.astype(np.float32), new_points.astype(np.float32))
            orig_image = cv2.warpPerspective(orig_image, M, table_shape)
        else:
            table_shape[1] = table_shape[1] + 10
            M, mask = cv2.findHomography(old_points.astype(np.float32), new_points.astype(np.float32))
            orig_image = cv2.warpPerspective(orig_image, M, table_shape)
    else:
        print(file + "Not enough point of reference")

#    # Save results
    if save_results == True:
        print(file, "DONE")
        edge_detection_full_output = os.path.join(edge_detection_output, file)
        cv2.imwrite(edge_detection_full_output, image)
        transform_full_output = os.path.join(transform_output, ("new_" + file))
        cv2.imwrite(transform_full_output, orig_image)
        #orig_image = orig_image[100:,]
        #cv2.imshow("Top_detected", orig_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        #cv2.imshow("Top_detected", image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
print("Edge detection results saved to:" + edge_detection_output)
print("Perspective transformation results saved to:" + transform_output)

