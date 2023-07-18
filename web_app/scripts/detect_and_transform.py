# Import packages
import cv2
import numpy as np
import os
import math
import pandas as pd
from itertools import combinations

# Create function to calculate Manhattan distance 
def manhattan(a, b):
    return sum(abs(val1-val2+val1/10000) for val1, val2 in zip(a,b))

# Create a function to calculate closest value 
def closest_value(input_list, input_value):
    arr = np.asarray(input_list) 
    i = (np.abs(arr - input_value)).argmin()
    return arr[i]

# Create a function that picks the n-th best corner of a given color 
def find_best_corner(color, corners, n):
    c_diff_values   = []
    if len(corners) > 1:
        for i in corners:
            c_diff_values.append(diff_values[i][0])
        c_diff_values_min = sorted(c_diff_values)[n]
        index_c_corner = corners[c_diff_values.index(c_diff_values_min)]
        locals()[color + "_corners"] = final_corners[index_c_corner]
    elif len(corners) == 1:
        locals()[color + "_corners"] = final_corners[corners[0]]
    return locals()[color + "_corners"]

# Create a function which determines the corner positions and calculate basic metrics
def determine_corner_positions(color, corners):
    x_axis          = np.array([corners[0][0], corners[1][0], corners[2][0], corners[3][0]])
    sorted_points   = x_axis.argsort()
    right_corners   = sorted_points[2:4]
    left_corners    = sorted_points[0:2]
    if corners[right_corners[0]][1] > corners[right_corners[1]][1]:
        globals()[color + "_up_right"]  = corners[right_corners[1]]
        globals()[color + "_bot_right"] = corners[right_corners[0]]
    else:
        globals()[color + "_up_right"]  = corners[right_corners[0]]
        globals()[color + "_bot_right"] = corners[right_corners[1]]
    if corners[left_corners[0]][1] > corners[left_corners[1]][1]:
        globals()[color + "_up_left"]   = corners[left_corners[1]]
        globals()[color + "_bot_left"]  = corners[left_corners[0]]
    else:
        globals()[color + "_up_left"]   = corners[left_corners[0]]
        globals()[color + "_bot_left"]  = corners[left_corners[1]]

    globals()["final_coord_" + color]        = [globals()[color + "_up_left"], globals()[color + "_up_right"], globals()[color + "_bot_left"], globals()[color + "_bot_right"]]
    globals()["atan_" + color]               = math.atan2(globals()[color + "_bot_left"][1] - globals()[color + "_up_left"][1], globals()[color + "_bot_left"][0] - globals()[color + "_up_left"][0])
    globals()["angle_" + color]              = 180 - math.degrees(globals()["atan_" + color])
    globals()["angle_" + color + "_rad"]     = - globals()["angle_" + color] * math.pi / 180 
    #globals()["atan_" + color + "_hor"]      = math.atan2(globals()[color + "_up_left"][1] - globals()[color + "_up_right"][1], globals()[color + "_up_left"][0] - globals()[color + "_up_right"][0])
    globals()["atan_" + color + "_hor"]      = math.atan2(globals()[color + "_bot_right"][1] - globals()[color + "_bot_left"][1], globals()[color + "_bot_right"][0] - globals()[color + "_bot_left"][0])
    #globals()["atan_" + color + "_hor"]      = math.atan2(globals()[color + "_bot_left"][0] * globals()[color + "_bot_right"][1] - globals()[color + "_bot_right"][0]* globals()[color + "_bot_left"][1], globals()[color + "_bot_left"][0] * globals()[color + "_bot_right"][0] + globals()[color + "_bot_left"][1] * globals()[color + "_bot_right"][1])
    #globals()["angle_" + color + "_hor"]     = 180 - abs(math.degrees(globals()["atan_" + color + "_hor"]))
    globals()["angle_" + color + "_hor"]     = - math.degrees(globals()["atan_" + color + "_hor"])
    globals()["angle_" + color + "_rad_hor"] = -globals()["angle_" + color + "_hor"] * math.pi / 180
    globals()[color + "_vert_l"]             = manhattan(globals()[color + "_up_left"], globals()[color + "_bot_left"])
    globals()[color + "_hor_l_up"]           = manhattan(globals()[color + "_up_left"], globals()[color + "_up_right"])
    globals()[color + "_hor_l_bot"]          = manhattan(globals()[color + "_bot_left"], globals()[color + "_bot_right"])
    globals()[color.upper()]                 = True


