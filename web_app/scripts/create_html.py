# import module
import webbrowser  
import requests
import threading
import random
import box_detect_and_cut
import detect_and_transform
import work_from_coord
import veg_analyzer
import os
import datetime
import pandas as pd
import json
from flask import Flask, request, render_template, redirect, send_from_directory, url_for

# Define global variables
# Randomizáljuk a portokat? https://stackoverflow.com/questions/11125196/python-flask-open-a-webpage-in-default-browser
url = 'http://127.0.0.1:5000/'
globals()["annotated_points"] = []
globals()["id_seq"] = []
globals()["global_config_data"] = [] 
globals()["global_seq_id_data"] = []

app = Flask(__name__)

# Method picker, allows the user to choose either work from coord or use automated detection+transformation.
@app.route('/')
def home():
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.config["FILES"] = []
    globals()["annotated_points"] = []
    globals()["id_seq"] = []
    globals()["global_config_data"] = [] 
    globals()["global_seq_id_data"] = []
    return render_template('index.html')

# Submit the choice of the user and redirect to the sufficent page.
@app.route('/', methods =["POST"])
def submit_home():
    coord = request.form.get("Coord")
    if coord == "Detect":
         return redirect("detect/")
    elif coord == "Load":
         return redirect("load/")

# Method picker inside "work from coord". Allows the user to pick between supplying coords as CSV-file and annotating them on site.
@app.route('/load/')
def load():
    return render_template('load.html')

# Submit the choice of the user and redirect to the sufficent page.
@app.route('/load/', methods = ["POST"])
def submit_load():
    load = request.form.get("Load") 
    if load == "CSV":
         return redirect("/csv/")
    elif load == "Annotate":
         return redirect("/annotate/")

### Automated transformation
# Parameter supply page for automated detection method
@app.route('/detect/')
def detect():
    return render_template('detect.html')

@app.route('/detect/', methods = ["POST"])
def submit_detect():
    orig_path = request.form.get("Orig_path") 
    project_dir_path = request.form.get("Project_dir_path") 
    board_height = request.form.get("Board_height")
    board_width = request.form.get("Board_width")
    rect_l = request.form.get("Rect_l")
    r_gap_top = request.form.get("r_gap_top")
    r_gap_side = request.form.get("r_gap_side")
    b_gap_top = request.form.get("b_gap_top")
    b_gap_side = request.form.get("b_gap_side")
    p_gap_top = request.form.get("p_gap_top")
    p_gap_side = request.form.get("p_gap_side")
    save_images = request.form.get("Save_images")
    if orig_path != None and project_dir_path != None and board_height != None and board_width != None and rect_l != None and r_gap_top != None and r_gap_side != None and r_gap_top != None and b_gap_side != None and r_gap_side != None and p_gap_side != None:
        print("MODE: DETECTION")
        globals()["glob_orig_path"]        = orig_path
        globals()["glob_img_list"]         = os.listdir(orig_path)
        globals()["glob_project_dir_path"] = project_dir_path
        globals()["glob_board_height"]     = board_height
        globals()["glob_board_width"]      = board_width
        globals()["glob_rect_l"]           = rect_l
        globals()["glob_r_gap_top"]        = r_gap_top
        globals()["glob_r_gap_side"]       = r_gap_side  
        globals()["glob_b_gap_top"]        = b_gap_top
        globals()["glob_b_gap_side"]       = b_gap_side
        globals()["glob_p_gap_top"]        = p_gap_top
        globals()["glob_p_gap_side"]       = p_gap_side
        globals()["glob_save_images"]      = save_images
        app.config["FILES"] = glob_img_list
        
        # Create neccessary directories in project_dir
        if not os.path.exists(project_dir_path + "/images"):
            os.mkdir(project_dir_path + "/images")
        if not os.path.exists(project_dir_path + "/images/box_images"):
            os.mkdir(project_dir_path + "/images/box_images")
        if not os.path.exists(project_dir_path + "/images/cropped_images"):
            os.mkdir(project_dir_path + "/images/cropped_images")
        if not os.path.exists(project_dir_path + "/images/edge_detected_images"):
            os.mkdir(project_dir_path + "/images/edge_detected_images")
        if not os.path.exists(project_dir_path + "/images/transformed_images"):
            os.mkdir(project_dir_path + "/images/transformed_images")
        if not os.path.exists(project_dir_path + "/images/result_images"):
            os.mkdir(project_dir_path + "/images/result_images")
        if not os.path.exists(project_dir_path + "/results"):
            os.mkdir(project_dir_path + "/results")

        # For each picture in image directory place 0 as placeholder to config-data lists.
        for f in glob_img_list:
            global_config_data.append(0)
            global_seq_id_data.append(0)
        return redirect(url_for("calibrate"))

