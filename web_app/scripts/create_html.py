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

# Flask constructor
#app = Flask(__name__, static_folder = '/home/eram/python_venv/images/')
#try:
#    glob_orig_path
#except NameError:
#    var_exists = False
#else:
#    var_exists = True
#
#if var_exists == True:
#    app = Flask(__name__, static_folder = glob_orig_path)
#else:
#    app = Flask(__name__)

app = Flask(__name__)

# A decorator used to tell the application
# which URL is associated function
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

@app.route('/', methods =["POST"])
def submit_home():
    coord = request.form.get("Coord")
    if coord == "Detect":
         return redirect("detect/")
    elif coord == "Load":
         return redirect("load/")

@app.route('/load/')
def load():
    return render_template('load.html')

@app.route('/load/', methods = ["POST"])
def submit_load():
    load = request.form.get("Load") 
    if load == "CSV":
         return redirect("/csv/")
    elif load == "Annotate":
         return redirect("/annotate/")
    
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
        for f in glob_img_list:
            global_config_data.append(0)
            global_seq_id_data.append(0)
        if save_images == "on":
# CSVsből bemásolni a jó megoldást
            print("ON")
        else:
            print("OFF")
        return redirect(url_for("calibrate"))
    
@app.route('/calibrate')
def calibrate():
    directory = app.config["IMAGES"]
    globals()["image"] = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    #not_end   = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    #not_first = not(app.config["HEAD"] == 0)
    return render_template('calibrate.html', directory=directory, image=image, head = 0, labels=labels, len=len(app.config["FILES"]))

@app.route('/add_calibrate/<id>')
def add_calibrate(id):
    print("SEQ", id_seq)
    print("EARLY_ID", id)
    if len(app.config["LABELS"]) != 0:
        if int(id) not in id_seq:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            zoom_pos_x = request.args.get("zoom_pos_x")
            zoom_pos_y = request.args.get("zoom_pos_y")
            zoom_scale = request.args.get("zoom_scale")
            name = image
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            id_seq.append(int(id))
            print("LABELS", app.config["LABELS"])
        else:
            # More than one coord for an ID -- > Object dragged, update coord values
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            zoom_pos_x = request.args.get("zoom_pos_x")
            zoom_pos_y = request.args.get("zoom_pos_y")
            zoom_scale = request.args.get("zoom_scale")
            app.config["LABELS"][int(id)-1]["x_coord"] = x_coord
            app.config["LABELS"][int(id)-1]["y_coord"] = y_coord
            app.config["LABELS"][int(id)-1]["zoom_pos_x"] = zoom_pos_x
            app.config["LABELS"][int(id)-1]["zoom_pos_y"] = zoom_pos_y
            app.config["LABELS"][int(id)-1]["zoom_scale"] = zoom_scale
    else:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            zoom_pos_x = request.args.get("zoom_pos_x")
            zoom_pos_y = request.args.get("zoom_pos_y")
            zoom_scale = request.args.get("zoom_scale")
            name = image
            print("FIRST", x_coord, y_coord)
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
            print("LABELS", app.config["LABELS"])
    return redirect(url_for('calibrate'))

