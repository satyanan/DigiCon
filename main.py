import os
import sys
import logging
from PyQt4 import QtGui, QtCore
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import time
import requests
import json
import cv2 as cv
import numpy as np
from reportlab.pdfgen import canvas
import qdarkstyle


# pdf.cell(200,10,'Powered by FPDF',0,1,'C')


def setupLogging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    loggerHandler = logging.StreamHandler(sys.stdout)
    loggerHandler.setLevel(logging.DEBUG)
    loggerFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    loggerHandler.setFormatter(loggerFormatter)
    logger.addHandler(loggerHandler)

def SaveFigureAsImage(fileName,fig=None,**kwargs):
    fig_size = fig.get_size_inches()
    w,h = fig_size[0], fig_size[1]
    fig.patch.set_alpha(0)
    if kwargs.has_key('orig_size'): # Aspect ratio scaling if required
        w,h = kwargs['orig_size']
        w2,h2 = fig_size[0],fig_size[1]
        fig.set_size_inches([(w2/w)*w,(w2/w)*h])
        fig.set_dpi((w2/w)*fig.get_dpi())
    a=fig.gca()
    a.set_frame_on(False)
    a.set_xticks([]); a.set_yticks([])
    plt.axis('off')
    plt.xlim(0,h); plt.ylim(w,0)
    fig.savefig(fileName, transparent=True, bbox_inches='tight',pad_inches=0)

def SaveFigureAsImage(fileName,fig=None):
    fig_size = fig.get_size_inches()
    w,h = fig_size[0], fig_size[1]
    fig.patch.set_alpha(0)
    a=fig.gca()
    a.set_frame_on(False)
    a.set_xticks([]); a.set_yticks([])
    plt.axis('off')
    plt.xlim(0,h); plt.ylim(w,0)
    fig.savefig(fileName, transparent=True, bbox_inches='tight',pad_inches=0)

def azureCVDispProcessing(analysis, image_path):
    polygons = [(line["boundingBox"], line["text"]) for line in analysis["recognitionResult"]["lines"]] 
    img_path = str(image_path)
    print(img_path)
    img = cv.imread(img_path)
    height, width, channels = img.shape
    bg_img = img
    for polygon in polygons:
        vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
        cv.fillPoly(bg_img, pts=np.int32([vertices]), color=(0,255,0))
    cv.imwrite('./temp/bg_img.jpg',bg_img)
    c.drawImage('./temp/bg_img.jpg',0,0)    
    for polygon in polygons:
        vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
        text     = polygon[1]
        # print vertices
        min_x = min(vertices, key = lambda t: t[0])[0]
        min_y = min(vertices, key = lambda t: t[1])[1]
        max_x = max(vertices, key = lambda t: t[0])[0]
        max_y = max(vertices, key = lambda t: t[1])[1]
        # print min_x,min_y,max_x,max_y
        # cv.fillPoly(img, pts=np.int32([vertices]), color=(0,255,0))
        cv.rectangle(img,(min_x,min_y),(max_x,max_y),(0,255,0),cv.cv.CV_FILLED)
        cv.putText(img, text, vertices[0], cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1 , cv.CV_AA)
        c.drawString(min_x,height-(min_y+max_y)/2,text)
    cv.imwrite( "./temp/azureCVDispProcessing.jpg", img)
    qimg = cv.cvtColor(img, cv.cv.CV_BGR2RGB)#for Qt display
    logging.debug('Image with ROI saved')
    c.save()
    return qimg

def azureDispProcessing(analysis, image_path):
    polygons = [(line["boundingBox"], line["text"]) for line in analysis["recognitionResult"]["lines"]] 
    plt.figure(figsize=(15,15))
    image  = mpimg.imread(image_path)
    ax     = plt.imshow(image)
    for polygon in polygons:
        vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
        text     = polygon[1]
        patch    = Polygon(vertices, closed=True,fill=True, linewidth=2, color='y')
        ax.axes.add_patch(patch)
        plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")
    _ = plt.axis("off")
    plt.show(block=False)
    logging.debug('Image with ROI saved')

def azureHandwriting(image_path):
    subscription_key = "00c800bde4fe46b7b36fc42aba617e6b"
    assert subscription_key
    vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
    text_recognition_url = vision_base_url + "RecognizeText"

    # using image in disk
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
    qimg = azureCVDispProcessing(analysis=analysis, image_path=image_path)
    return qimg
    

class Window(QtGui.QMainWindow):
    image_path = ''
    # progressBar = None
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 1024, 768)
        self.setWindowTitle("DigiCon")

        self.centralwidget = QtGui.QWidget(self)
        # self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.pb = QtGui.QProgressBar(self.centralwidget)
        self.pb.setGeometry(QtCore.QRect(20, 20, 3001, 301))
        self.pb.setRange(0,1000)
        self.pb.setProperty("value", 10)
        self.pb.move(10,10)
        # self.pb.setObjectName(_fromUtf8("pb"))

        openFile = QtGui.QAction("&File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip("Open File")
        openFile.triggered.connect(self.file_open)

        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)

        # self.lbl = QtGui.QLabel(self)
        # self.setCentralWidget(self.lbl)

        self.home()

    def home(self):
        # progressBar = QtGui.QProgressBar()
        # progressBar.setMinimum(1)
        # progressBar.setMaximum(100)
        # progressBar.setValue(50)
        # progressBar.move(100,100)
        # progressBar.resize(100,100)
        # progressBar.repaint()

        process_btn = QtGui.QPushButton("Process", self)
        process_btn.clicked.connect(lambda: self.processImage(process_btn))
        process_btn.resize(100,100)
        process_btn.move(100,100)
        process_btn.setVisible(False)

        open_btn = QtGui.QPushButton("Open an image", self)
        open_btn.clicked.connect(lambda: self.file_open(open_btn, process_btn))
        open_btn.resize(100,100)
        open_btn.move(100,100)

        
        self.show()

    def file_open(self, open_btn, process_btn):
        self.image_path = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        logging.debug('Image path is' + self.image_path)

        open_btn.setVisible(False)
        process_btn.setVisible(True)

    def processImage(self, process_btn):
        # pixmap = QtGui.QPixmap(image_path)
        # self.lbl.setPixmap(pixmap)
        # logging.debug('Image opened')

        img = azureHandwriting(self.image_path)
        # self.lbl.setPixmap(QtGui.QPixmap("./temp/azureCVDispProcessing.jpg"))

        process_btn.setVisible(False)

        # logging.debug('azured image displayed')
def run():
    setupLogging()
    app = QtGui.QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())
    GUI = Window()
    sys.exit(app.exec_())

c = canvas.Canvas("./temp/test.pdf")
run()