# Calibration page for automated detection method
@app.route('/calibrate')
def calibrate():
    directory = app.config["IMAGES"]
    globals()["image"] = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    return render_template('calibrate.html', directory=directory, image=image, head = 0, labels=labels, len=len(app.config["FILES"]))

# On image-click event, add mouse position, image name and point (label) id to config data.
@app.route('/add_calibrate/<id>', methods=['GET'])
def add_calibrate(id):
    
    # If there are points in config data, check their id.
    if len(app.config["LABELS"]) != 0:
        
        # If the id of the point hasn't been declared before, apply the params to config data.
        if int(id) not in id_seq:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            name = image
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
        else:
            
            # More than one coord for a single ID -- > Point been dragged, update coord values.
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            app.config["LABELS"][int(id)-1]["x_coord"] = x_coord
            app.config["LABELS"][int(id)-1]["y_coord"] = y_coord
            #app.config["LABELS"][int(id)-1]["zoom_pos_x"] = zoom_pos_x
            #app.config["LABELS"][int(id)-1]["zoom_pos_y"] = zoom_pos_y
            #app.config["LABELS"][int(id)-1]["zoom_scale"] = zoom_scale
    
    # If there is no point recorded in config data, append the parameters of the first points.
    else:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            name = image
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
    #return redirect(url_for('calibrate'))
    return ('', 204)