@app.route('/remove_calibrate/<id>')
def remove_calibrate(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    del id_seq[index]
    for n, i in enumerate(id_seq[index:]):
        id_seq[index + n] = id_seq[index + n] - 1
    return redirect(url_for('calibrate'))


@app.route('/calibrate/', methods = ["POST"])
def submit_calibrate():
    for label in app.config["LABELS"]:
        annotated_points.append([label["name"],float(label["x_coord"]), float(label["y_coord"])])
    annotated_points_dataframe = pd.DataFrame(annotated_points, columns = ['name','x_coord', 'y_coord'])
    image_name = annotated_points_dataframe['name'][0]
    error_images = []
    old_points   = [] 
    work_from_coord.transform_by_coord(file_path = "", sep = 0, header = 0, x = "x_coord", y = "y_coord", label = "name", image_name = image_name, old_points = old_points, data_type = "data_frame", data_frame = annotated_points_dataframe, error_images = error_images)
    average_side_length = detect_and_transform.calc_average_side_length(old_points)
    #object_detection_errors = box_detect_and_cut.detect_and_cut(glob_orig_path, glob_project_dir_path)
    object_detection_errors = []
    transformation_errors, transformation_warnings, transformation_config = detect_and_transform.detect_and_transform(glob_orig_path, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, average_side_length)
    globals()["transformation_config"] = transformation_config 
    #transformation_errors = []
    #transformation_warnings = []
    #analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
    analysis_errors = []
    if glob_save_images == "on":
        pass
    else:
        transformation_dir = glob_project_dir_path + "images/transformed_images"
        for f in os.listdir(transformation_dir):
            os.remove(os.path.join(transformation_dir, f))
        results_dir = glob_project_dir_path + "images/result_images"
        for f in os.listdir(results_dir):
            os.remove(os.path.join(results_dir, f))
    # to open/create a new html file in the write mode
    f = open('templates/final.html', 'w')
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
    f = open(glob_project_dir_path + "results/report.txt", 'w')
    f.write("Results of object detection: \n")
    if len(object_detection_errors) != 0:
        for img in object_detection_errors:
            line_text = "Detection error: No whiteboard detected on image: {}. \n".format(img)
            f.write(line_text)
    else:
        line_text = "Success: Detected the whiteboard on all images. \n"
        f.write(line_text)
    
    
    f.write("\n Results of reference rectangle detection: \n")
    if len(transformation_errors) != 0:
        for img in transformation_errors:
            line_text = "Count error: No reference rectangle found on image: {}. \n".format(img)
            f.write(line_text)
    else:
        line_text = "Success: Found at least 1 reference rectangle on all images. \n"
        f.write(line_text)
    
    f.write("\n Results of keypoint detection: \n")
    if len(transformation_warnings) != 0:
        for img, color in transformation_warnings:
            line_text = "Count warning: On image: {} the {} reference rectangle was not found. Using the other two for transformation, if possible. \n".format(img, color)
            f.write(line_text)
    else:
        line_text = "Success: The detected number of keypoints on all images are the same as expected (12). \n"
        f.write(line_text)

    f.write("\n Results of pixel analysis: \n")
    if len(analysis_errors) != 0:
        for img, param in analysis_errors:
            print(img, param)
            line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
            f.write(line_text)
    else:
        line_text = "Success: The calculated structural parameters are valid numbers."
        f.write(line_text)
    f.close()

    return redirect(url_for('final'))

@app.route('/check_results')
def check_results():
    directory = app.config["IMAGES"]
    app.config["FILES"] = glob_img_list
    print("DIRECTORY", directory)
    print("FILES", app.config["FILES"])
    print("HEAD", app.config["HEAD"])
    globals()["image"] = app.config["FILES"][app.config["HEAD"]]
    print("IMAGE", image)
    #globals()["id_seq"] = []
    globals()["label_count"] = 0
    #app.config["LABELS"] = []
    if len(globals()["transformation_config"]) != 0 and app.config["LABELS"] == []:
        for i in globals()["transformation_config"]:
            if i["name"] == image:
                app.config["LABELS"].append(i)
                globals()["label_count"] = label_count + 1
                globals()["id_seq"].append(label_count)
    labels = app.config["LABELS"]
    print("LABELS", labels)
    not_end   = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    not_first = not(app.config["HEAD"] == 0)
    return render_template('check.html', not_first=not_first, not_end=not_end, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

@app.route('/next_results')
def next_results():
    image = app.config["FILES"][app.config["HEAD"]]
    print("TEST+++++++++++", global_config_data)
    global_config_data[app.config["HEAD"]] = app.config["LABELS"]
    global_seq_id_data[app.config["HEAD"]] = id_seq
    app.config["HEAD"] = app.config["HEAD"] + 1
    globals()["label_count"] = 0
    for label in app.config["LABELS"]:
        globals()["annotated_points"].append([label["name"],round(float(label["x_coord"])), round(float(label["y_coord"]))])
        globals()["label_count"] = globals()["label_count"] + 1
    if global_config_data[app.config["HEAD"]] == 0:
        app.config["LABELS"] = []
        globals()["id_seq"] = []
    else:
        globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
        app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('check_results'))


@app.route('/prev_results')
def prev_results():
    image = app.config["FILES"][app.config["HEAD"]]
    app.config["HEAD"] = app.config["HEAD"] - 1
    # Visszaszűrni
    globals()["annotated_points"] = globals()["annotated_points"][:len(globals()["annotated_points"]) - globals()["label_count"]]
    print("ANN POINTS", len(annotated_points), globals()["label_count"],"PTS", annotated_points)
    globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
    app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('check_results'))

