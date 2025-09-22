import numpy as np
import cv2
import math
from pyzbar import pyzbar
import os
import pathlib

def detect_qr_code(image):
    barcodes = pyzbar.decode(image)
    if len(barcodes) >= 2:
        b_corners = [[], []]
        ni = 0
        for barcode in barcodes:
            points_x = []
            points_y = []
            for p in barcode.polygon:
                points_x.append(p.x)
                points_y.append(p.y)
            i = np.argsort(points_y)
            if (points_x[i[0]] < points_x[i[1]]):
                b_corners[ni].append([points_x[i[0]], points_y[i[0]]])
                b_corners[ni].append([points_x[i[1]], points_y[i[1]]])
            else:
                b_corners[ni].append([points_x[i[1]], points_y[i[1]]])
                b_corners[ni].append([points_x[i[0]], points_y[i[0]]])

            if (points_x[i[2]] > points_x[i[3]]):
                b_corners[ni].append([points_x[i[2]], points_y[i[2]]])
                b_corners[ni].append([points_x[i[3]], points_y[i[3]]])
            else:
                b_corners[ni].append([points_x[i[3]], points_y[i[3]]])
                b_corners[ni].append([points_x[i[2]], points_y[i[2]]])
            ni = 1
        if (b_corners[0][0][0] > b_corners[1][0][0]):
            b_corners[1], b_corners[0] = b_corners[0], b_corners[1]
        return b_corners
    #else:
    #    raise Exception("Not enough qr code detected")

def convert_and_treshold_image(image_file_name, treshold=175, debug=True, debug_dir="."):
    image = cv2.imread(image_file_name)
    # Check original image's height to width ratio.
    if image.shape[0] / image.shape[1] < height_to_width_ratio:
    # Then rotate
        image = cv2.rotate(image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)

    file_path      = pathlib.Path(image_file_name)
    file_name      = file_path.name
    file_extension = file_path.suffix
    gray           = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #if debug is not None:
    #    cv2.imwrite(os.path.join(debug_dir, file_name.replace(file_extension, "_g.JPG")), gray)
    tresh          = cv2.threshold(gray, 175, 255, cv2.THRESH_BINARY)[1]
    #if debug is not None:
    #    cv2.imwrite(os.path.join(debug_dir, file_name.replace(file_extension, "_t.JPG")), tresh)
    return image, tresh

def generate_points_for_qr_codes(b_corners, table_shape=(760, 2310), qr_code_shape=(110,110)):
    points_left       = np.array([[b_corners[0][0][0], b_corners[0][0][1]], [b_corners[0][1][0], b_corners[0][1][1]],
                                 [b_corners[0][2][0], b_corners[0][2][1]], [b_corners[0][3][0], b_corners[0][3][1]]],
                                 np.int32)
    points_left_x     = np.array([b_corners[0][0][0], b_corners[0][1][0], b_corners[0][2][0], b_corners[0][3][0]],np.int32)
    points_left_y     = np.array([b_corners[0][0][1], b_corners[0][1][1], b_corners[0][2][1], b_corners[0][3][1]],np.int32)
    dist_left_low_y   = (points_left_y[3] - points_left_y[2])/ 2 
    dist_left_upp_y   = (points_left_y[0] - points_left_y[1])/ 2 
    dist_left_low_x   = (points_left_x[3] - points_left_x[2])/ 2 
    dist_left_upp_x   = (points_left_x[0] - points_left_x[1])/ 2
    dist_left_left_y  = (points_left_y[3] - points_left_y[0])/2
    dist_left_right_y = (points_left_y[2] - points_left_y[1])/2
    dist_left_left_x  = (points_left_x[3] - points_left_x[0])/2
    dist_left_right_x = (points_left_x[2] - points_left_x[1])/2

    left_midpoints    = np.array([[points_left_x[3]-dist_left_low_x, points_left_y[3]-dist_left_low_y], [points_left_x[0]-dist_left_upp_x, points_left_y[0]-dist_left_upp_y],[points_left_x[3]-dist_left_right_x,points_left_y[3]-dist_left_right_y], [points_left_x[2]-dist_left_left_x, points_left_y[2]-dist_left_left_y]], np.int32)
   
    points_left       = np.append(points_left, left_midpoints, axis =0).astype(np.float32)
    points_left_im    = np.array([[-qr_code_shape[0], int(-qr_code_shape[0])], [0, int(-qr_code_shape[0])], [0, 0], [-qr_code_shape[0], 0], [-qr_code_shape[0]/2,0],[-qr_code_shape[0]/2, int(-qr_code_shape[0])], [-qr_code_shape[0], int(-qr_code_shape[0]/2)], [0,int(-qr_code_shape[0]/2)]], np.int32)

    #RIGHT
    points_right = np.array([[b_corners[1][0][0], b_corners[1][0][1]], [b_corners[1][1][0], b_corners[1][1][1]],
                             [b_corners[1][2][0], b_corners[1][2][1]], [b_corners[1][3][0], b_corners[1][3][1]]],
                            np.int32)
   
    points_right_x     = np.array([b_corners[1][0][0], b_corners[1][1][0], b_corners[1][2][0], b_corners[1][3][0]],np.int32)
    points_right_y     = np.array([b_corners[1][0][1], b_corners[1][1][1], b_corners[1][2][1], b_corners[1][3][1]],np.int32)
    dist_right_low_y   = (points_right_y[3] - points_right_y[2])/ 2 
    dist_right_upp_y   = (points_right_y[0] - points_right_y[1])/ 2 
    dist_right_low_x   = (points_right_x[3] - points_right_x[2])/ 2 
    dist_right_upp_x   = (points_right_x[0] - points_right_x[1])/ 2
    dist_right_left_y  = (points_right_y[3] - points_right_y[0])/2
    dist_right_right_y = (points_right_y[2] - points_right_y[1])/2
    dist_right_left_x  = (points_right_x[3] - points_right_x[0])/2
    dist_right_right_x = (points_right_x[2] - points_right_x[1])/2

    right_midpoints    = np.array([[points_right_x[3]-dist_right_low_x, points_right_y[3]-dist_right_low_y], [points_right_x[0]-dist_right_upp_x, points_right_y[0]-dist_right_upp_y],[points_right_x[3]-dist_right_right_x,points_right_y[3]-dist_right_right_y], [points_right_x[2]-dist_right_left_x, points_right_y[2]-dist_right_left_y]], np.int32)
    points_right       = np.append(points_right, right_midpoints, axis =0).astype(np.float32)
    points_right_im    = np.array([[table_shape[0], int(-qr_code_shape[0])], [table_shape[0]+qr_code_shape[0], int(-qr_code_shape[0])], [table_shape[0]+qr_code_shape[0], 0], [table_shape[0], 0], [table_shape[0]+qr_code_shape[0]/2, 0], [table_shape[0]+qr_code_shape[0]/2, int(-qr_code_shape[0])], [table_shape[0], int(-qr_code_shape[0]/2)], [table_shape[0]+qr_code_shape[0], int(-qr_code_shape[0]/2)]], np.int32)
    points            = np.append(points_left, points_right, axis=0).astype(np.float32)
    points_im         = np.append(points_left_im, points_right_im, axis=0).astype(np.float32)
    pts               = points[[0,3,5,7]].astype(np.float32)
    dst               = points_im[[0,3,5,7]].astype(np.float32)
    return points, points_im, points_left, points_left_im, points_right, points_right_im, dst, pts

