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
from flask import Flask, request, render_template, redirect, send_from_directory 

# Randomizáljuk a portokat? https://stackoverflow.com/questions/11125196/python-flask-open-a-webpage-in-default-browser
url = 'http://127.0.0.1:5000/'
# Flask constructor
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
    print(glob_p_gap_side)
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
        #work_from_coord.work_from_coord(glob_orig_path, glob_coord_path, glob_project_dir_path, glob_board_height, glob_board_width, glob_rect_l, glob_r_gap_top, glob_r_gap_side, glob_b_gap_top, glob_b_gap_side, glob_p_gap_top, glob_p_gap_side, glob_sep, glob_header, glob_colname_x, glob_colname_y, glob_colname_img)
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
        return render_template("final.html")
    
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
        print(glob_img_list)
        #media_folder = glob_orig_path + 'IMG_20230228_141926.jpg'
        #print(media_folder)
        #send_from_directory(media_folder, 'IMG_20230228_141926.jpg', as_attachment = True) 
        return redirect("/image_annotator/")
    
@app.route('/image_annotator/')
def image_annotator():
    return render_template('image_annotator.html')

@app.route('/image_annotator/', methods = ["POST"])
# Ezt befejezni!
def submit_image_annotator():
    return redirect('/')

#       if calibrate_coords != None:
#           if calibrate_coords != "":
#               return render_template("check.html")
#           else:
#                print("PLEASE SUPPLY PARAMS")
#    return render_template("index.html")


threading.Timer(1.25, lambda: webbrowser.open(url)).start()
if __name__=='__main__':
# In background
#   threading.Thread(target = app.run).start() 
    app.run()