@app.route('/add_results/<id>')
def add_results(id):
    print("SEQ", id_seq)
    print("EARLY_ID", id)
    print("ADD/LABELS", app.config["LABELS"])
    if len(app.config["LABELS"]) != 0:
        if int(id) not in id_seq:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            zoom_pos_x = request.args.get("zoom_pos_x")
            zoom_pos_y = request.args.get("zoom_pos_y")
            zoom_scale = request.args.get("zoom_scale")
            name = image
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            id_seq.append(int(id))
            print("LABELS", app.config["LABELS"])
        else:
            # More than one coord for an ID -- > Object dragged, update coord values
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            zoom_pos_x = request.args.get("zoom_pos_x")
            zoom_pos_y = request.args.get("zoom_pos_y")
            zoom_scale = request.args.get("zoom_scale")
            app.config["LABELS"][int(id)-1]["x_coord"] = x_coord
            app.config["LABELS"][int(id)-1]["y_coord"] = y_coord
            app.config["LABELS"][int(id)-1]["zoom_pos_x"] = zoom_pos_x
            app.config["LABELS"][int(id)-1]["zoom_pos_y"] = zoom_pos_y
            app.config["LABELS"][int(id)-1]["zoom_scale"] = zoom_scale
    else:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            zoom_pos_x = request.args.get("zoom_pos_x")
            zoom_pos_y = request.args.get("zoom_pos_y")
            zoom_scale = request.args.get("zoom_scale")
            name = image
            print("FIRST", x_coord, y_coord)
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
            print("LABELS", app.config["LABELS"])
    return redirect(url_for('check_results'))

@app.route('/remove_results/<id>')
def remove_results(id):
    index = int(id) - 1
    print("SEQ", id_seq)
    print("EARLY_ID", id)
    print("INDEX", index)
    print("REMOVE/LABELS", app.config["LABELS"])
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    del id_seq[index]
    for n, i in enumerate(id_seq[index:]):
        id_seq[index + n] = id_seq[index + n] - 1
    return redirect(url_for('check_results'))

@app.route('/check_results/', methods = ["POST"])
def submit_check_results():
    for label in app.config["LABELS"]:
        annotated_points.append([label["name"],float(label["x_coord"]), float(label["y_coord"])])
    annotated_points_dataframe = pd.DataFrame(annotated_points, columns = ['name','x_coord', 'y_coord'])
    transformation_errors = work_from_coord.work_from_coord(glob_orig_path, 0, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, 0, 0, "x_coord", "y_coord", "name", "data_frame", annotated_points_dataframe)
    #transformation_errors = []
    print("ERRORS", transformation_errors)
    analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
    print("ANAL_ERRORS", analysis_errors)
    globals()["analyze"] = True
    if glob_save_images == "on":
        pass
    else:
        transformation_dir = glob_project_dir_path + "images/transformed_images"
        for f in os.listdir(transformation_dir):
            os.remove(os.path.join(transformation_dir, f))
        results_dir = glob_project_dir_path + "images/result_images"
        for f in os.listdir(results_dir):
            os.remove(os.path.join(results_dir, f))
    # to open/create a new html file in the write mode
    f = open('templates/final.html', 'w')
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
    f = open(glob_project_dir_path + "results/report_rerun.txt", 'w')
    f.write("Results of keypoint detection: \n")
    if len(transformation_errors) != 0:
        for img, count in transformation_errors:
            print(img, count)
            line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
            f.write(line_text)
    else:
        line_text = "Success: The provided number of keypoints on all images are the same as expected (12). \n"
        f.write(line_text)
    f.write("\n Results of pixel analysis: \n")
    if len(analysis_errors) != 0:
        for img, param in analysis_errors:
            print(img, param)
            line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
            f.write(line_text)
    else:
        line_text = "Success: The calculated structural parameters are valid numbers."
        f.write(line_text)
    f.close()
    return redirect(url_for('final'))