# Create a function that calculates manhattan distances between 2 rectangles.
def calculate_manhattan_distances(color_1, color_2):
        # Up left
        globals()[color_1 + "_" + color_2 + "_up_left_dist"]       = manhattan(globals()[color_1 + "_up_left"], globals()[color_2 + "_up_left"])
        #globals()["atan_" + color_1 + color_2 + "_up_left"]       = math.atan2(globals()[color_1 + "_up_left"][1] - globals()[color_2 + "_up_left"][1], globals()[color_1 + "_up_left"][0] - globals()[color_2 + "_up_left"][0])
        #globals()["angle_" + color_1 + color_2 + "_up_left"]      = 180 - abs(math.degrees(globals()["atan_" + color_1 + color_2 + "_up_left"]))
        #globals()["angle_" + color_1 + color_2 + "_up_left_rad"]  = - globals()["angle_" + color_1 + color_2 + "_up_left"] * math.pi / 180

        #if (color_1 == "r" and color_2 == "b") or (color_1 == "b" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_up_left"]  = abs(0 - abs(globals()["angle_" + color_1 + color_2 + "_up_left"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_up_left_dist"] = globals()[color_1 + "_" + color_2 +"_up_left_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_up_left"])
        #elif (color_1 == "r" and color_2 == "p") or (color_1 == "p" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_up_left"]  = abs(49 - abs(globals()["angle_" + color_1 + color_2 + "_up_left"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_up_left_dist"] = globals()[color_1 + "_" + color_2 +"_up_left_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_up_left"])
        #elif (color_1 == "b" and color_2 == "p") or (color_1 == "p" and color_2 == "b"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_up_left"]  = abs(131 - abs(globals()["angle_" + color_1 + color_2 + "_up_left"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_up_left_dist"] = globals()[color_1 + "_" + color_2 +"_up_left_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_up_left"])
        
        # Up right
        globals()[color_1 + "_" + color_2 + "_up_right_dist"]     = manhattan(globals()[color_1 + "_up_right"], globals()[color_2 + "_up_right"])
        #globals()["atan_" + color_1 + color_2 + "_up_right"]      = math.atan2(globals()[color_1 + "_up_right"][1] - globals()[color_2 + "_up_right"][1], globals()[color_1 + "_up_right"][0] - globals()[color_2 + "_up_right"][0])
        #globals()["angle_" + color_1 + color_2 + "_up_right"]     = 180 - abs(math.degrees(globals()["atan_" + color_1 + color_2 + "_up_right"]))
        #globals()["angle_" + color_1 + color_2 + "_up_right_rad"] = - globals()["angle_" + color_1 + color_2 + "_up_left"] * math.pi / 180
        #if (color_1 == "r" and color_2 == "b") or (color_1 == "b" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_up_right"]  = abs(0 - abs(globals()["angle_" + color_1 + color_2 + "_up_right"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_up_right_dist"] = globals()[color_1 + "_" + color_2 +"_up_right_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_up_right"])
        #elif (color_1 == "r" and color_2 == "p") or (color_1 == "p" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_up_right"]  = abs(49 - abs(globals()["angle_" + color_1 + color_2 + "_up_right"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_up_right_dist"] = globals()[color_1 + "_" + color_2 +"_up_right_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_up_right"])
        #elif (color_1 == "b" and color_2 == "p") or (color_1 == "p" and color_2 == "b"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_up_right"]  = abs(131 - abs(globals()["angle_" + color_1 + color_2 + "_up_right"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_up_right_dist"] = globals()[color_1 + "_" + color_2 +"_up_right_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_up_right"])


        # Bot left
        globals()[color_1 + "_" + color_2 + "_bot_left_dist"]     = manhattan(globals()[color_1 + "_bot_left"], globals()[color_2 + "_bot_left"])
        #globals()["atan_" + color_1 + color_2 + "_bot_left"]      = math.atan2(globals()[color_1 + "_bot_left"][1] - globals()[color_2 + "_bot_left"][1], globals()[color_1 + "_bot_left"][0] - globals()[color_2 + "_bot_left"][0])
        #globals()["angle_" + color_1 + color_2 + "_bot_left"]     = 180 - abs(math.degrees(globals()["atan_" + color_1 + color_2 + "_bot_left"]))
        #globals()["angle_" + color_1 + color_2 + "_bot_left_rad"] = - globals()["angle_" + color_1 + color_2 + "_bot_left"] * math.pi / 180
        #if (color_1 == "r" and color_2 == "b") or (color_1 == "b" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_bot_left"]  = abs(0 - abs(globals()["angle_" + color_1 + color_2 + "_bot_left"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_bot_left_dist"] = globals()[color_1 + "_" + color_2 +"_bot_left_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_bot_left"])
        #elif (color_1 == "r" and color_2 == "p") or (color_1 == "p" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_bot_left"]  = abs(49 - abs(globals()["angle_" + color_1 + color_2 + "_bot_left"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_bot_left_dist"] = globals()[color_1 + "_" + color_2 +"_bot_left_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_bot_left"])
        #elif (color_1 == "b" and color_2 == "p") or (color_1 == "p" and color_2 == "b"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_bot_left"]  = abs(131 - abs(globals()["angle_" + color_1 + color_2 + "_bot_left"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_bot_left_dist"] = globals()[color_1 + "_" + color_2 +"_bot_left_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_bot_left"])
        
        # Bot right
        globals()[color_1 + "_" + color_2 + "_bot_right_dist"]     = manhattan(globals()[color_1 + "_bot_right"], globals()[color_2 + "_bot_right"])
        #globals()["atan_" + color_1 + color_2 + "_bot_right"]      = math.atan2(globals()[color_1 + "_bot_right"][1] - globals()[color_2 + "_bot_right"][1], globals()[color_1 + "_bot_right"][0] - globals()[color_2 + "_bot_right"][0])
        #globals()["angle_" + color_1 + color_2 + "_bot_right"]     = 180 - abs(math.degrees(globals()["atan_" + color_1 + color_2 + "_bot_right"]))
        #globals()["angle_" + color_1 + color_2 + "_bot_right_rad"] = - globals()["angle_" + color_1 + color_2 + "_bot_right"] * math.pi / 180
        #if (color_1 == "r" and color_2 == "b") or (color_1 == "b" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_bot_right"]  = abs(0 - abs(globals()["angle_" + color_1 + color_2 + "_bot_right"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_bot_right_dist"] = globals()[color_1 + "_" + color_2 +"_bot_right_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_bot_right"])
        #elif (color_1 == "r" and color_2 == "p") or (color_1 == "p" and color_2 == "r"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_bot_right"]  = abs(49 - abs(globals()["angle_" + color_1 + color_2 + "_bot_right"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_bot_right_dist"] = globals()[color_1 + "_" + color_2 +"_bot_right_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_bot_right"])
        #elif (color_1 == "b" and color_2 == "p") or (color_1 == "p" and color_2 == "b"):
        #    globals()["manhattan_weight_" + color_1 + color_2 + "_bot_right"]  = abs(131 - abs(globals()["angle_" + color_1 + color_2 + "_bot_right"])) * 0.01111111111
        #    globals()[color_1 + "_" + color_2 + "_bot_right_dist"] = globals()[color_1 + "_" + color_2 +"_bot_right_dist"] / (1 - globals()["manhattan_weight_" + color_1 + color_2 +"_bot_right"])
        
        globals()[color_1 + color_2 + "_dist"]                     = [globals()[color_1 + "_" + color_2 + "_up_left_dist"], globals()[color_1 + "_" + color_2 + "_up_right_dist"], globals()[color_1 + "_" + color_2 + "_bot_left_dist"], globals()[color_1 + "_" + color_2 + "_bot_right_dist" ]]
        print("CALC_DIST", color_1, color_2, globals()[color_1 + color_2 + "_dist"])

# Create a function which determines theoretical lengths and angles based on found rectangles
def determine_theoretical_lengths_and_angles(colors):
    if len(colors) == 3:
        globals()["vert_l"            ] = [globals()[colors[0] + "_vert_l"], globals()[colors[1] + "_vert_l"], globals()[colors[2] + "_vert_l"]]
        globals()["hor_l_up"          ] = [globals()[colors[0] + "_hor_l_up"], globals()[colors[1] + "_hor_l_up"], globals()[colors[2] + "_hor_l_up"]]
        globals()["hor_l_bot"         ] = [globals()[colors[0] + "_hor_l_bot"], globals()[colors[1] + "_hor_l_bot"], globals()[colors[2] + "_hor_l_bot"]]
        globals()["vert_angles"       ] = [globals()["angle_" + colors[0]], globals()["angle_" + colors[1]], globals()["angle_" + colors[2]]]
        globals()["hor_angles"        ] = [globals()["angle_" + colors[0] + "_hor"], globals()["angle_" + colors[1] + "_hor"], globals()["angle_" + colors[2]+ "_hor"]]
        globals()[colors[0] + "_index"] = 0
        globals()[colors[1] + "_index"] = 1
        globals()[colors[2] + "_index"] = 2
    elif len(colors) == 2:
        globals()["vert_l"            ] = [globals()[colors[0] + "_vert_l"], globals()[colors[1] + "_vert_l"]]
        globals()["hor_l_up"          ] = [globals()[colors[0] + "_hor_l_up"], globals()[colors[1] + "_hor_l_up"]]
        globals()["hor_l_bot"         ] = [globals()[colors[0] + "_hor_l_bot"], globals()[colors[1] + "_hor_l_bot"]]
        globals()["vert_angles"       ] = [globals()["angle_" + colors[0]], globals()["angle_" + colors[1]]]
        globals()["hor_angles"        ] = [globals()["angle_" + colors[0] + "_hor"], globals()["angle_" + colors[1] + "_hor"]]
        globals()[colors[0] + "_index"] = 0
        globals()[colors[1] + "_index"] = 1
    elif len(colors) == 1:
        globals()["vert_l"            ] = [globals()[colors[0] + "_vert_l"]]
        globals()["hor_l_up"          ] = [globals()[colors[0] + "_hor_l_up"]]
        globals()["hor_l_bot"         ] = [globals()[colors[0] + "_hor_l_bot"]]
        globals()["vert_angles"       ] = [globals()["angle_" + colors[0]]]
        globals()["hor_angles"        ] = [globals()["angle_" + colors[0] + "_hor"]]
        globals()[colors[0] + "_index"] = 0