# On ctrl + image-click event (or clicking the '-' button'), remove point having target id.
@app.route('/remove_calibrate/<id>')
def remove_calibrate(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    del id_seq[index]
    for n, i in enumerate(id_seq[index:]):
        id_seq[index + n] = id_seq[index + n] - 1
    #return redirect(url_for('calibrate'))
    return redirect('', 204)

# Submit data on calibration page.
@app.route('/calibrate/', methods = ["POST"])
def submit_calibrate():
    
    # Define variables
    for label in app.config["LABELS"]:
        annotated_points.append([label["name"],float(label["x_coord"]), float(label["y_coord"])])

    # If all keypoints are annotated
    if len(annotated_points) == 12:
        annotated_points_dataframe = pd.DataFrame(annotated_points, columns = ['name','x_coord', 'y_coord'])
        image_name = annotated_points_dataframe['name'][0]
        error_images = []
        old_points   = [] 
        
        # Organize calibration points
        work_from_coord.transform_by_coord(file_path = "", sep = 0, header = 0, x = "x_coord", y = "y_coord", label = "name", image_name = image_name, old_points = old_points, data_type = "data_frame", data_frame = annotated_points_dataframe, error_images = error_images)
        
        # Calculate average side length based on calibration data
        average_side_length = detect_and_transform.calc_average_side_length(old_points)
        
        # Object detection
        object_detection_errors = box_detect_and_cut.detect_and_cut(glob_orig_path, glob_project_dir_path)
        #object_detection_errors = []
        
        # Keypoint detection and transformation
        transformation_errors, transformation_warnings, transformation_config = detect_and_transform.detect_and_transform(glob_orig_path, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, average_side_length)
        globals()["transformation_config"] = transformation_config 
        #transformation_errors = []
        #transformation_warnings = []
        
        # Pixel analysis
        analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
        #analysis_errors = []
        
        # If save images is on, keep images
        if glob_save_images == "on":
            pass
        # Else delete them
        else:
            transformation_dir = glob_project_dir_path + "images/transformed_images"
            for f in os.listdir(transformation_dir):
                os.remove(os.path.join(transformation_dir, f))
            results_dir = glob_project_dir_path + "images/result_images"
            for f in os.listdir(results_dir):
                os.remove(os.path.join(results_dir, f))
            box_dir = glob_project_dir_path + "images/box_images"
            for f in os.listdir(box_dir):
                os.remove(os.path.join(box_dir, f))
            cropped_dir = glob_project_dir_path + "images/cropped_images"
            for f in os.listdir(cropped_dir):
                os.remove(os.path.join(cropped_dir, f))
            edge_detected_dir = glob_project_dir_path + "images/edge_detected_images"
            for f in os.listdir(edge_detected_dir):
                os.remove(os.path.join(edge_detected_dir, f))
        
        # create a HTML page which instructs about the location of the results
        f = open(os.path.join('templates', 'final_2.html'), 'w')
        html_template = """
         <html>
        <body>
        <div class="wrapper"> 
            <h2>Success the results are in {}</h2>
            <a href="/" type="button">
            Home
            </a>
            <a href="/check_results"class="btn btn-primary" type="button">
            Check results!
            </a>
        </div>
        </html>
        </body>
        </html>
        """.format(glob_project_dir_path + "results/")
        
        # writing the code into the file
        f.write(html_template)
        
        # close the file
        f.close()
   
        # Create report of object detection, transformation and analysis results.
        f = open(os.path.join(glob_project_dir_path, "results", "report.txt"), 'w')
        
        # Report message of object detection
        f.write("Results of object detection: \n")
        if len(object_detection_errors) != 0:
            for img in object_detection_errors:
                line_text = "Detection error: No whiteboard detected on image: {}. \n".format(img)
                f.write(line_text)
        else:
            line_text = "Success: Detected the whiteboard on all images. \n"
            f.write(line_text)
        
        # Report message of reference rectangle detection
        f.write("\n Results of reference rectangle detection: \n")
        if len(transformation_errors) != 0:
            for img in transformation_errors:
                line_text = "Count error: No reference rectangle found on image: {}. \n".format(img)
                f.write(line_text)
        else:
            line_text = "Success: Found at least 1 reference rectangle on all images. \n"
            f.write(line_text)
        
        # Report message of keypoint detection
        f.write("\n Results of keypoint detection: \n")
        if len(transformation_warnings) != 0:
            for img, color in transformation_warnings:
                line_text = "Count warning: On image: {} the {} reference rectangle was not found. Using the other two for transformation, if possible. \n".format(img, color)
                f.write(line_text)
        else:
            line_text = "Success: The detected number of keypoints on all images are the same as expected (12). \n"
            f.write(line_text)

        # Report message of pixel analysis
        f.write("\n Results of pixel analysis: \n")
        if len(analysis_errors) != 0:
            for img, param in analysis_errors:
                line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
                f.write(line_text)
        else:
            line_text = "Success: The calculated structural parameters are valid numbers."
            f.write(line_text)
        f.close()
        return redirect(url_for('final_2'))

    # Else if the count of annotated points != 12
    else:
        globals()["annotated_points"] = []
        return ('', 204)

# Result checker page for automated detection. Here the user can modify the location of keypoints and re-run the transformation.
@app.route('/check_results')
def check_results():
    # Define variables
    directory = app.config["IMAGES"]
    app.config["FILES"] = glob_img_list
    globals()["image"] = app.config["FILES"][app.config["HEAD"]]
    globals()["label_count"] = 0

    # If there was any points detected on the image, add their params to config-data.
    if len(globals()["transformation_config"]) != 0 and app.config["LABELS"] == []:
        for i in globals()["transformation_config"]:
            if i["name"] == image:
                app.config["LABELS"].append(i)
                globals()["label_count"] = label_count + 1
                globals()["id_seq"].append(label_count)
    labels = app.config["LABELS"]

    # A variable which tells whether the last image is displayed or not.
    not_end   = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    
    # A variable which tells whether the first image is displayed or not.
    not_first = not(app.config["HEAD"] == 0)
    
    # Render the page using defined variables.
    return render_template('check.html', not_first=not_first, not_end=not_end, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

# Next button for result checker
@app.route('/next_results')
def next_results():
    
    # Define variables
    image = app.config["FILES"][app.config["HEAD"]]
    global_config_data[app.config["HEAD"]] = app.config["LABELS"]
    global_seq_id_data[app.config["HEAD"]] = id_seq

    # Increase HEAD param by 1. HEAD is the index of the image to be loaded.
    app.config["HEAD"] = app.config["HEAD"] + 1
    globals()["label_count"] = 0

    # Save drawn points on current picture to pointsdata.
    for label in app.config["LABELS"]:
        globals()["annotated_points"].append([label["name"],round(float(label["x_coord"])), round(float(label["y_coord"]))])
        globals()["label_count"] = globals()["label_count"] + 1

    # If the next image has any points recorded in the global config data load them. If not, open the plain image.
    if global_config_data[app.config["HEAD"]] == 0:
        app.config["LABELS"] = []
        globals()["id_seq"] = []
    else:
        globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
        app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('check_results'))

# Prev button for result checker
@app.route('/prev_results')
def prev_results():
    image = app.config["FILES"][app.config["HEAD"]]
    
    # Decrease HEAD param by 1.
    app.config["HEAD"] = app.config["HEAD"] - 1
    
    # Remove drawn points from points data.
    globals()["annotated_points"] = globals()["annotated_points"][:len(globals()["annotated_points"]) - globals()["label_count"]]

    # Load config data params for previous image.
    globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
    app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('check_results'))