@app.route('/csv/')
def csv():
    return render_template('csv.html')

@app.route('/csv/', methods = ["POST"])
def submit_csv():
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
        transformation_errors = work_from_coord.work_from_coord(glob_orig_path, glob_coord_path, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, glob_sep, glob_header, glob_colname_x, glob_colname_y, glob_colname_img)
        #globals()["transform"] = True
        analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
        #globals()["analyze"] = True
        if save_images == "on":
            pass
        else:
            transformation_dir = glob_project_dir_path + "images/transformed_images"
            for f in os.listdir(transformation_dir):
                os.remove(os.path.join(transformation_dir, f))
            results_dir = glob_project_dir_path + "images/result_images"
            for f in os.listdir(results_dir):
                os.remove(os.path.join(results_dir, f))

        # to open/create a new html file in the write mode
        f = open('templates/final.html', 'w')
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
        f = open(glob_project_dir_path + "results/report.txt", 'w')
        f.write("Results of keypoint detection: \n")
        if len(transformation_errors) != 0:
            for img, count in transformation_errors:
                print(img, count)
                line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
                f.write(line_text)
        else:
            line_text = "Success: The provided number of keypoints on all images are the same as expected (12). \n"
            f.write(line_text)
        f.write("\n Results of pixel analysis: \n")
        if len(analysis_errors) != 0:
            for img, param in analysis_errors:
                print(img, param)
                line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
                f.write(line_text)
        else:
            line_text = "Success: The calculated structural parameters are valid numbers."
            f.write(line_text)
        f.close()

    return redirect(url_for('final'))

@app.route('/annotate/')
def annotate():
    return render_template('annotate.html')

@app.route('/annotate/', methods = ["POST"])
def submit_annotate():
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
        print(glob_img_list)
        app.config["FILES"] = glob_img_list
        for f in glob_img_list:
            global_config_data.append(0)
            global_seq_id_data.append(0)
        return redirect(url_for("tagger"))

@app.route('/tagger')
def tagger():
    #if (app.config["HEAD"] == len(app.config["FILES"])):
    #    return redirect(url_for('final'))
    directory = app.config["IMAGES"]
    globals()["image"] = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    not_end   = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    not_first = not(app.config["HEAD"] == 0)
    print(not_first)
    return render_template('tagger.html', not_first=not_first, not_end=not_end, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

@app.route('/next')
def next():
    image = app.config["FILES"][app.config["HEAD"]]
    global_config_data[app.config["HEAD"]] = app.config["LABELS"]
    global_seq_id_data[app.config["HEAD"]] = id_seq
    app.config["HEAD"] = app.config["HEAD"] + 1
    globals()["label_count"] = 0
    for label in app.config["LABELS"]:
        #annotated_points.append([label["id"],label["name"],round(float(label["x_coord"])), round(float(label["y_coord"]))])
        globals()["annotated_points"].append([label["name"],round(float(label["x_coord"])), round(float(label["y_coord"]))])
        globals()["label_count"] = globals()["label_count"] + 1
    if global_config_data[app.config["HEAD"]] == 0:
        app.config["LABELS"] = []
        globals()["id_seq"] = []
    else:
        globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
        app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('tagger'))

