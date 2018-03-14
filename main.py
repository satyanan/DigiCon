import sys
import logging
from PyQt4 import QtGui, QtCore
from PIL import Image
from io import BytesIO
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import time
import requests
import json

def setupLogging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    loggerHandler = logging.StreamHandler(sys.stdout)
    loggerHandler.setLevel(logging.DEBUG)
    loggerFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    loggerHandler.setFormatter(loggerFormatter)
    logger.addHandler(loggerHandler)

def azureDispProcessing(analysis, image_path):
    polygons = [(line["boundingBox"], line["text"]) for line in analysis["recognitionResult"]["lines"]] 
    plt.figure(figsize=(15,15))
    image  = mpimg.imread(image_path)
    ax     = plt.imshow(image)
    for polygon in polygons:
        vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
        text     = polygon[1]
        patch    = Polygon(vertices, closed=True,fill=False, linewidth=2, color='y')
        ax.axes.add_patch(patch)
        plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")
    _ = plt.axis("off")
    plt.show(block=False)
    logging.debug('Image with ROI displayed')

def azureHandwriting(image_path):
    subscription_key = "cfa2ac95fcf04101b79b839837876d16"
    assert subscription_key
    vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
    text_recognition_url = vision_base_url + "RecognizeText"
    
    # # When using url of image to be analysed
    # image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Cursive_Writing_on_Notebook_paper.jpg/800px-Cursive_Writing_on_Notebook_paper.jpg"    
    # headers  = {'Ocp-Apim-Subscription-Key': subscription_key}
    # params   = {'handwriting' : True}
    # data     = {'url': image_url}
    # response = requests.post(text_recognition_url, headers=headers, params=params, data=json.dumps(data))
    # response.raise_for_status()

    # When using image in disk
    image_data = open(image_path, "rb").read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key, 
              "Content-Type": "application/octet-stream" }
    params   = {'handwriting' : True}
    response = requests.post(text_recognition_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()
    
    operation_url = response.headers["Operation-Location"]
    analysis = {}
    while not "recognitionResult" in analysis:
        logging.info('Polling azure GET')
        response_final = requests.get(response.headers["Operation-Location"], headers=headers)
        analysis       = response_final.json()
        time.sleep(1)
    azureDispProcessing(analysis=analysis, image_path=image_path)
    

class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100, 100, 500, 300)
        self.setWindowTitle("PyQT Show Image")

        openFile = QtGui.QAction("&File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip("Open File")
        openFile.triggered.connect(self.file_open)

        self.statusBar()

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)

        self.lbl = QtGui.QLabel(self)
        self.setCentralWidget(self.lbl)

        self.home()

    def home(self):
        self.show()

    def file_open(self):
        image_path = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        logging.debug('Image path is' + image_path)
        pixmap = QtGui.QPixmap(image_path)
        self.lbl.setPixmap(pixmap)
        logging.debug('Image opened')
        azureHandwriting(image_path)
        

def run():
    setupLogging()
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()