# On image-click event, add mouse position, image name and point (label) id to config data.
@app.route('/add_results/<id>', methods=['GET'])
def add_results(id):

    # If there are points in config data, check their id.
    if len(app.config["LABELS"]) != 0:

        # If the id of the point hasn't been declared before, apply the params to config data.
        if int(id) not in id_seq:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            name = image
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
        else:
            
            # More than one coord for a single ID -- > Point been dragged, update coord values.
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            app.config["LABELS"][int(id)-1]["x_coord"] = x_coord
            app.config["LABELS"][int(id)-1]["y_coord"] = y_coord
            #app.config["LABELS"][int(id)-1]["zoom_pos_x"] = zoom_pos_x
            #app.config["LABELS"][int(id)-1]["zoom_pos_y"] = zoom_pos_y
            #app.config["LABELS"][int(id)-1]["zoom_scale"] = zoom_scale

    # If there is no point recorded in config data, append the parameters of the first points.
    else:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            name = image
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
    #return redirect(url_for('check_results'))
    return ('', 204)

# On ctrl + image-click event (or clicking the '-' button'), remove point having target id.
@app.route('/remove_results/<id>')
def remove_results(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    del id_seq[index]
    for n, i in enumerate(id_seq[index:]):
        id_seq[index + n] = id_seq[index + n] - 1
    #return redirect(url_for('check_results'))
    return ('', 204)

# Submit data on check_results page.
@app.route('/check_results/', methods = ["POST"])
def submit_check_results():
    for label in app.config["LABELS"]:
        annotated_points.append([label["name"],float(label["x_coord"]), float(label["y_coord"])])
    annotated_points_dataframe = pd.DataFrame(annotated_points, columns = ['name','x_coord', 'y_coord'])
    
    # Run transformation based on corrected coords
    transformation_errors = work_from_coord.work_from_coord(glob_orig_path, 0, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, 0, 0, "x_coord", "y_coord", "name", "data_frame", annotated_points_dataframe)
    #transformation_errors = []
    
    # Pixel analysis
    analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
    
    # If save images is on, keep images
    if glob_save_images == "on":
        pass
    # Else delete them
    else:
        transformation_dir = glob_project_dir_path + "images/transformed_images"
        for f in os.listdir(transformation_dir):
            os.remove(os.path.join(transformation_dir, f))
        results_dir = glob_project_dir_path + "images/result_images"
        for f in os.listdir(results_dir):
            os.remove(os.path.join(results_dir, f))
    
    # create a HTML page which instructs about the location of the results
    f = open(os.path.join('templates', 'final.html'), 'w')
    html_template = """
     <html>
    <body>
    <div class="wrapper"> 
        <h2>Success the re-run results are in {}</h2>
        <button onClick="window.location.href='http://127.0.0.1:5000/'">Home</button>
    </div>
    </html>
    </body>
    </html>
    """.format(glob_project_dir_path + "results/")
    
    # writing the code into the file
    f.write(html_template)
    
    # close the file
    f.close()
   
    # Create report of transformation and analysis results.
    f = open(os.path.join(glob_project_dir_path, "results", "report_rerun.txt"), 'w')
    
    # Report message of keypoint detection
    f.write("Results of keypoint detection: \n")
    if len(transformation_errors) != 0:
        for img, count in transformation_errors:
            line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
            f.write(line_text)
    else:
        line_text = "Success: The provided number of keypoints on all images are the same as expected (12). \n"
        f.write(line_text)

    # Report message of pixel analysis
    f.write("\n Results of pixel analysis: \n")
    if len(analysis_errors) != 0:
        for img, param in analysis_errors:
            line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
            f.write(line_text)
    else:
        line_text = "Success: The calculated structural parameters are valid numbers."
        f.write(line_text)
    f.close()
    return redirect(url_for('final'))

### Transformation using coords from CSV file.
# Parameter supply page for load from csv method.
@app.route('/csv/')
def csv():
    return render_template('csv.html')

@app.route('/csv/', methods = ["POST"])
def submit_csv():
    
    # Define variables based on user input.
    orig_path = request.form.get("Orig_path") 
    coord_path = request.form.get("Coord_path")
    project_dir_path = request.form.get("Project_dir_path") 
    board_height = request.form.get("Board_height")
    board_width = request.form.get("Board_width")
    rect_l = request.form.get("Rect_l")
    r_gap_top = request.form.get("r_gap_top")
    r_gap_side = request.form.get("r_gap_side")
    b_gap_top = request.form.get("b_gap_top")
    b_gap_side = request.form.get("b_gap_side")
    p_gap_top = request.form.get("p_gap_top")
    p_gap_side = request.form.get("p_gap_side")
    save_images = request.form.get("Save_images")
    sep = request.form.get("Separator")
    header = request.form.get("Header")
    colname_y = request.form.get("Colname_y")
    colname_x = request.form.get("Colname_x")
    colname_img = request.form.get("Colname_img")
    if orig_path != None and coord_path != None and project_dir_path != None and board_height != None and board_width != None and rect_l != None and r_gap_top != None and r_gap_side != None and r_gap_top != None and b_gap_side != None and r_gap_side != None and p_gap_side != None and colname_y != None and colname_y != None and colname_img != None:
        print("MODE: LOAD")
        globals()["glob_orig_path"]        = orig_path
        globals()["glob_coord_path"]       = coord_path
        globals()["glob_project_dir_path"] = project_dir_path
        globals()["glob_board_height"]     = board_height
        globals()["glob_board_width"]      = board_width
        globals()["glob_rect_l"]           = rect_l
        globals()["glob_r_gap_top"]        = r_gap_top
        globals()["glob_r_gap_side"]       = r_gap_side  
        globals()["glob_b_gap_top"]        = b_gap_top
        globals()["glob_b_gap_side"]       = b_gap_side
        globals()["glob_p_gap_top"]        = p_gap_top
        globals()["glob_p_gap_side"]       = p_gap_side
        globals()["glob_sep"]              = sep
        globals()["glob_header"]           = header
        globals()["glob_colname_x"]        = colname_x
        globals()["glob_colname_y"]        = colname_y
        globals()["glob_colname_img"]      = colname_img
        
        # Create neccessary directories in project_dir
        if not os.path.exists(project_dir_path + "/images"):
            os.mkdir(project_dir_path + "/images")
        if not os.path.exists(project_dir_path + "/images/transformed_images"):
            os.mkdir(project_dir_path + "/images/transformed_images")
        if not os.path.exists(project_dir_path + "/images/result_images"):
            os.mkdir(project_dir_path + "/images/result_images")
        if not os.path.exists(project_dir_path + "/results"):
            os.mkdir(project_dir_path + "/results")

        # Transformation based on CSV coords
        transformation_errors = work_from_coord.work_from_coord(glob_orig_path, glob_coord_path, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, glob_sep, glob_header, glob_colname_x, glob_colname_y, glob_colname_img)
        
        # Pixel analysis
        analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
        
        # If save images is on, keep images
        if save_images == "on":
            pass
        # Else delete them
        else:
            transformation_dir = glob_project_dir_path + "images/transformed_images"
            for f in os.listdir(transformation_dir):
                os.remove(os.path.join(transformation_dir, f))
            results_dir = glob_project_dir_path + "images/result_images"
            for f in os.listdir(results_dir):
                os.remove(os.path.join(results_dir, f))

        # create a HTML page which instructs about the location of the results
        f = open(os.path.join('templates', 'final.html'), 'w')
        html_template = """
         <html>
        <body>
        <div class="wrapper"> 
            <h2>Success the results are in {}</h2>
            <button onClick="window.location.href='http://127.0.0.1:5000/'">Home</button>
        </div>
        </html>
        </body>
        </html>
        """.format(glob_project_dir_path + "results/")
        
        # writing the code into the file
        f.write(html_template)
        
        # close the file
        f.close()
        
        # Create report of transformation and analysis results.
        f = open(os.path.join(glob_project_dir_path, "results", "report.txt"), 'w')

        # Report message of keypoint counting
        f.write("Results of keypoint counting: \n")
        if len(transformation_errors) != 0:
            for img, count in transformation_errors:
                line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
                f.write(line_text)
        else:
            line_text = "Success: The provided number of keypoints on all images are the same as expected (12). \n"
            f.write(line_text)

        # Report message of pixel analysis
        f.write("\n Results of pixel analysis: \n")
        if len(analysis_errors) != 0:
            for img, param in analysis_errors:
                line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
                f.write(line_text)
        else:
            line_text = "Success: The calculated structural parameters are valid numbers."
            f.write(line_text)
        f.close()
    return redirect(url_for('final'))

# Parameter supply page for annotation in site method
@app.route('/annotate/')
def annotate():
    return render_template('annotate.html')

@app.route('/annotate/', methods = ["POST"])
def submit_annotate():
    
    # Define variables based on user input.
    orig_path = request.form.get("Orig_path") 
    project_dir_path = request.form.get("Project_dir_path") 
    board_height = request.form.get("Board_height")
    board_width = request.form.get("Board_width")
    rect_l = request.form.get("Rect_l")
    r_gap_top = request.form.get("r_gap_top")
    r_gap_side = request.form.get("r_gap_side")
    b_gap_top = request.form.get("b_gap_top")
    b_gap_side = request.form.get("b_gap_side")
    p_gap_top = request.form.get("p_gap_top")
    p_gap_side = request.form.get("p_gap_side")
    save_images = request.form.get("Save_images")
    if orig_path != None and project_dir_path != None and board_height != None and board_width != None and rect_l != None and r_gap_top != None and r_gap_side != None and r_gap_top != None and b_gap_side != None and r_gap_side != None and p_gap_side != None:
        print("MODE: ANNOTATION")
        globals()["glob_orig_path"]        = orig_path
        globals()["glob_img_list"]         = os.listdir(orig_path)
        globals()["glob_project_dir_path"] = project_dir_path
        globals()["glob_board_height"]     = board_height
        globals()["glob_board_width"]      = board_width
        globals()["glob_rect_l"]           = rect_l
        globals()["glob_r_gap_top"]        = r_gap_top
        globals()["glob_r_gap_side"]       = r_gap_side  
        globals()["glob_b_gap_top"]        = b_gap_top
        globals()["glob_b_gap_side"]       = b_gap_side
        globals()["glob_p_gap_top"]        = p_gap_top
        globals()["glob_p_gap_side"]       = p_gap_side
        globals()["glob_save_images"]      = save_images
        app.config["FILES"] = glob_img_list
        
        # Create neccessary directories in project_dir
        if not os.path.exists(project_dir_path + "/images"):
            os.mkdir(project_dir_path + "/images")
        if not os.path.exists(project_dir_path + "/images/transformed_images"):
            os.mkdir(project_dir_path + "/images/transformed_images")
        if not os.path.exists(project_dir_path + "/images/result_images"):
            os.mkdir(project_dir_path + "/images/result_images")
        if not os.path.exists(project_dir_path + "/results"):
            os.mkdir(project_dir_path + "/results")
       
        # For each picture in image directory place 0 as placeholder to config-data lists.
        for f in glob_img_list:
            global_config_data.append(0)
            global_seq_id_data.append(0)
        return redirect(url_for("tagger"))

# Image annotator page. Here the user can mark the keypoints of reference rectangles.
@app.route('/tagger')
def tagger():
    # Define variables based on config data
    directory = app.config["IMAGES"]
    globals()["image"] = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]

    # A variable which tells whether the last image is displayed or not.
    not_end   = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)

    # A variable which tells whether the first image is displayed or not.
    not_first = not(app.config["HEAD"] == 0)
    
    # Render the page using defined variables.
    return render_template('tagger.html', not_first=not_first, not_end=not_end, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

# Next button for image annotator
@app.route('/next')
def next():

    # Define variables
    image = app.config["FILES"][app.config["HEAD"]]
    global_config_data[app.config["HEAD"]] = app.config["LABELS"]
    global_seq_id_data[app.config["HEAD"]] = id_seq

    # Increase HEAD param by 1. HEAD is the index of the image to be loaded.
    app.config["HEAD"] = app.config["HEAD"] + 1
    globals()["label_count"] = 0

    # Save drawn points on current picture to points data.
    for label in app.config["LABELS"]:
        #annotated_points.append([label["id"],label["name"],round(float(label["x_coord"])), round(float(label["y_coord"]))])
        globals()["annotated_points"].append([label["name"],round(float(label["x_coord"])), round(float(label["y_coord"]))])
        globals()["label_count"] = globals()["label_count"] + 1

    # If the next image has any points recorded in the global config data load them. If not, open the plain image.
    if global_config_data[app.config["HEAD"]] == 0:
        app.config["LABELS"] = []
        globals()["id_seq"] = []
    else:
        globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
        app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('tagger'))