def transform_and_cut_table(image, M, debug=True, table_shape=(760, 2310), qr_code_shape=(110,110), debug_dir=".", original_file_name=None):
    finalimage = cv2.warpPerspective(image, M, table_shape)
    finalimage = finalimage[10:, ]
    if debug:
        file_path            = pathlib.Path(original_file_name)
        file_name            = file_path.name
        file_extension       = file_path.suffix
        table_polygon        = [np.array([[0, 0], [0, table_shape[1]], [table_shape[0], table_shape[1]],[table_shape[0], 0]])]
        #cv2.polylines(finalimage, table_polygon, True, (36, 255, 12), thickness=3)
        #cv2.polylines(finalimage, mid, True, (36, 12, 255), thickness=2)
        cv2.imwrite(os.path.join(debug_dir, file_name.replace(file_extension, ".JPG")), finalimage)
        image_t              = cv2.warpPerspective(finalimage, M, (image.shape[1], image.shape[0]), flags=cv2.WARP_INVERSE_MAP,
                                                   borderMode=cv2.BORDER_CONSTANT)
        image_tg             = cv2.cvtColor(image_t, cv2.COLOR_BGR2GRAY)
        image[image_tg != 0] = image[image_tg != 0] * 0
        #cv2.polylines(image, [cut_points], True, (36,255,12), thickness=3)
        #cv2.imwrite(os.path.join(out_dir, file_name.replace(file_extension, "._cut2.jpg")),image+ image_t)
    return finalimage, image_tg

def get_homography_matrix(source, destination):
    """ Calculates the entries of the Homography matrix between two sets of matching points.
    Args
    ----
        - `source`: Source points where each point is int (x, y) format.
        - `destination`: Destination points where each point is int (x, y) format.
    Returns
    ----
        - A numpy array of shape (3, 3) representing the Homography matrix.
    Raises
    ----
        - `source` and `destination` is lew than four points.
        - `source` and `destination` is of different size.
    """
    assert len(source) >= 4, "must provide more than 4 source points"
    assert len(destination) >= 4, "must provide more than 4 destination points"
    assert len(source) == len(destination), "source and destination must be of equal length"
    A = []
    b = []
    for i in range(len(source)):
        s_x, s_y = source[i]
        d_x, d_y = destination[i]
        A.append([s_x, s_y, 1, 0, 0, 0, (-d_x)*(s_x), (-d_x)*(s_y)])
        A.append([0, 0, 0, s_x, s_y, 1, (-d_y)*(s_x), (-d_y)*(s_y)])
        b += [d_x, d_y]
    A = np.array(A)
    h = np.linalg.lstsq(A, b)[0]
    h = np.concatenate((h, [1]), axis=-1)
    return np.reshape(h, (3, 3))

# Define parameters
in_dir  = '/home/golah/whiteboard_project/projects/edvard/images/original_images/'
out_dir = '/home/golah/whiteboard_project/projects/edvard/images/qrd_images/'
height_to_width_ratio = 0.70

for f in os.listdir(in_dir):
    print("IMG:", f)
    image, tresh = convert_and_treshold_image(os.path.join(in_dir, f), 175, True, out_dir)
    b_corners    = detect_qr_code(tresh)
    if b_corners == None:
        print(f, "skipped: Not enough QR-code detected") 
        continue
    qr_code_shape = (100, 100)  
    table_shape   = (500, 2025)
    points, points_im, points_left, points_left_im, points_right, points_right_im, dst, pts = generate_points_for_qr_codes(b_corners, table_shape, qr_code_shape)
    #M_1 = cv2.getPerspectiveTransform(points_left.astype(np.float32), points_left_im.astype(np.float32))
    #M_2, mask = cv2.findHomography(points, points_im)
    #M_3 = cv2.getPerspectiveTransform(points_right.astype(np.float32), points_right_im.astype(np.float32))
    M_4 = get_homography_matrix(points, points_im)
    finalimage = transform_and_cut_table(image, M_4, True, table_shape, qr_code_shape, out_dir, f)