@app.route('/prev')
def prev():
    image = app.config["FILES"][app.config["HEAD"]]
    app.config["HEAD"] = app.config["HEAD"] - 1
    # Visszaszűrni
    globals()["annotated_points"] = globals()["annotated_points"][:len(globals()["annotated_points"]) - globals()["label_count"]]
    print("ANN POINTS", len(annotated_points), globals()["label_count"],"PTS", annotated_points)
    globals()["id_seq"] = global_seq_id_data[app.config["HEAD"]] 
    app.config["LABELS"] = global_config_data[app.config["HEAD"]]
    return redirect(url_for('tagger'))

@app.route('/add/<id>', methods=['GET', 'POST'])
def add(id):
    print("SEQ", id_seq)
    print("EARLY_ID", id)
    if len(app.config["LABELS"]) != 0:
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
            print("LABELS", app.config["LABELS"])
        else:
            # More than one coord for an ID -- > Object dragged, update coord values
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
    else:
            x_coord = request.args.get("x_coord")
            y_coord = request.args.get("y_coord")
            #zoom_pos_x = request.args.get("zoom_pos_x")
            #zoom_pos_y = request.args.get("zoom_pos_y")
            #zoom_scale = request.args.get("zoom_scale")
            name = image
            print("FIRST", x_coord, y_coord)
            #app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord, "zoom_pos_x": zoom_pos_x,"zoom_pos_y":  zoom_pos_y, "zoom_scale": zoom_scale})
            app.config["LABELS"].append({"id":id, "name":name, "x_coord":x_coord, "y_coord":y_coord})
            id_seq.append(int(id))
            print("LABELS", app.config["LABELS"])
    #return redirect(url_for('tagger'))
    return ('', 204)

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

@app.route('/image/<f>')
def get_image_2(f):
    return send_from_directory(glob_orig_path, f)

@app.route('/tagger/', methods = ["POST"])
def submit_annotation():
    for label in app.config["LABELS"]:
        annotated_points.append([label["name"],float(label["x_coord"]), float(label["y_coord"])])
    annotated_points_dataframe = pd.DataFrame(annotated_points, columns = ['name','x_coord', 'y_coord'])
    #transformation_errors = work_from_coord.work_from_coord(glob_orig_path, 0, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, 0, 0, "x_coord", "y_coord", "name", "data_frame", annotated_points_dataframe)
    transformation_errors = []
    print("ERRORS", transformation_errors)
    globals()["transform"] = True
    analysis_errors = veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
    print("ANAL_ERRORS", analysis_errors)
    globals()["analyze"] = True
    if glob_save_images == "on":
        pass
    else:
        transformation_dir = glob_project_dir_path + "images/transformed_images"
        for f in os.listdir(transformation_dir):
            os.remove(os.path.join(transformation_dir, f))
        results_dir = glob_project_dir_path + "images/result_images"
        for f in os.listdir(results_dir):
            os.remove(os.path.join(results_dir, f))
    # to open/create a new html file in the write mode
    f = open('templates/final.html', 'w')
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
    f = open(glob_project_dir_path + "results/report.txt", 'w')
    f.write("Results of keypoint detection: \n")
    if len(transformation_errors) != 0:
        for img, count in transformation_errors:
            print(img, count)
            line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
            f.write(line_text)
    else:
        line_text = "Success: The provided number of keypoints on all images are the same as expected (12). \n"
        f.write(line_text)
    f.write("\n Results of pixel analysis: \n")
    if len(analysis_errors) != 0:
        for img, param in analysis_errors:
            print(img, param)
            line_text = "Value error: The calculated value of {} on image: {} is Nan. \n".format(param, img)
            f.write(line_text)
    else:
        line_text = "Success: The calculated structural parameters are valid numbers."
        f.write(line_text)
    f.close()
    return redirect(url_for('final'))

@app.route('/final')
def final():
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    globals()["annotated_points"] = []
    globals()["id_seq"] = []
    return render_template("final.html")


threading.Timer(1, lambda: webbrowser.open(url)).start()
if __name__=='__main__':
# In background
#   threading.Thread(target = app.run).start() 
    app.config["IMAGES"] = 'images'
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.run()