# Prev button for image annotator
@app.route('/prev')
def prev():
    image = app.config["FILES"][app.config["HEAD"]]

    # Decrease HEAD param by 1.
    app.config["HEAD"] = app.config["HEAD"] - 1
    
    # Remove drawn points from points data.
    globals()["annotated_points"] = globals()["annotated_points"][:len(globals()["annotated_points"]) - globals()["label_count"]]

    # Load config data params for previous image.
    globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
    app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('tagger'))

# On image-click event, add mouse position, image name and point (label) id to config data.
@app.route('/add/<id>', methods=['GET'])
def add(id):

    # If there are points in config data, check their id.
    if len(app.config["LABELS"]) != 0:

        # If the id of the point hasn't been declared before, apply the params to config data.
        if int(id) not in id_seq:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            name = image
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))

        # Else: More than one coord for a single ID -- > Point been dragged, update coord values.
        else:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            app.config["LABELS"][int(id)-1]["x_coord"] = x_coord
            app.config["LABELS"][int(id)-1]["y_coord"] = y_coord
            #app.config["LABELS"][int(id)-1]["zoom_pos_x"] = zoom_pos_x
            #app.config["LABELS"][int(id)-1]["zoom_pos_y"] = zoom_pos_y
            #app.config["LABELS"][int(id)-1]["zoom_scale"] = zoom_scale

    # If there is no point recorded in config data, append the parameters of the first points.
    else:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            name = image
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
    #return redirect(url_for('tagger'))
    return ('', 204)