# Define base params
# Low res:
    #globals()["theoretical_length"                ] = 60
    #globals()["moe"                               ] = 0.15 * theoretical_length
# High res:
    globals()["theoretical_length"                ] = 170
    globals()["moe"                               ] = 0.085 * theoretical_length
    globals()["theoretical_angle"                 ] = 90
    globals()["theoretical_angle_rad"             ] = -theoretical_angle * math.pi / 180
    globals()["theoretical_angle_hor"             ] = 0
    globals()["theoretical_angle_rad_hor"         ] = 0
    globals()["moe_angle"                         ] = 4.5
    globals()["theoretical_distance_rb_multiplier"] = 5.20
    globals()["theoretical_distance_p_multiplier" ] = 5.60
    globals()["hor_l"                             ] = hor_l_up + hor_l_bot
# Use values inside margin of error
    print("VERT_L---------", vert_l)
    print("HOR_L----------", hor_l)
    globals()["vert_l_mod"    ] = [i for i in vert_l if theoretical_length + moe  > i > theoretical_length - moe ]
    globals()["hor_l_mod" ] = [i for i in hor_l if theoretical_length + moe  > i > theoretical_length - moe ]
    #globals()["lengths"   ] = vert_l_mod + hor_l_mod
    globals()["lengths"       ] =  hor_l_mod
    lengths.append(theoretical_length)
    print("LEEEEEEEEEEEEEENG", lengths)
    globals()["lengths_mean"      ] = sum(lengths) / len(lengths)
    globals()["theoretical_length"] = closest_value(lengths, lengths_mean)
    globals()["moe"               ] = 0.10 * theoretical_length
    globals()["vert_angles_mod"   ] = [i for i in vert_angles if theoretical_angle + moe_angle  > i > theoretical_angle - moe_angle]
    globals()["hor_angles_mod"    ] = [i for i in hor_angles if theoretical_angle_hor + moe_angle > i > theoretical_angle_hor - moe_angle]
    globals()["vert_angles_diff"  ] = max(vert_angles) - min(vert_angles)
    globals()["hor_angles_diff"   ] = max(hor_angles) - min(hor_angles)
    vert_angles_mod.append(90)
    hor_angles_mod.append(0)
    globals()["vert_angles_mean"       ] = sum(vert_angles_mod) / len(vert_angles_mod)
    globals()["hor_angles_mean"        ] = sum(hor_angles_mod) / len(hor_angles_mod)
    #if len(hor_angles_mod) > 1:
        #globals()["hor_angles_mean_weight" ] = sum(hor_angles_mod[:-1]) / len(hor_angles_mod[:-1])
        #manhattan_weight_rb  = abs(0 - abs(hor_angles_mean_weight)) * 0.01111111111
        #globals()["theoretical_distance_rb_multiplier"] = theoretical_distance_rb_multiplier / (1 - manhattan_weight_rb)
        #manhattan_weight_rp  = abs(0 - abs(hor_angles_mean_weight)) * 0.01111111111
        #globals()["theoretical_distance_rp_multiplier"]  = theoretical_distance_p_multiplier / (1 - manhattan_weight_rp)
        #manhattan_weight_bp  = abs(0 - abs(hor_angles_mean_weight)) * 0.01111111111
        #globals()["theoretical_distance_bp_multiplier"]  = theoretical_distance_p_multiplier / (1 - manhattan_weight_bp)
        #globals()["theoretical_distance_rb" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_rb_multiplier)
        #globals()["theoretical_distance_rp" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_rp_multiplier)
        #globals()["theoretical_distance_bp" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_bp_multiplier)
    #else:
        #globals()["theoretical_distance_rb" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_rb_multiplier)
        #globals()["theoretical_distance_rp" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_p_multiplier)
        #globals()["theoretical_distance_bp" ] = theoretical_distance_rp
    if angle_r_hor != [] and angle_b_hor != []:
        manhattan_weight_rb  = abs(angle_r_hor - angle_b_hor) * 0.020
        globals()["theoretical_distance_rb_multiplier"] = theoretical_distance_rb_multiplier * (1 - manhattan_weight_rb)
        globals()["theoretical_distance_rb" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_rb_multiplier)
        print("MAAAAAAAAAAAAN_RB", theoretical_distance_rb_multiplier, manhattan_weight_rb,theoretical_distance_rb, angle_b_hor, angle_r_hor)
    else:
        globals()["theoretical_distance_rb" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_rb_multiplier)
    if angle_r_hor != [] and angle_p_hor != []:
        #manhattan_weight_rp  = abs(angle_p_hor - angle_r_hor) * 0.0095
        manhattan_weight_rp  = abs(angle_r_hor - angle_p_hor) * 0.0095
        globals()["theoretical_distance_rp_multiplier"]  = theoretical_distance_p_multiplier * (1 - manhattan_weight_rp)
        globals()["theoretical_distance_rp" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_rp_multiplier)
        print("MAAAAAAAAAAAAN_RP", theoretical_distance_rp_multiplier, manhattan_weight_rp,theoretical_distance_rp, angle_p_hor, angle_r_hor)
    else:
        globals()["theoretical_distance_rp" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_p_multiplier)

    if angle_b_hor != [] and angle_p_hor != []:
        manhattan_weight_bp  = abs(angle_p_hor - angle_b_hor) * 0.0095
        globals()["theoretical_distance_bp_multiplier"]  = theoretical_distance_p_multiplier * (1 - manhattan_weight_bp)
        globals()["theoretical_distance_bp" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_bp_multiplier)
        print("MAAAAAAAAAAAAN", theoretical_distance_bp_multiplier, manhattan_weight_bp,theoretical_distance_bp, angle_p_hor, angle_b_hor)
    else:
        globals()["theoretical_distance_bp" ] = closest_value(lengths, theoretical_length) * (theoretical_distance_p_multiplier)
    #globals()["moe_dist"                ] = 0.01810
    globals()["theoretical_distance_br" ] = theoretical_distance_rb
    globals()["theoretical_distance_pr" ] = theoretical_distance_rp
    globals()["theoretical_distance_pb" ] = theoretical_distance_bp
    globals()["moe_dist"                ] = 0.019
    globals()["moe_dist_rb"             ] = 0.045 * theoretical_distance_rb
    globals()["moe_dist_br"             ] = moe_dist_rb
    globals()["moe_dist_rp"             ] = 0.045 * theoretical_distance_rp
    globals()["moe_dist_pr"             ] = moe_dist_rp
    globals()["moe_dist_bp"             ] = 0.045 * theoretical_distance_bp
    globals()["moe_dist_pb"             ] = moe_dist_bp

