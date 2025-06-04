Description
===========

We have developed a reproducible, semi-automated, photography-based
method that provides reliable results for the structural parameters of
vegetation (leaf area - LA, height of closed vegetation - HCV, maximum
canopy height - MHC, foliage height diversity -- FHD), utilizing the
power of **digital image processing** and **machine learning** based
**object detection** tools.

Read more about the concept at: **link to paper/manuscript - DOI**

To allow users to pick their preferred way of structure analysis, and to
freely parameterize the functions with ease, we have developed a
(\[Flask\]([[https://flask.palletsprojects.com/en/2.3.x/]](https://flask.palletsprojects.com/en/2.3.x/))
based) web application.

This documentation page contains all the basic information users need to
install and use the web application, including an installation guide,
rules of thumb.

Install
=======

Linux
-----

Prerequisites:

Python\>=3.8 (tested on 3.8.11, 3.8.17), see more at:
[[https://docs.python-guide.org/starting/install3/linux/]](https://docs.python-guide.org/starting/install3/linux/)
)

Git:
[[https://git-scm.com/downloads]](https://git-scm.com/downloads)

1\. Clone the repository using:

git clone
[https://github.com/EvoZooDeb/whiteboard](https://github.com/EvoZooDeb/whiteboard)

2\. Create python virtual environment using:

python3 -m venv /path/to/your\_virtual\_environment

3\. Activate your virtual environment using (you need to activate your
virtual environment every time you are using the application):

source /path/to/your\_virtual\_environment/bin/activate

4\. Install packages found in git\_dir/web\_app/requirements\_linux.txt
using:

pip install -r /path/to/requirements.txt

5\. In git\_dir/web\_app/scripts/ launch application using (keep the
terminal running during work):

python3 app.py

Windows
-------

Prerequisites:

Python\>=3.8\* (tested on 3.10.4 we recommend this version), see more
at:
[[https://www.python.org/downloads/windows/]](https://www.python.org/downloads/windows/)\
(only if didn't install with Python: pip (tested on 22.0.4), see more
at:
[[https://phoenixnap.com/kb/install-pip-windows]](https://phoenixnap.com/kb/install-pip-windows)
)

Git:
[[https://git-scm.com/downloads]](https://git-scm.com/downloads)

1\. Clone the repository using (in git-cmd):

git clone
[https://github.com/EvoZooDeb/whiteboard](https://github.com/EvoZooDeb/whiteboard)

2\. Create python virtual environment using:

py -3 -m venv \\path\\to\\your\_virtual\_virtual\_environment

3\. Activate your virtual environment using (you need to activate your
virtual environment every time you are using the application):

\\path\\to\\your\_virtual\_environment\\Scripts\\activate

4\. Install packages found in git\_dir/web\_app/requirements.

py -3 -mpip install -r \\path\\to\\requirements.txt

5\. In **git\_dir\\web\_app\\scripts**\\ launch application using (keep
the terminal running during work):

py app.py

Workflow
--------

The essence of the proposed method can be summarized in two core steps:

1\. Perspective transformation based on keypoint coordinates: which
corrects the perspective distortion of the projection of our
three-dimensional object on the image.

2\. Pixel analysis: which classifies pixels into two categories: either
as part of the board or as vegetation. Based on pixel classes it is
possible to calculate structural variables (**see paper).**

There are two main ways to get the coordinates of keypoints, which are
the foundation of perspective transformation: first is being the manual
recording using image processing software, second is the automated
detection proposed at **paper**. This web application can handle both
cases using the following workflows:

### 1. Work with manual coordinates

![](media/image1.png){width="6.6930555555555555in"
height="4.729861111111111in"}

### 

### 

### 

### 2. Automated detection

![](media/image2.png){width="6.6930555555555555in"
height="4.729861111111111in"}

**Flowchart explanation:**

Yellow elements indicate directories, blue elements indicate files, gray
elements scripts, orange element indicates parameters gained from user
input (from web application). Green lines indicate inputs for scripts,
red lines indicate outputs, black lines indicate parental relationship.

**Directories**

-   **proj** = Project directory: The directory that contains the model,
    and will contain the result images and text files. Directory
    '/whiteboard/web\_app/' contains all necessary files (scripts,
    models) so it's and ideal project directory.

-   **inp/original** = Original image directory: The directory that
    (ONLY!) contains the original images. Images should have the same
    resolution!

-   measures = Directory that contains annotated coords.

-   box = Box image directory: Automatically generated directory, that
    contains the original images with object detection results (bounding
    box).

-   cropped = Cropped image directory: Automatically generated
    directory, that contains the cropped out bounding box images.

-   corner detect = Edge detected images directory: Automatically
    generated directory, that contains the cropped out bounding box
    images with drawn reference squares (based on corner detection).

-   transformed = Transformed images directory: Automatically generated
    directory, that contains the cropped out board images (based on
    perspective transformation).

-   results = Results images directory: Automatically generated
    directory, that contains the pixel-analyzed board images. Black
    pixels are classified as 'board'. Pink vertical line indicates MHC,
    red vertical line indicates HCV.

**Scripts:**

-   detect\_cut.py = box\_detect\_and\_cut.py

-   transform.py = detect\_and\_transform.py

-   analyze.py = veg\_analyzer.py

-   from\_crd.py = work\_from\_coord.py

See **app** **parameters and results below.**

How to use
==========

**Index page (index.html)**

**Description:**

There are two main ways to use this method (see differences in
**Workflow** above). The first one is to use the coordinates of manually
recorded keypoints, the second includes the automated detection of these
points. Using manually recorded coordinates generally yields more
accurate results, but requires more time and manpower. Keeping these
information in mind, at the first page (**index.html)** the users gets
to decide the preferred method.

**What to do:**

-   Select the first option "Work with coordinates" if you want to
    import or record keypoint coordinates.

-   Select the second option "Detect and transform" if you want
    automated detection.

**Load page (load.html)**

**Description:**

Only relevant if you choose "Work with coordinates" at the first option.

There are two main ways to supply keypoint coordinates for
transformation. The first one is to import them from a CSV file (e.g.
the user previously recorded the coordinates of keypoints using another
image processing software, like ImageJ and exported the results.). This
CSV file needs to contain the following columns (the name of the column
can be passed as a parameter later, see **example\_coords.csv)**:

-   Image\_name: a column which (only!) contains the name of the image.

-   X\_coord: a column which (only!) contains the X coordinates of a
    keypoint.

-   Y\_coord: a column which (only!) contains the Y coordinates of a
    keypoint.

The second way is to record keypoint coordinates using our built-in
annotator module.

**What to do:**

-   Select the first option "Import from CSV" if you already recorded
    keypoint coordinates, and want to import them from a CSV file (see
    structure above).

-   Select the second option "Record keypoint coordinates" if you want
    record keypoint coordinates using our built-in annotator module.

**CSV page (csv.html)**

**Description:**

Only relevant if you choose " Import from CSV" at the second option.

**What to do:**

-   Supply the necessary parameters (see List of parameters below).

**Annotate page (annotate.html)**

**Description:**

Only relevant if you choose "Record keypoint coordinates" at the second
option.

**What to do:**

-   Supply the necessary parameters (see List of parameters below).

**Tagger page (tagger.html)**

**Description:**

Only relevant after you supplied parameters at "Annotate page".

On this page, you can record a keypoint coordinate, by clicking on the
image. After the point is successfully added an orange cross and a menu
element (containing the ID and coordinates of the clicked points) will
appear. You can move a recorded point, by clicking and dragging the
orange cross. After a successful move event the corresponding coordinate
is updated. By holding the 'Ctrl' key while clicking (or using the '-'
button at the sidebar menu), you can delete a recorded point. By holding
the 'Ctrl' key while scrolling you can zoom-in/out on the picture. You
can follow the progress by looking at the top menu (eg. image 1 / 24).
You can navigate through images using the 'Next (→)' and 'Previous (←)'
buttons. **Important:** The recorded points of displayed image are only
saved when clicking 'Next (→)' button.

**What to do:**

-   Click the corners of colored squares (there are 12) as accurate as
    possible on all images.

-   Move points by 'click and drag'.

-   Delete points by 'Ctrl + click' or by using the '-' button on the
    side menu.

**Detect page (detect.html)**

Only relevant if you choose "Detect and transform" at the first option.

**What to do:**

-   Supply the necessary parameters (see List of parameters below).

**Calibrate page (calibrate.html)**

**Description:**

Only relevant after you supplied parameters at "Detect page".

In order to execute the automated detection a calibration step is needed
to determine the average side length of reference squares in pixels. On
this page you can record a keypoint coordinate, by clicking on the
image. After the point is successfully added an orange cross and a menu
element (containing the ID and coordinates of the clicked points) will
appear. You can move a recorded point, by clicking and dragging the
orange cross. After a successful move event the corresponding coordinate
is updated. By holding the 'Ctrl' key while clicking (or using the '-'
button at the sidebar menu), you can delete a recorded point. By holding
the 'Ctrl' key while scrolling you can zoom-in/out on the picture.

**What to do:**

-   Click the corners of colored squares (there are 12) as accurate as
    possible on the calibration image.

-   Move points by 'click and drag'.

-   Delete points by 'Ctrl + click' or by using the '-' button on the
    side menu.

**Final pages**

**Description:**

Only relevant after the structure analysis is done.

This page indicates that the analysis was done without a problem, and
informs you about the location of the results (**see Results below**).

**What to do:**

-   Click 'Home' to go back to 'index page' and start a new analysis.

-   Click 'Check results!' (only after automated detection) to overview
    (and edit) the location of detected keypoints.

-   Otherwise hit 'Ctrl + c' in terminal (from which you started app.py)
    to quit the application.

**Result checker page (check\_results.html)**

Only relevant after the structure analysis is done (only when using
automated detection). This page is mostly identical to **'Tagger
page'**, the main difference being, that on this page the orange crosses
indicating the coordinates of detected keypoints are drawn by default.
By taking a look at the position of the crosses, you can get a feedback
about the accuracy of the transformation, then have the option 're-run'
it using the modified coordinates.

**What to do:**

-   Click the corners of colored squares as accurate as possible on
    images where points are missing (the corner detection failed for one
    or more square, **see Results below**).

-   Move points by 'click and drag' for more accurate results.

-   Remove points by 'Ctrl + click' or by using the '-' button on the
    side menu.

  {#section-5 .ListParagraph}

List of parameters to supply
============================

Path parameters
---------------

-   **Orig image path:** path to directory containing (only!) input
    images

-   **Coord file path**: full file path for CSV file containing keypoint
    coordinates (see structure **above**).

-   **Project dir path**: project directory path. In this directory the
    library structure described in the **workflow** is created, and the
    results are stored.

Board parameters
----------------

-   **Board height:** Height of the whiteboard in cm.

-   **Board width:** Width of the whiteboard in cm.

-   **Square side length**: Side length of reference square in cm.

-   **R Top gap**: The distance between the top of the table and the top
    of the red rectangle in cm.

-   **R Side gap**: The distance between the left side of the table and
    the left side of the red rectangle in cm.

-   **B Top gap**: The distance between the top of the table and the top
    of the blue rectangle in cm.

-   **B Side gap**: The distance between the right side of the table and
    the right side of the blue rectangle in cm.

-   **P Top gap**: The distance between the top of the table and the top
    of the purple rectangle in cm.

-   **P Side gap**: The distance between the left/right side of the
    table and the left/right side of the purple rectangle in cm. Note:
    purple rectangle should be at center.

### **Illustrating board parameters**

![](media/image3.png){width="6.6930555555555555in"
height="9.469444444444445in"}

### How to create your own board

The simplest method is to use a sheet of A4 paper as a dipping tool.
Fold the A4 sheet in half and it will fit neatly between the 3 squares.
On the sheet of paper, the corner points of the 5 cm squares must be
drawn on in advance. Then, by marking out the center of the board and
the sheet, you can position the sheet accurately on the board and draw
the corner points of the squares on the board. Then, using two rulers,
we can construct the 3 squares on the board with absolute precision. Be
sure to draw the edges of the squares exactly along the ruler. There
should be no overhangs. Also, try to paint the squares as evenly as
possible, as this can help the accuracy of recognition.

Additional parameters
---------------------

-   **Separator**: separator of CSV file. Read more at:
    [[https://pandas.pydata.org/docs/reference/api/pandas.read\_csv.html]](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

-   **Header**: header option for read\_csv. Read more at:
    [[https://pandas.pydata.org/docs/reference/api/pandas.read\_csv.html]](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

-   **Colname X**: name of the column containing X coordinates.

-   **Colname Y**: name of the column containing Y coordinates.

-   **Colname IMG**: name of the column containing image names.

-   **Save images:** If checked saves images to project\_dir/images/...
    (see **workflow**).

  {#section-6 .ListParagraph}

Results
=======

The results are stored in project\_dir/results/... (see **workflow and
params**).

**1. cut\_coords.csv:** Contains the coordinates of image cropping. Has
the following columns:

-   img: Name of the image.

-   top\_y: The Y coordinate of the top line of the bounding box.

-   top\_left\_x: The X coordinate of the top left corner of the
    bounding box

-   top\_right\_x: The X coordinate of the top right corner of the
    bounding box

**2. report.txt:** Contains the report of each steps result.

-   First paragraph (automated detection only): Feedback about the
    result of object detection (whiteboard localization). It contains
    the names of images without detected whiteboard, if there is any.
    Otherwise return success note.

-   First paragraph (only when working with manually recorded
    coordinates): Feedback about the number of supplied keypoint
    coordinate on images. Raises 'Count error' if there is any image
    with more/less than 12 coordinate attached to it. Returns the name
    of the image and the count of keypoints attached to it. Otherwise
    return success note.

-   Second paragraph (automated detection only): Feedback about the
    result of reference square detection. Raises 'Count error' if there
    is any picture without detected reference square. The transformation
    can't be executed on listed images. Returns the name of the image.
    Otherwise return success note.

-   Third paragraph (automated detection only): Feedback about the
    results of keypoint detection. Raises 'Count warning' if there is
    any square with less than 4 corner attached to it. The
    transformation is executed, but the results are probably less
    accurate (**see paper noise test section).** Returns the name of the
    image and the color of undetected rectangle. Otherwise return
    success note.

-   Last paragraph (second or fourth based on method): Feedback about
    the results of pixel analysis. Raises 'Value error' if a structural
    variable is 'NA'. Returns the name of the image and name of the
    structural variable. Otherwise return success note.

**3. report\_rerun.txt:** Contains the results of 're-run' (re-run is
only possible after automated detection). The structure is identical to
'report.txt'

**4. vegetation\_structure\_results.csv:** Contains the calculated
structural parameters of each image. Has the following columns:

-   img: Name of the image.

-   la: Calculated leaf area in cm^2^.

-   coverage\_percent: The percentage of board coverage.

-   hcv: Calculated height of closed vegetation in cm.

-   mhc: Calculated maximum vegetation height in cm.

-   vor: Calculated visual obstruction reading value in cm.

-   fhd: Calculated foliage height diversity.

Example (tutorial video)
------------------------

Coming soon!

Rules of thumb
==============

Original image directory should contain the original images, and nothing
else!

Only use images of the same resolution at a time!

Citations
=========

Our paper:

Inspiration:

Point recorder inspired by:
[[https://github.com/techytushar/flask-image-annotator]](https://github.com/techytushar/flask-image-annotator)