# On ctrl + image-click event (or clicking the '-' button'), remove point having target id.
@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    del id_seq[index]
    for n, i in enumerate(id_seq[index:]):
        id_seq[index + n] = id_seq[index + n] - 1
    #return redirect(url_for('tagger'))
    return redirect('', 204)

# Submit data on image annotator
@app.route('/tagger/', methods = ["POST"])
def submit_annotation():
    for label in app.config["LABELS"]:
        annotated_points.append([label["name"],float(label["x_coord"]), float(label["y_coord"])])
    annotated_points_dataframe = pd.DataFrame(annotated_points, columns = ['name','x_coord', 'y_coord'])
    
    # Run transformation based on annotated coords
    transformation_errors = work_from_coord.work_from_coord(glob_orig_path, 0, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, 0, 0, "x_coord", "y_coord", "name", "data_frame", annotated_points_dataframe)
    #transformation_errors = []
    
    # Pixel analysis
    analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)

    # If save images is on, keep images
    if glob_save_images == "on":
        pass
    # Else delete them
    else:
        transformation_dir = glob_project_dir_path + "images/transformed_images"
        for f in os.listdir(transformation_dir):
            os.remove(os.path.join(transformation_dir, f))
        results_dir = glob_project_dir_path + "images/result_images"
        for f in os.listdir(results_dir):
            os.remove(os.path.join(results_dir, f))

    # create a HTML page which instructs about the location of the results
    f = open(os.path.join('templates' 'final.html'), 'w')
    html_template = """
     <html>
    <body>
    <div class="wrapper"> 
        <h2>Success the results are in {}</h2>
        <button onClick="window.location.href='http://127.0.0.1:5000/'">Home</button>
    </div>
    </html>
    </body>
    </html>
    """.format(glob_project_dir_path + "results/")
    
    # writing the code into the file
    f.write(html_template)
    
    # close the file
    f.close()
   
    # Create report of transformation and analysis results.
    f = open(os.path.join(glob_project_dir_path, "results", "report.txt"), 'w')
    
    # Report message of keypoint detection
    f.write("Results of keypoint detection: \n")
    if len(transformation_errors) != 0:
        for img, count in transformation_errors:
            line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
            f.write(line_text)
    else:
        line_text = "Success: The provided number of keypoints on all images are the same as expected (12). \n"
        f.write(line_text)

    # Report message of pixel analysis
    f.write("\n Results of pixel analysis: \n")
    if len(analysis_errors) != 0:
        for img, param in analysis_errors:
            line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
            f.write(line_text)
    else:
        line_text = "Success: The calculated structural parameters are valid numbers."
        f.write(line_text)
    f.close()
    return redirect(url_for('final'))

# Load image from non-static directory
@app.route('/image/<f>')
def get_image_2(f):
    return send_from_directory(glob_orig_path, f)

# Render final pages
@app.route('/final')
def final():
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    globals()["annotated_points"] = []
    globals()["id_seq"] = []
    return render_template("final.html")

@app.route('/final_2')
def final_2():
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    globals()["annotated_points"] = []
    globals()["id_seq"] = []
    return render_template("final_2.html")

# Open a browser tab
threading.Timer(1, lambda: webbrowser.open(url)).start()

# Start application
if __name__=='__main__':
    app.config["IMAGES"] = 'images'
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.run()


