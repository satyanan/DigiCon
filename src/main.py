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
import pickle as pkl
import heapq
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder

def setupLogging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    loggerHandler = logging.StreamHandler(sys.stdout)
    loggerHandler.setLevel(logging.DEBUG)
    loggerFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    loggerHandler.setFormatter(loggerFormatter)
    logger.addHandler(loggerHandler)

# def SaveFigureAsImage(fileName,fig=None,**kwargs):
#     fig_size = fig.get_size_inches()
#     w,h = fig_size[0], fig_size[1]
#     fig.patch.set_alpha(0)
#     if kwargs.has_key('orig_size'): # Aspect ratio scaling if required
#         w,h = kwargs['orig_size']
#         w2,h2 = fig_size[0],fig_size[1]
#         fig.set_size_inches([(w2/w)*w,(w2/w)*h])
#         fig.set_dpi((w2/w)*fig.get_dpi())
#     a=fig.gca()
#     a.set_frame_on(False)
#     a.set_xticks([]); a.set_yticks([])
#     plt.axis('off')
#     plt.xlim(0,h); plt.ylim(w,0)
#     fig.savefig(fileName, transparent=True, bbox_inches='tight',pad_inches=0)

# def SaveFigureAsImage(fileName,fig=None):
#     fig_size = fig.get_size_inches()
#     w,h = fig_size[0], fig_size[1]
#     fig.patch.set_alpha(0)
#     a=fig.gca()
#     a.set_frame_on(False)
#     a.set_xticks([]); a.set_yticks([])
#     plt.axis('off')
#     plt.xlim(0,h); plt.ylim(w,0)
#     fig.savefig(fileName, transparent=True, bbox_inches='tight',pad_inches=0)
class prescription():
    imagePath = ""

    def __init__(self, imagePath):
        self.imagePath = imagePath


    def azureCVDispProcessing(self, analysis):
        image_path = self.imagePath
        polygons = [(line["boundingBox"], line["text"]) for line in analysis["recognitionResult"]["lines"]] 
        self.azurePolygons = polygons
        img_path = str(image_path)
        img = cv.imread(img_path)
        height, _width, _channels = img.shape
        bg_img = img
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
            cv.fillPoly(bg_img, pts = np.int32([vertices]), color=(0,255,0))
        cv.imwrite('../temp/bg_img.jpg',bg_img)
        c.drawImage('../temp/bg_img.jpg',0,0)    
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
            text     = polygon[1]
            min_x = min(vertices, key = lambda t: t[0])[0]
            min_y = min(vertices, key = lambda t: t[1])[1]
            max_x = max(vertices, key = lambda t: t[0])[0]
            max_y = max(vertices, key = lambda t: t[1])[1]
            # cv.fillPoly(img, pts=np.int32([vertices]), color=(0,255,0))
            cv.rectangle(img,(min_x,min_y),(max_x,max_y),(0,255,0),cv.cv.CV_FILLED)
            cv.putText(img, text, vertices[0], cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1 , cv.CV_AA)
            c.drawString(min_x,height-(min_y+max_y)/2,text)
        # cv.imwrite( "../temp/azureCVDispProcessing.jpg", img)
        cvImg = cv.cvtColor(img, cv.cv.CV_BGR2RGB)#for Qt display
        logging.debug('Image with ROI saved')
        c.save()
        return cvImg

    def imageAzureHandwriting(self):
        image_path = self.imagePath
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
        
        _operation_url = response.headers["Operation-Location"]
        analysis = {}
        while not "recognitionResult" in analysis:
            logging.info('Polling azure GET')
            response_final = requests.get(response.headers["Operation-Location"], headers=headers)
            analysis       = response_final.json()
            time.sleep(1)
        qimg = self.azureCVDispProcessing(analysis=analysis)
        return qimg, analysis

    def imageDenoising(self, img):
        img= cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        return img

    def imageBinarization(self, img):
        blur = cv.GaussianBlur(img,(3,3),0)
        _ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        return th3

    def imageLOTDetection(self, img):
        return img

    def imageWordROIDetection(self, img):
        return img

    def imageNNWordDetection(self, img):
        return img

    def imageWordSpellcorrection(self, img):
        return img

    def charToNN(self, charImg):
        mlp = pkl.load(open('../classifier/classifier.bin', 'rb'))
        return False, 'i', 0.0

    def wordImgToNN(self, wordImg):
        height, width = wordImg.shape
        windowMinSize = 1
        windowSize = 1
        windowSizeStep = 1
        prevX = 0
        detectedWord = ""
        detectionArray = [0]
        for i in range(0,width):
            if prevX+windowSize > width:
                break
            detected, charDetected, _ = self.charToNN(wordImg[0:height,prevX:prevX+windowSize])
            if detected == True:
                prevX = prevX+windowSize
                windowSize = windowMinSize
                detectedWord += charDetected
                detectionArray.append(prevX)
            else:
                windowSize += windowSizeStep
        return detectedWord, detectionArray

    def wordTree(self, startPos, prevProb, dpMatrix, heap, maxAggregation = 3):

        for i in range(1, maxAggregation+1):
            _detected, detectedChar, detectionProb = dpMatrix[startPos][startPos + i]
            # heap[startPos+i].heappush((detectionProb, detectedChar))
            if(len(heap[i+ detectionProb]) > 10): # and len(heap[i+ detectionProb]) > 0.03**(i+maxAggregation) ):
                if(heapq.nsmallest(1, heap)[0].first > detectionProb*prevProb):
                    return
            heapq.heappush((detectionProb, detectedChar), heap)

    def wordImgToNNTree(self, wordImg):
        height, width = wordImg.shape()
        windowSize = 3
        maxAggregation = 3
        nWindows = width/windowSize + 1
        self.dpMatrix = [[(False,'a', 0.0) for _x in range(nWindows)] for _y in range(nWindows)]
        for i in range(nWindows):
            for j in range(maxAggregation):
                detected, detectedChar, detectionProb = self.charToNN(wordImg[0:height, i*windowSize:min(width, (i+1)*windowSize)])
                self.dpMatrix[i][j] = (detected, detectedChar, detectionProb)
        heap = [[(0.0, "")] for i in range(nWindows)]
        self.wordTree(0, 1, self.dpMatrix, heap, 3)
        
    def wordImgToNNDP(self, wordImg):
        height, width = wordImg.shape
        windowSize = 1
        maxAggregation = 4
        maxRows = width/windowSize + 1
        dpMatrix = [[(False,'a', 0.0) for _x in range(maxRows)] for _y in range(maxAggregation)]
        for i in range(0,maxRows):
            x = i*windowSize
            for j in range(1,maxAggregation):
                if x > width:
                    continue
                if x + windowSize*j > width:
                    continue
                detected, detectedChar, probChar = self.charToNN(wordImg[0:height, x:x+windowSize*j])
                dpMatrix[i][j] = (detected, detectedChar, probChar)
        detectedWord, detectionArray = self.dpEval(dpMatrix)

        return detectedWord, detectionArray

    def dpEval(self, dpMatrix):
        return (0.0,'a')

    def imageWordToList(self, bImg):
        if(len(bImg.shape) == 2):
            binarisedImg = cv.cvtColor(bImg, cv.COLOR_GRAY2RGB)
        else:
            binarisedImg = bImg
        wordROIList = []

        for polygon in self.azurePolygons:
            vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
            _text     = polygon[1]
            min_x = min(vertices, key = lambda t: t[0])[0]
            min_y = min(vertices, key = lambda t: t[1])[1]
            max_x = max(vertices, key = lambda t: t[0])[0]
            max_y = max(vertices, key = lambda t: t[1])[1]
            roi = binarisedImg[min_y:max_y,min_x:max_x]
            wordROIList.append(roi)
            # cv.imshow("dsdsd",roi )
            # cv.waitKey(0)
        return wordROIList
        