# Create a function that determines safe corners based on corner distances
def determine_safe_corners(color_1, color_2):
    globals()[color_1 + color_2 + "_diff"] = max(globals()[color_1 + color_2 + "_dist"]) - min(globals()[color_1 + color_2 + "_dist"])
    globals()[color_1 + color_2 + "_mean"] = sum(globals()[color_1 + color_2 + "_dist"]) / len(globals()[color_1 + color_2 + "_dist"])
    print("TEST--------------------------", globals()[color_1 + color_2 + "_diff"], globals()[color_1 + color_2 + "_mean"] * moe_dist)
    if globals()[color_1 + color_2 + "_diff"] < globals()[color_1 + color_2 + "_mean"] * moe_dist and globals()["theoretical_distance_" + color_1 + color_2] - globals()["moe_dist_" + color_1 + color_2] < globals()[color_1 + color_2 + "_mean"] < globals()["theoretical_distance_" + color_1 + color_2] + globals()["moe_dist_" + color_1 + color_2]:
        reference_1 = closest_value(globals()[color_1 + color_2 + "_dist"], globals()["theoretical_distance_" + color_1 + color_2])
        index_ref_1 = globals()[color_1 + color_2 + "_dist"].index(reference_1)
        dist_sliced = globals()[color_1 + color_2 + "_dist"][:index_ref_1] + globals()[color_1 + color_2 + "_dist"][index_ref_1 + 1:]
        reference_2 = closest_value(dist_sliced, globals()["theoretical_distance_" + color_1 + color_2])
        globals()[color_1 + color_2 + "_dist"][index_ref_1] = reference_1
        index_ref_2 = globals()[color_1 + color_2 + "_dist"].index(reference_2)
        if (index_ref_1 == 0 or index_ref_1 == 2) and (index_ref_2 == 2 or index_ref_2 == 0):
            globals()["safe_corners_" + color_1 + color_2] = [ "up_left", "bot_left"]
        elif (index_ref_1 == 0 or index_ref_1 == 1) and (index_ref_2 == 1 or index_ref_2 == 0):
            globals()["safe_corners_" + color_1 + color_2] = [ "up_left", "up_right"]
        elif (index_ref_1 == 2 or index_ref_1 == 3) and (index_ref_2 == 3 or index_ref_2 == 2):
            globals()["safe_corners_" + color_1 + color_2] = [ "bot_left", "bot_right"]
        elif (index_ref_1 == 1 or index_ref_1 == 3) and (index_ref_2 == 3 or index_ref_2 == 1):
            globals()["safe_corners_" + color_1 + color_2] = [ "up_right", "bot_right"]
        elif (index_ref_1 == 0 or index_ref_1 == 3) and (index_ref_2 == 3 or index_ref_2 == 0):
            globals()["safe_corners_" + color_1 + color_2] = [ "up_left", "bot_right"]
        elif (index_ref_1 == 1 or index_ref_1 == 2) and (index_ref_2 == 2 or index_ref_2 == 1):
            globals()["safe_corners_" + color_1 + color_2] = [ "up_right", "bot_left"]

