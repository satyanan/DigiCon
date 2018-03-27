import time
import requests
import json
import cv2 as cv
import numpy as np
import heapq
from reportlab.pdfgen import canvas
import setupLogging
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import pickle as pkl
from utils.binary import *
'''
Maintains prescriptiin's image and its mutators and processing functions. 
Also contains method for generating the pdf output
'''
class prescription():
    imagePath = ""
    wordROI = []
    wordROIList = []
    correctedWordROIList = []
    
    def __init__(self, imagePath):
        self.imagePath = imagePath
        self.c = canvas.Canvas("../temp/test.pdf")

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
        self.c.drawImage('../temp/bg_img.jpg',0,0)    
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
            self.c.drawString(min_x,height-(min_y+max_y)/2,text)
        # cv.imwrite( "../temp/azureCVDispProcessing.jpg", img)
        cvImg = cv.cvtColor(img, cv.cv.CV_BGR2RGB)#for Qt display
        setupLogging.logging.debug('Image with ROI saved')
        self.c.save()
        return cvImg

    def imageAzureHandwriting(self):
        image_path = self.imagePath
        subscription_key = "00c800bde4fe46b7b36fc42aba617e6b"
        assert subscription_key
        vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
        text_recognition_url = vision_base_url + "RecognizeText"

        # using image in disk
        image_data = open(image_path, "rb").read()
        headers    = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/octet-stream" }
        params   = {'handwriting' : True}
        response = requests.post(text_recognition_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()
        _operation_url = response.headers["Operation-Location"]
        analysis = {}
        while not "recognitionResult" in analysis:
            setupLogging.logging.info('Polling azure GET')
            response_final = requests.get(response.headers["Operation-Location"], headers=headers)
            analysis       = response_final.json()
            time.sleep(1)
        qimg = self.azureCVDispProcessing(analysis=analysis)
        return qimg, analysis

    def imageDenoising(self, img):
        img= cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        return img

    def imageBinarization(self, img):
        img_sobel = cv.Sobel(img, cv.CV_8U, 1, 0, 3)
	img_threshold = cv.threshold(img_sobel, 0, 255, cv.THRESH_OTSU+cv.THRESH_BINARY)[1]
	img_threshold = 255 - img_threshold
        #kernel = np.ones((3,3),np.uint8)
	#img_threshold = cv.erode(img_threshold,kernel,iterations = 1)
        return img_threshold
  	
    def imageLOTDetection(self, img):
        return img

    def imageWordROIDetection(self, img):
        imageWordROIDetected = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
        for roi in self.wordROI:
            cv.rectangle(imageWordROIDetected,(roi[0],roi[2]),(roi[1],roi[3]),(0,255,0),2)
        return imageWordROIDetected

    def imageNNWordDetection(self, img):
        return img

    def imageWordSpellcorrection(self, img):
        return img

    def charToNN(self, charImg):
        cvImgResized = cv.resize(255-charImg, (50, 50)).reshape(1,2500)

        lab = LabelEncoder()
        l = map(chr, list(range(ord('0'), ord('9')+1))+list(range(ord('A'), ord('Z')+1))+list(range(ord('a'), ord('z')+1)))
        lab.fit(l)
        len(lab.classes_)

        mlp = pkl.load(open('../classifier/classifier.bin', 'rb'))
        print (mlp.predict_proba(cvImgResized)[0])
        return True, 'i', 0.0

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

        for i in range(1, maxAggregation + 1):
            _detected, detectedChar, detectionProb = dpMatrix[startPos][i]
            if(len(heap[i+ startPos]) > 10): # and len(heap[i+ detectionProb]) > 0.03**(i+maxAggregation) ):
                if(heapq.nsmallest(1, heap)[0].first > detectionProb*prevProb):
                    return
            heapq.heappush(heap, (detectionProb, detectedChar))

    def wordImgToNNTree(self, wordImg):
        height, width = wordImg.shape
        windowSize = 10
        maxAggregation = 3
        nWindows = width/windowSize + 1
        self.dpMatrix = [[(False,'a', 0.0) for _x in range(nWindows)] for _y in range(nWindows)]
        for i in range(nWindows):
            for j in range(1, maxAggregation+1):
                imgToTest = wordImg[0:height, i*windowSize:min(width, (i+j)*windowSize)]
                _, _wide = wordImg.shape
                if _wide <=0:
                    continue
                setupLogging.logging.debug(i*windowSize, (i+j)*windowSize, width)
                detected, detectedChar, detectionProb = self.charToNN(imgToTest)
                self.dpMatrix[i][j] = (detected, detectedChar, detectionProb)

        # for row in self.dpMatrix:
        #     for val in row:
        #         print '{:4}'.format(val[1]),
        #     print

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

    def wordCorrection(self):
        pass

    def imageWordToList(self, bImg):
        if(len(bImg.shape) == 2):
            binarisedImg = cv.cvtColor(bImg, cv.COLOR_GRAY2RGB)
        else:
            binarisedImg = bImg

        for polygon in self.azurePolygons:
            vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
            _text     = polygon[1]
            min_x = min(vertices, key = lambda t: t[0])[0]
            min_y = min(vertices, key = lambda t: t[1])[1]
            max_x = max(vertices, key = lambda t: t[0])[0]
            max_y = max(vertices, key = lambda t: t[1])[1]
            self.wordROI.append((min_x,max_x,min_y,max_y))
            roi = binarisedImg[min_y:max_y,min_x:max_x]
            self.wordROIList.append(roi)
        return self.wordROIList