class Window(QtGui.QMainWindow):
    image_path = ''
    imageSeq = []
    currentSeq = -1
    processingComplete = False

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 1024, 768)
        self.setWindowTitle("DigiCon")

        self.lbl = QtGui.QLabel(self)
        self.setCentralWidget(self.lbl)
        
        self.lbl.progressBar = QtGui.QProgressBar(self)
        self.lbl.progressBar.setGeometry(QtCore.QRect(20, 20, 1024, 30))
        self.lbl.progressBar.setRange(0,1024)
        self.lbl.progressBar.setProperty("value", 1)
        self.lbl.progressBar.move(0,500)
        self.lbl.progressBar.setVisible(False)

        openFile = QtGui.QAction("&File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip("Open File")
        openFile.triggered.connect(self.file_open)

        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)

        self.home()

    def home(self):
        self.process_btn = QtGui.QPushButton("Process", self)
        self.process_btn.clicked.connect(lambda: self.processImage())
        self.process_btn.resize(100,100)
        self.process_btn.move(100,100)
        self.process_btn.setVisible(False)

        self.open_btn = QtGui.QPushButton("Open an image", self)
        self.open_btn.clicked.connect(lambda: self.file_open())
        self.open_btn.resize(100,100)
        self.open_btn.move(100,100)

        self.show()

    def file_open(self):
        self.image_path = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        self.prescriptionInstance = prescription(str(self.image_path))
        logging.debug('Image path is' + self.image_path)

        self.open_btn.setVisible(False)
        self.lbl.progressBar.setVisible(True)
        self.process_btn.setVisible(True)

    def progressBarUpdate(self):
        self.lbl.progressBar.setValue(self.progressBarCurrent)
        self.progressBarCurrent += self.progressBarIncrement
        self.lbl.progressBar.repaint()

    def imageSeqHandler(self, _cvImg):
        #Just saves image in imgSeq for displaying in GUI
        if(len(_cvImg.shape) == 2):
            cvImg = cv.cvtColor(_cvImg, cv.COLOR_GRAY2RGB)
        else:
            cvImg = _cvImg
        height, width, channel = cvImg.shape
        bytesPerLine = channel*3 #Error prone in case of binarized images
        _qImg = QtGui.QImage(cvImg, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        self.imageSeq.append(cvImg)

    def processingStepsHandler(self, cvImg):
        # GUI stuff
        self.imageSeqHandler(cvImg)
        self.progressBarUpdate()

    def processImage(self):
        self.progressBarIncrement = 1024/8
        self.progressBarCurrent = self.progressBarIncrement

        virginImg = cv.imread(str(self.image_path))

        self.processingStepsHandler(virginImg)
        denoisedImg = self.prescriptionInstance.imageDenoising(virginImg)
        self.processingStepsHandler(denoisedImg)
        binarisedImg = self.prescriptionInstance.imageBinarization(denoisedImg)
        self.processingStepsHandler(binarisedImg)
        LOTDetectedImg = self.prescriptionInstance.imageLOTDetection(binarisedImg)
        self.processingStepsHandler(LOTDetectedImg)
        wordROIDetectedImg = self.prescriptionInstance.imageWordROIDetection(binarisedImg)
        self.processingStepsHandler(wordROIDetectedImg)
        NNWordDetectedImg = self.prescriptionInstance.imageNNWordDetection(binarisedImg)
        self.processingStepsHandler(NNWordDetectedImg)
        wordSpellcorrectedImg = self.prescriptionInstance.imageWordSpellcorrection(binarisedImg)
        self.processingStepsHandler(wordSpellcorrectedImg)
        azuredImg, _azureAnalysis = self.prescriptionInstance.imageAzureHandwriting()
        self.processingStepsHandler(azuredImg)

        wordROIList = self.prescriptionInstance.imageWordToList(binarisedImg)
        NNTestImg = cv.imread("../temp/roiImg/32.jpg",0)
        # _NNTestDetectedWord, _NNTestDetectionArray = self.prescriptionInstance.wordImgToNN(NNTestImg)
        _detectedWordTree = self.prescriptionInstance.wordImgToNNTree(NNTestImg)

        i = 0
        print(len(wordROIList))
        for roiImg in wordROIList:
            i+=1
            logging.debug("saving "+ str(i))
            cv.imwrite("../temp/roiImg/"+str(i)+".jpg",roiImg)

        self.processingComplete = True
        self.lbl.setPixmap(QtGui.QPixmap("../test.jpg"))
        self.adjustSize()

        self.process_btn.setVisible(False)
        self.lbl.progressBar.setVisible(False)

    def dispalyHandler(self):
        print("display handler called")
        cv.imwrite("../temp/res.jpg",self.imageSeq[self.currentSeq])
        self.lbl.setPixmap(QtGui.QPixmap("../temp/res.jpg"))
        self.lbl.repaint()
        self.adjustSize()
    
    def leftKeyHandler(self):
        if(self.processingComplete == False):
            return
        if(self.currentSeq == 0):
            return
        self.currentSeq -= 1
        self.dispalyHandler()

    def rightKeyHandler(self):
        if(self.processingComplete == False):
            return
        if(self.currentSeq == len(self.imageSeq)-1):
            return
        self.currentSeq += 1
        self.dispalyHandler()
        
    def keyPressEvent(self, event):
        print("keyPressEvent happened",self.currentSeq, len(self.imageSeq))
        if event.key() == QtCore.Qt.Key_P:
            logging.info("Left key pressed")
            self.leftKeyHandler()
        elif event.key() == QtCore.Qt.Key_N:
            logging.info("Right key pressed")
            self.rightKeyHandler()
        event.accept()

def run():
    setupLogging()
    app = QtGui.QApplication(sys.argv)
    sshFile="./stylesheet/darkOrange.stylesheet"
    with open(sshFile,"r") as fh:
        app.setStyleSheet(fh.read())
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())
    _GUI = Window()
    sys.exit(app.exec_())

c = canvas.Canvas("../temp/test.pdf")
run()