# Create a function to verify corners based on the reference rectangle size and angle
def verify_safe_corners(n):
    if n == 3:
        if all(i == 90 for i in vert_angles[:3]):
            reference_vert  = closest_value(vert_l, theoretical_length)
            index_ref_angle = vert_l.index(reference_vert)
        else:
            reference_angle = closest_value(vert_angles[:3], vert_angles_mean)
            index_ref_angle = vert_angles.index(reference_angle)
        print("DEBUG--------------------------------------------", hor_l[index_ref_angle], vert_l[index_ref_angle], theoretical_length)
        if hor_l[index_ref_angle] >= theoretical_length - moe and hor_l[index_ref_angle] <= theoretical_length + moe and vert_l[index_ref_angle] >= theoretical_length - moe and vert_l[index_ref_angle] <= theoretical_length + moe:
            if index_ref_angle == 0:
                if safe_corners_rb != []:
                    globals()["safe_corners_r"] = safe_corners_rb
                    globals()["safe_corners_b"] = safe_corners_rb
                elif safe_corners_bp != [] and hor_l[2] >= theoretical_length - moe and hor_l[2] <= theoretical_length + moe and vert_l[2] >= theoretical_length - moe and vert_l[2] <= theoretical_length + moe:
                    globals()["safe_corners_b"] = safe_corners_bp
                    globals()["safe_corners_p"] = safe_corners_bp
                if safe_corners_rp != []:
                    globals()["safe_corners_p"] = safe_corners_rp
                    globals()["safe_corners_r"] = safe_corners_rp
                elif safe_corners_bp != [] and hor_l[1] >= theoretical_length - moe and hor_l[1] <= theoretical_length + moe and vert_l[1] >= theoretical_length - moe and vert_l[1] <= theoretical_length + moe:
                    globals()["safe_corners_p"] = safe_corners_bp
                    globals()["safe_corners_b"] = safe_corners_bp
            if index_ref_angle == 1:
                if safe_corners_rb != []:
                    globals()["safe_corners_r"] = safe_corners_rb
                    globals()["safe_corners_b"] = safe_corners_rb
                elif safe_corners_rp != [] and hor_l[2] >= theoretical_length - moe and hor_l[2] <= theoretical_length + moe and vert_l[2] >= theoretical_length - moe and vert_l[2] <= theoretical_length + moe:
                    globals()["safe_corners_r"] = safe_corners_rp
                    globals()["safe_corners_p"] = safe_corners_rp
                if safe_corners_bp != []:
                    globals()["safe_corners_p"] = safe_corners_bp
                    globals()["safe_corners_b"] = safe_corners_bp
                elif safe_corners_rp != [] and hor_l[0] >= theoretical_length - moe and hor_l[0] <= theoretical_length + moe and vert_l[0] >= theoretical_length - moe and vert_l[0] <= theoretical_length + moe:
                    globals()["safe_corners_p"] = safe_corners_rp
                    globals()["safe_corners_r"] = safe_corners_rp
            if index_ref_angle == 2:
                if safe_corners_rp != []:
                    globals()["safe_corners_r"] = safe_corners_rp
                    globals()["safe_corners_p"] = safe_corners_rp
                elif safe_corners_rb != [] and hor_l[1] >= theoretical_length - moe and hor_l[1] <= theoretical_length + moe and vert_l[1] >= theoretical_length - moe and vert_l[1] <= theoretical_length + moe:
                    globals()["safe_corner_r"] = safe_corners_rb
                    globals()["safe_corner_b"] = safe_corners_rb
                if safe_corners_bp != []:
                    globals()["safe_corners_b"] = safe_corners_bp
                    globals()["safe_corners_p"] = safe_corners_bp
                elif safe_corners_rb != [] and hor_l[0] >= theoretical_length - moe and hor_l[0] <= theoretical_length + moe and vert_l[0] >= theoretical_length - moe and vert_l[0] <= theoretical_length + moe:
                    globals()["safe_corners_b"] = safe_corners_rb
                    globals()["safe_corners_r"] = safe_corners_rb
        else:
            if all(i == 90 for i in vert_angles):
                vert_l_sliced = vert_l[:index_ref_angle] + vert_l[index_ref_angle +1 :-1]
                reference_angle_2 = closest_value(vert_l_sliced, theoretical_length)
                index_ref_angle_2 = vert_l_sliced.index(reference_angle_2)
            else:
                vert_angles_sliced = vert_angles[:index_ref_angle] + vert_angles[index_ref_angle +1 :-1]
                reference_angle_2 = closest_value(vert_angles_sliced, vert_angles_mean)
                index_ref_angle_2 = vert_angles_sliced.index(reference_angle_2)
                if index_ref_angle == 0:
                    index_ref_angle_2 = index_ref_angle_2 + 1
                elif index_ref_angle == 1 and index_ref_angle_2 == 0:
                    index_ref_angle_2 == index_ref_angle_2
                elif index_ref_angle == 1 and index_ref_angle_2 == 1:
                    index_ref_angle_2 == index_ref_angle_2 + 1
            print("Reference_angle_index_2:", index_ref_angle_2)
            if (hor_l[index_ref_angle_2] >= theoretical_length - moe and hor_l[index_ref_angle_2] <= theoretical_length + moe) and (vert_l[index_ref_angle_2] >= theoretical_length - moe  and vert_l[index_ref_angle_2] <= theoretical_length + moe):
                if index_ref_angle_2 == 0:
                    if safe_corners_rb != []:
                        globals()["safe_corners_r"] = safe_corners_rb
                        globals()["safe_corners_b"] = safe_corners_rb
                    if safe_corners_rp != []:
                        globals()["safe_corners_p"] = safe_corners_rp
                        globals()["safe_corners_r"] = safe_corners_rp
                elif index_ref_angle_2 == 1:
                    if safe_corners_rb != []:
                        globals()["safe_corners_r"] = safe_corners_rb
                        globals()["safe_corners_b"] = safe_corners_rb
                    if safe_corners_bp != []:
                        globals()["safe_corners_p"] = safe_corners_bp
                        globals()["safe_corners_b"] = safe_corners_bp
                elif index_ref_angle_2 == 2:
                    if safe_corners_rp != []:
                        globals()["safe_corners_r"] = safe_corners_rp
                        globals()["safe_corners_p"] = safe_corners_rp
                    if safe_corners_bp != []:
                        globals()["safe_corners_b"] = safe_corners_bp
                        globals()["safe_corners_p"] = safe_corners_bp
    elif n == 2:
        reference_found = False
        if safe_corners_rb != []:
            globals()["safe_corners_r"] = safe_corners_rb
            globals()["safe_corners_b"] = safe_corners_rb
        elif safe_corners_rp != []:
            globals()["safe_corners_r"] = safe_corners_rp
            globals()["safe_corners_p"] = safe_corners_rp
        elif safe_corners_bp != []:
            globals()["safe_corners_b"] = safe_corners_bp
            globals()["safe_corners_p"] = safe_corners_bp
# If no safe corner, use closest to theoretical
        elif all(i == 90 for i in vert_angles[:3]):
            reference_vert  = closest_value(vert_l, theoretical_length)
            index_ref_angle = vert_l.index(reference_vert)
            reference_found = True
        else:
            reference_angle = closest_value(vert_angles[:3], vert_angles_mean)
            index_ref_angle = vert_angles.index(reference_angle)
            reference_found = True
        if reference_found == True:
            if hor_l[index_ref_angle] >= theoretical_length - moe and hor_l[index_ref_angle] <= theoretical_length + moe and vert_l[index_ref_angle] >= theoretical_length - moe and vert_l[index_ref_angle] <= theoretical_length + moe:
                print("Using best corner compared to theoretical value.")
                if index_ref_angle == 0 and R == True and B == True:
                    globals()["safe_corners_r"] = [1, 1]
                elif index_ref_angle == 1 and R == True and B == True:
                    globals()["safe_corners_b"] = [1, 1]
                elif index_ref_angle == 0 and R == True and P == True:
                    globals()["safe_corners_r"] = [1, 1]
                elif index_ref_angle == 1 and R == True and P == True:
                    globals()["safe_corners_p"] = [1, 1]
                elif index_ref_angle == 0 and B == True and P == True:
                    globals()["safe_corners_b"] = [1, 1]
                elif index_ref_angle == 1 and B == True and P == True:
                    globals()["safe_corners_p"] = [1, 1]
    elif n == 1:
        reference_vert  = closest_value(vert_l, theoretical_length)
        index_ref_angle = vert_l.index(reference_vert)
        if hor_l[index_ref_angle] >= theoretical_length - moe and hor_l[index_ref_angle] <= theoretical_length + moe and vert_l[index_ref_angle] >= theoretical_length - moe and vert_l[index_ref_angle] <= theoretical_length + moe and R == True:
                print("Using best corner compared to theoretical value.")
                globals()["safe_corners_r"] = [1, 1]
        elif hor_l[index_ref_angle] >= theoretical_length - moe and hor_l[index_ref_angle] <= theoretical_length + moe and vert_l[index_ref_angle] >= theoretical_length - moe and vert_l[index_ref_angle] <= theoretical_length + moe and B == True:
                print("Using best corner compared to theoretical value.")
                globals()["safe_corners_b"] = [1, 1]
        elif hor_l[index_ref_angle] >= theoretical_length - moe and hor_l[index_ref_angle] <= theoretical_length + moe and vert_l[index_ref_angle] >= theoretical_length - moe and vert_l[index_ref_angle] <= theoretical_length + moe and P == True:
                print("Using best corner compared to theoretical value.")
                globals()["safe_corners_p"] = [1, 1]

