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
from flask import Flask, request, render_template, redirect, send_from_directory, url_for


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
        globals()["glob_project_dir_path"] = project_dir_path
        globals()["glob_board_height"]     = board_height
        globals()["glob_board_width"]      = board_width
        globals()["glob_rect_l"] = rect_l
        globals()["glob_r_gap_top"]  = r_gap_top
        globals()["glob_r_gap_side"] = r_gap_side  
        globals()["glob_b_gap_top"]  = b_gap_top
        globals()["glob_b_gap_side"] = b_gap_side
        globals()["glob_p_gap_top"]  = p_gap_top
        globals()["glob_p_gap_side"] = p_gap_side
        #box_detect_and_cut.detect_and_cut(glob_orig_path, glob_project_dir_path)
        globals()["box"] = True
        #detect_and_transform.detect_and_transform(glob_orig_path, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side)
        globals()["transform"] = True
        #veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
        globals()["analyze"] = True
        if save_images == "on":
# CSVsből bemásolni a jó megoldást
            print("ON")
        else:
            print("OFF")
        return redirect("/calibrate/")
    
@app.route('/calibrate/')
def calibrate():
    return render_template('calibrate.html')

@app.route('/calibrate/', methods = ["POST"])
def submit_calibrate():
# Ezt ellenőrizni
    #calibrate_coords = request.form.get("Calibrate")
    return redirect('/')

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
        globals()["glob_orig_path"]  = orig_path
        globals()["glob_coord_path"] = coord_path
        globals()["glob_project_dir_path"] = project_dir_path
        globals()["glob_board_height"]  = board_height
        globals()["glob_board_width"]      = board_width
        globals()["glob_rect_l"] = rect_l
        globals()["glob_r_gap_top"]  = r_gap_top
        globals()["glob_r_gap_side"] = r_gap_side  
        globals()["glob_b_gap_top"]  = b_gap_top
        globals()["glob_b_gap_side"] = b_gap_side
        globals()["glob_p_gap_top"]  = p_gap_top
        globals()["glob_p_gap_side"] = p_gap_side
        globals()["glob_sep"] = sep
        globals()["glob_header"] = header
        globals()["glob_colname_x"]  = colname_x
        globals()["glob_colname_y"]  = colname_y
        globals()["glob_colname_img"]  = colname_img
        transformation_errors = work_from_coord.work_from_coord(glob_orig_path, glob_coord_path, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, glob_sep, glob_header, glob_colname_x, glob_colname_y, glob_colname_img)
        print("ASSSSSSD", transformation_errors)
        globals()["transform"] = True
        #veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
        globals()["analyze"] = True
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
        if len(transformation_errors) != 0:
            for img, count in transformation_errors:
                print(img, count)
                line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
                f.write(line_text)
        else:
            line_text = "Transformation success: The provided number of keypoints on all images are the same as expected (12)."
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
    if (app.config["HEAD"] == len(app.config["FILES"])):
        return redirect(url_for('final'))
    directory = app.config["IMAGES"]
    globals()["image"] = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    not_end   = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    not_first = not(app.config["HEAD"] == 0)
    print(not_first)
    return render_template('tagger.html',not_first=not_first, not_end=not_end, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

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

@app.route('/add/<id>')
def add(id):
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
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    del id_seq[index]
    for n, i in enumerate(id_seq[index:]):
        id_seq[index + n] = id_seq[index + n] - 1
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def get_image_2(f):
    return send_from_directory(glob_orig_path, f)

@app.route('/tagger/', methods = ["POST"])
def submit_annotation():
    for label in app.config["LABELS"]:
        annotated_points.append([label["name"],float(label["x_coord"]), float(label["y_coord"])])
    annotated_points_dataframe = pd.DataFrame(annotated_points, columns = ['name','x_coord', 'y_coord'])
    transformation_errors = work_from_coord.work_from_coord(glob_orig_path, 0, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, 0, 0, "x_coord", "y_coord", "name", "data_frame", annotated_points_dataframe)
    print("ERRORS", transformation_errors)
    globals()["transform"] = True
    veg_analyzer.pixel_analyze(glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l)
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
    if len(transformation_errors) != 0:
        for img, count in transformation_errors:
            print(img, count)
            line_text = "Count error: The provided number of keypoints on image: {} is {} (expected 12). \n".format(img, str(count))
            f.write(line_text)
    else:
        line_text = "Transformation success: The provided number of keypoints on all images are the same as expected (12)."
        f.write(line_text)
    f.close()

    return redirect(url_for('final'))

@app.route('/final')
def final():
    app.config["IMAGES"] = 'images'
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.config["FILES"] = []
    globals()["annotated_points"] = []
    #annotated_points_dataframe = []
    globals()["id_seq"] = []
    globals()["global_config_data"] = [] 
    globals()["global_seq_id_data"] = []
    return render_template("final.html")


threading.Timer(1, lambda: webbrowser.open(url)).start()
if __name__=='__main__':
# In background
#   threading.Thread(target = app.run).start() 
    app.config["IMAGES"] = 'images'
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.run()