# Create a function which tries the top 3 rectangles in case of no safe corner
def corrigate_using_other_rectangles(main_color, color_1 = 0, color_2 = 0):
    if len(globals()["index_" + main_color + "_corner"]) >= 3:
            for i in range(1, 3, 1):
                if globals()["safe_corners_" + main_color] == [0, 0]:
                    globals()[main_color + "_corners"] = find_best_corner(main_color, globals()["index_" + main_color + "_corner"], i)
                    determine_corner_positions(main_color, globals()[main_color + "_corners"])
                    if color_1 != 0 and color_2 != 0:
                        determine_theoretical_lengths_and_angles([main_color, color_1, color_2])
                        calculate_manhattan_distances(main_color, color_1)
                        calculate_manhattan_distances(main_color, color_2)
                        print("RP_DIST", rp_dist)
                        determine_safe_corners(main_color, color_1)
                        determine_safe_corners(main_color, color_2)
                        verify_safe_corners(3)
                    elif color_1 != 0 and color_2 == 0:
                        determine_theoretical_lengths_and_angles([main_color, color_1])
                        calculate_manhattan_distances(main_color, color_1)
                        determine_safe_corners(main_color, color_1)
                        verify_safe_corners(2)
                    elif color_1 == 0 and color_2 != 0:
                        determine_theoretical_lengths_and_angles([main_color, color_2])
                        calculate_manhattan_distances(main_color, color_2)
                        determine_safe_corners(main_color, color_2)
                        verify_safe_corners(2)
                else:
                    break
    elif len(globals()["index_" + main_color + "_corner"]) == 2:
        globals()[main_color + "_corners"] = find_best_corner(main_color, globals()["index_" + main_color + "_corner"], 1)
        determine_corner_positions(main_color, globals()[main_color + "_corners"])
        if color_1 != 0 and color_2 != 0:
            determine_theoretical_lengths_and_angles([main_color, color_1, color_2])
            calculate_manhattan_distances(main_color, color_1)
            calculate_manhattan_distances(main_color, color_2)
            determine_safe_corners(main_color, color_1)
            determine_safe_corners(main_color, color_2)
            verify_safe_corners(3)
        elif color_1 != 0 and color_2 == 0:
            determine_theoretical_lengths_and_angles([main_color, color_1])
            calculate_manhattan_distances(main_color, color_1)
            determine_safe_corners(main_color, color_1)
            verify_safe_corners(2)
        elif color_1 == 0 and color_2 != 0:
            determine_theoretical_lengths_and_angles([main_color, color_2])
            calculate_manhattan_distances(main_color, color_2)
            determine_safe_corners(main_color, color_2)
            verify_safe_corners(2)


# Create a function to determine points form a Rectangle
def isRect(points, threshold, h, w):
    h = h
    w = w
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
        #atan_bot                          = math.atan2(bot_right[1] - bot_left[1], bot_right[0] - bot_left[0])
        #angle_bot                         = 180 - math.degrees(atan_bot)
        distances_from_other_corners_diff = max(distances_from_other_corners) - min(distances_from_other_corners)  
        distances_from_other_corners_mean = sum(distances_from_other_corners) / len(distances_from_other_corners)
        relative_distances_from_other_corners_diff = ((distances_from_other_corners_diff/ 4.4) +  (distances_from_other_corners_mean) + distances_diff * distances_mean) 
        #if (distances_from_other_corners_diff < distances_from_other_corners_mean * (threshold * 2.35 )) and w /7.7 < distances_from_other_corners_mean < w / 6.95:
        #if (distances_from_other_corners_diff < distances_from_other_corners_mean * (threshold * 2.35 )) and w / 7.7 < d_left < w / 6.70 and w / 7.7 < d_right < w / 6.70 and w / 7.7 < d_top < w / 6.70 and w / 7.7 < d_bot < w / 6.70:
        # Megkéne nézni, hogy a generátoros megoldás gyorsabban fut-e, updatelni nyilván könnyebb
        #if (distances_from_other_corners_diff < distances_from_other_corners_mean * (threshold * 2.35 )) and all(w / 7.8 < i < w / 6.50 for i in distances_from_other_corners):
        if (distances_from_other_corners_diff < distances_from_other_corners_mean * (threshold * 2.35 )) and all(w / 8 < i < w / 6.50 for i in distances_from_other_corners):
            print("DIFF", distances_from_other_corners_diff, "THRESH", distances_from_other_corners_mean * (threshold *2.35), "MEAN", distances_from_other_corners_mean, "RELATIVE MEAN", relative_distances_from_other_corners_diff, "CENTROID_DIST", distances_diff, "CENTROID_MEAN", distances_mean)
            #print("DISTANCES", d_left, d_right, d_top, d_bot)
            if cx < w/3:
                diff_values.append([relative_distances_from_other_corners_diff, "R"])
            elif w/3 < cx < w*2/3:
                diff_values.append([relative_distances_from_other_corners_diff, "P"])
            elif w*2/3 < cx:
                diff_values.append([relative_distances_from_other_corners_diff, "B"])
            return True
    return False

### Detect keypoints and transform images
def detect_and_transform(orig_path, project_dir, board_height = 105, board_width = 35, rect_l = 5, r_gap_top = 0, r_gap_side = 2, b_gap_top = 0, b_gap_side = 2, p_gap_top = 15, p_gap_side = 15):
    crop_output           = project_dir + 'images/cropped_images/'  ## output containing crop results
    edge_detection_output = project_dir + 'images/edge_detected_images/'
    transform_output      = project_dir + 'images/transformed_images/'
    original_image_input  = orig_path
    cut_coord_path        = project_dir + 'results/cut_coords.csv'
    c_coords = pd.read_csv(cut_coord_path, sep = ";", header = None, index_col = 0, squeeze = True).to_dict()
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

    for file in os.listdir(crop_output):
        #file = "PA042208.JPG"
        ## Define base params
        image_full_path          = os.path.join(crop_output, file)
        image                    = cv2.imread(image_full_path)
        print("Image:", file)
        h,w                      = image.shape[:2]
        original_image_full_path = os.path.join(original_image_input, file)
        orig_image               = cv2.imread(original_image_full_path)
        globals()["cc"]          = c_coords[file].split(',')
        globals()["cc"][0]       = cc[0][1:]
        globals()["cc"][2]       = cc[2][:-1]
        globals()["R"]             = False
        globals()["B"]             = False
        globals()["P"]             = False
        globals()["final_coord_r"] = None
        globals()["final_coord_b"] = None
        globals()["final_coord_p"] = None
    
    # Examine table shade
        l           = 20
        m           = l / 2
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
    
    ### SubPixel accuracy corner finding using Shi_Thomasi detector
    #   Split box image then detect keypoints
    #   Red
        red = gray[:round(h/3.15), round(w*0.02):round(w/4)]
        corners_r = cv2.goodFeaturesToTrack(image = red, maxCorners = 45, qualityLevel = 0.20, minDistance = 5, blockSize = 6)
        corners_r = np.int0(corners_r)
        # Draw found points
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
        corrected_corners_r = cv2.cornerSubPix(red,np.float32(corners_r),(3,3),(-1,-1),criteria)
        #corrected_corners_r = corners_r
        corner_dummy_r      = []
        #print("RED_CORRECTED", corrected_corners_r)
        for n, i in enumerate(corrected_corners_r):
            x,y = i.ravel()
            corner_dummy_r.append([x+w*0.02, y])
            # Draw subpixel corrected points
            cv2.circle(image,(round(x+w*0.02),round(y)),1,(255,0,0),-1)
        corrected_corners_r = corner_dummy_r
    
    #   Blue
        blue = gray[:round(h/3.15), round(w*0.75):-round(w*0.02)]
        corners_b = cv2.goodFeaturesToTrack(image = blue, maxCorners = 35, qualityLevel = 0.325, minDistance = 3, blockSize = 6)
        corners_b = np.int0(corners_b)
        # Draw found points
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
        corrected_corners_b = cv2.cornerSubPix(blue,np.float32(corners_b),(3,6),(-1,-1),criteria)
        #corrected_corners_b = corners_b
        corner_dummy_b      = []
        #print("BLUE_CORRECTED", corrected_corners_b)
        for n, i in enumerate(corrected_corners_b):
            x,y = i.ravel()
            corner_dummy_b.append([x+w*0.75, y])
            # Draw subpixel corrected points
            cv2.circle(image,(round(x+w*0.75),round(y)),1,(0,255,0),-1)
        corrected_corners_b = corner_dummy_b
    
    #   Purple
        purple = gray[round(h*0.625):, round(w*0.4):round(w*0.66)]
        corners_p = cv2.goodFeaturesToTrack(image = purple, maxCorners = 25, qualityLevel = 0.25, minDistance = 5, blockSize = 3)
        corners_p = np.int0(corners_p)
        # Draw found points
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
        corrected_corners_p = cv2.cornerSubPix(purple,np.float32(corners_p),(3,3),(-1,-1),criteria)
        corner_dummy_p = []
        #print("PURPLE_CORRECTED", corrected_corners_p)
        for n, i in enumerate(corrected_corners_p):
            x,y = i.ravel()
            corner_dummy_p.append([x+w*0.4, y+h*0.625])
            # Draw subpixel corrected points
            cv2.circle(image,(round(x+w*0.4),round(y+h*0.625)),1,(255,0,255),-1)
        corrected_corners_p = corner_dummy_p  
        #cv2.imshow('dst', purple)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
    
        globals()["final_corners"] = []
        globals()["diff_values"]   = []
        globals()["r_corners"] = []
        globals()["b_corners"] = []
        globals()["p_corners"] = []
        globals()["index_r_corner"] = []
        globals()["index_b_corner"] = []
        globals()["index_p_corner"] = []
        globals()["angle_r_hor"]    = []
        globals()["angle_b_hor"]    = []
        globals()["angle_p_hor"]    = []
        
        # Find rectangles  
        for points in combinations(corrected_corners_b, 4):
            if isRect(points, 0.075, h, w) == True:
                final_corners.append(points)
        for points in combinations(corrected_corners_r, 4):
            if isRect(points, 0.075, h, w) == True:
                final_corners.append(points)
        for points in combinations(corrected_corners_p, 4):
            if isRect(points, 0.070, h, w) == True:
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
        if index_r_corner != []:
            r_corners = find_best_corner("r", index_r_corner, 0)
    
        ## Find best Blue corner
        if index_b_corner != []:
            b_corners = find_best_corner("b", index_b_corner, 0)
    
        # Find best Purple corner
        if index_p_corner != []:
            p_corners = find_best_corner("p", index_p_corner, 0)
        
        print("CORNERS", r_corners, b_corners, p_corners)
        print("DIFF_VALUES", diff_values)
        print("FINAL", final_corners, "LEN", len(final_corners)) 
        # Determine corner positions
        # If red rectangle found
        if r_corners != []:
            determine_corner_positions("r", r_corners) 
        # If blue rectangle found
        if b_corners != []:
            determine_corner_positions("b", b_corners)    
    
        # If purple rectangle found
        if p_corners != []:
            determine_corner_positions("p", p_corners) 
       
        # Verify points - for testing
        #if r_corners != []:
        #    image = cv2.line(image, (round(r_up_left[0]), round(r_up_left[1])), (round(r_up_right[0]), round(r_up_right[1])), (0,255,0), 2)
        #    image = cv2.line(image, (round(r_up_left[0]), round(r_up_left[1])), (round(r_bot_left[0]), round(r_bot_left[1])), (0,255,0), 2)
        #    image = cv2.line(image, (round(r_bot_right[0]), round(r_bot_right[1])), (round(r_up_right[0]), round(r_up_right[1])), (0,255,0), 2)
        #    image = cv2.line(image, (round(r_bot_right[0]), round(r_bot_right[1])), (round(r_bot_left[0]), round(r_bot_left[1])), (0,255,0), 2)
        #if b_corners != []:
        #    image = cv2.line(image, (round(b_up_left[0]), round(b_up_left[1])), (round(b_up_right[0]), round(b_up_right[1])), (0,0,255), 2)
        #    image = cv2.line(image, (round(b_up_left[0]), round(b_up_left[1])), (round(b_bot_left[0]), round(b_bot_left[1])), (0,0,255), 2)
        #    image = cv2.line(image, (round(b_bot_right[0]), round(b_bot_right[1])), (round(b_up_right[0]), round(b_up_right[1])), (0,0,255), 2)
        #    image = cv2.line(image, (round(b_bot_right[0]), round(b_bot_right[1])), (round(b_bot_left[0]), round(b_bot_left[1])), (0,0,255), 2)
        #if p_corners != []:
        #    image = cv2.line(image, (round(p_up_left[0]), round(p_up_left[1])), (round(p_up_right[0]), round(p_up_right[1])), (0,0,255), 2)
        #    image = cv2.line(image, (round(p_up_left[0]), round(p_up_left[1])), (round(p_bot_left[0]), round(p_bot_left[1])), (0,0,255), 2)
        #    image = cv2.line(image, (round(p_bot_right[0]), round(p_bot_right[1])), (round(p_up_right[0]), round(p_up_right[1])), (0,0,255), 2)
        #    image = cv2.line(image, (round(p_bot_right[0]), round(p_bot_right[1])), (round(p_bot_left[0]), round(p_bot_left[1])), (0,0,255), 2)
        #cv2.imshow("Top_detected", image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        #continue
    ### Coord correction
        h, w = image.shape[:2]
        globals()["vert_l"] = []
        globals()["hor_l"]  = []
        globals()["r_index"] = 99
        globals()["b_index"] = 99
        globals()["p_index"] = 99 
        globals()["safe_corners_rb"] = []
        globals()["safe_corners_rp"] = []
        globals()["safe_corners_bp"] = []
        globals()["safe_corners_r"]  = [0, 0]
        globals()["safe_corners_b"]  = [0, 0]
        globals()["safe_corners_p"]  = [0, 0]
    
    #### Find reference corners based on distances
        if R == True and B == True and P == True:
            print("RBP------------------------------------------")
            determine_theoretical_lengths_and_angles(["r", "b", "p"])
    
    ### Calculate distances
            # Red Blue        
            calculate_manhattan_distances("r", "b")
    
            # Red Pink
            calculate_manhattan_distances("r", "p")
    
            # Blue Pink
            calculate_manhattan_distances("b", "p")
            
    # Determine safe corners based on distances
            # Red Blue
            determine_safe_corners("r", "b")
            
            # Red Pink
            determine_safe_corners("r", "p")
    
            # Blue Pin
            determine_safe_corners("b", "p")
    
            # Run verification
            verify_safe_corners(3)
    
    # If no safe corner found after verification try it with the second and third best rectangle (if exists).
            # Red
            if safe_corners_r == [0, 0]:
                print("REEEEEEEEEEEEEEEEEEED")
                corrigate_using_other_rectangles(main_color = "r", color_1 = "b", color_2 = "p")
            
            # Blue 
            if safe_corners_b == [0, 0]:
                print("BLUEEEEEEE")
                corrigate_using_other_rectangles(main_color = "b", color_1 = "r", color_2 = "p")
            
            # Purple 
            if safe_corners_p == [0, 0]:
                print("PURPLEEEE")
                corrigate_using_other_rectangles(main_color = "p", color_1 = "r", color_2 = "b")
    
            print("Theoretical_l + moe:", theoretical_length, "|", theoretical_length+moe/1.333,"|", theoretical_length-moe/1.333)
            print("Vert_l:", vert_l)
            print("Hor_l:", hor_l)
            print("RB_theo:",theoretical_distance_rb)
            print("RP_theo:", theoretical_distance_rp)
            print("BP_theo:", theoretical_distance_bp)
            print("RB:", rb_dist)
            print("RP:", rp_dist)
            print("BP:", bp_dist)
            print("Safe_rb:", safe_corners_rb)
            print("Safe_rp:",safe_corners_rp)
            print("safe_bp:", safe_corners_bp)
            print("safe_r:", safe_corners_r)
            print("safe_b:", safe_corners_b)
            print("safe_p:", safe_corners_p)
    
        elif R == True and B == True and P == False:
            print("RB------------------------------------------")
            determine_theoretical_lengths_and_angles(["r", "b"])
            calculate_manhattan_distances("r", "b")
            determine_safe_corners("r", "b")
            verify_safe_corners(2)
            # Red
            if safe_corners_r == [0, 0]:
                corrigate_using_other_rectangles(main_color = "r", color_1 = "b")
            
            # Blue 
            if safe_corners_b == [0, 0]:
                corrigate_using_other_rectangles(main_color = "b", color_1 = "r")
            
            print("Theoretical_l + moe:", theoretical_length, "|", theoretical_length+moe/1.333,"|", theoretical_length-moe/1.333)
            print("Vert_l:", vert_l)
            print("Hor_l:", hor_l)
            print("RB_theo:",theoretical_distance_rb)
            print("RB:", rb_dist)
            print("Safe_rb:", safe_corners_rb)
            print("safe_r:", safe_corners_r)
            print("safe_b:", safe_corners_b)
    
        elif R == True and B == False and P == True:
            print("RP------------------------------------------")
            determine_theoretical_lengths_and_angles(["r", "p"])
            calculate_manhattan_distances("r", "p")
            determine_safe_corners("r", "p")
            verify_safe_corners(2)
            # Red
            if safe_corners_r == [0, 0]:
                corrigate_using_other_rectangles(main_color = "r", color_1 = "p")
            
            # Purple
            if safe_corners_p == [0, 0]:
                corrigate_using_other_rectangles(main_color = "p", color_1 = "r")
            
        elif R == False and B == True and P == True:
            print("BP------------------------------------------")
            determine_theoretical_lengths_and_angles(["b", "p"])
            calculate_manhattan_distances("b", "p")
            determine_safe_corners("b", "p")
            print(safe_corners_bp)
            verify_safe_corners(2)
            
            # Blue
            if safe_corners_b == [0, 0]:
                corrigate_using_other_rectangles(main_color = "b", color_1 = "p")
            
            # Purple
            if safe_corners_p == [0, 0]:
                corrigate_using_other_rectangles(main_color = "p", color_1 = "b")
            
    # Only one corner found 
        elif R == True and B == False and P == False:
            print("R------------------------------------------")
            determine_theoretical_lengths_and_angles(["r"])
            verify_safe_corners(1)
            
        elif R == False and B == True and P == False:
            print("B------------------------------------------")
            determine_theoretical_lengths_and_angles(["b"])
            verify_safe_corners(1)
        
        elif R == False and B == False and P == True:
            print("B------------------------------------------")
            determine_theoretical_lengths_and_angles(["p"])
            verify_safe_corners(1)
    
    ### Transformation
        old_points = []
        new_points = []
        # Rectangle reference points
        if final_coord_r != None and safe_corners_r != [0, 0]:
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
            new_points.append([r_gap_side, r_gap_top + 0])
            new_points.append([r_gap_side + rect_l, r_gap_top + 0])
            new_points.append([r_gap_side, r_gap_top + rect_l])
            new_points.append([r_gap_side + rect_l, r_gap_top + rect_l])
        if final_coord_b != None and safe_corners_b != [0,0]:
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
            new_points.append([table_shape[0] - b_gap_side - rect_l, b_gap_top + 0])
            new_points.append([table_shape[0] - b_gap_side, b_gap_top + 0])
            new_points.append([table_shape[0] - b_gap_side - rect_l, b_gap_top + rect_l])
            new_points.append([table_shape[0] - b_gap_side, b_gap_top + rect_l])
        if final_coord_p != None and safe_corners_p != [0,0]:
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
            new_points.append([p_gap_side, p_gap_top])
            new_points.append([p_gap_side + rect_l, p_gap_top])
            new_points.append([p_gap_side, p_gap_top + rect_l])
            new_points.append([p_gap_side + rect_l, p_gap_top + rect_l])
        
    
        # Perspective transformation
        h, w = orig_image.shape[:2]
        old_points = np.array(old_points)
        new_points = np.array(new_points)
        if old_points != []:
            M, mask = cv2.findHomography(old_points.astype(np.float32), new_points.astype(np.float32))
            orig_image = cv2.warpPerspective(orig_image, M, table_shape)
        else:
            print(file + "Not enough point of reference")
    
    #    # Save results
        print(file, "DONE")
        edge_detection_full_output = os.path.join(edge_detection_output, file)
        cv2.imwrite(edge_detection_full_output, image)
        transform_full_output = os.path.join(transform_output, ("new_" + file))
        cv2.imwrite(transform_full_output, orig_image)
        #orig_image = orig_image[100:,]
        #cv2.imshow("Top_detected", orig_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        #cv2.imshow("Top_detected", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    print("Edge detection results saved to:" + edge_detection_output)
    print("Perspective transformation results saved to:" + transform_output)

#(orig_path, project_dir, board_height = 105, board_width = 35, rect_l = 5, r_gap_top = 0, r_gap_side = 2, b_gap_top = 0, b_gap_side = 2, p_gap_top = 15, p_gap_side = 15):
if __name__ == '__main__':
    detect_and_transform("/home/eram/python_venv/images/original_images/", "/home/eram/python_venv/")

