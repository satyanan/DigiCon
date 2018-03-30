#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
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
sys.path.insert(0, '../autocorrect/')
from autocorrect import correctPage
# import autocorrect
'''
The prescription calss holds the prescription image and has all mutators to it
'''
class prescription:

    imagePath = ''
    wordROI = []
    wordROIList = []
    correctedWordROIList = []
    height = 0

    def __init__(self, imagePath):
        self.imagePath = imagePath
        self.c = canvas.Canvas('../temp/output/result.pdf')
        self.pdf = canvas.Canvas('../temp/output/finalResult.pdf')
    # From the detrected words recreates the image with digital version of text.
    def azureCVDispProcessing(self, analysis):
        image_path = self.imagePath
        polygons = [(line['boundingBox'], line['text']) for line in
                    analysis['recognitionResult']['lines']]
        self.azurePolygons = polygons
        img_path = str(image_path)
        img = cv.imread(img_path)
        (height, _width, _channels) = img.shape
        self.height = height
        bg_img = img
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i + 1]) for i in
                        range(0, len(polygon[0]), 2)]
            cv.fillPoly(bg_img, pts=np.int32([vertices]), color=(255,
                        255, 255))
        self.c.setPageSize((_width, height))
        self.pdf.setPageSize((_width, height))
        cv.imwrite('../temp/bg_img.jpg', bg_img)
        self.c.drawImage('../temp/bg_img.jpg', 0, 0)
        self.pdf.drawImage('../temp/bg_img.jpg', 0, 0)
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i + 1]) for i in
                        range(0, len(polygon[0]), 2)]
            text = polygon[1]
            min_x = min(vertices, key=lambda t: t[0])[0]
            min_y = min(vertices, key=lambda t: t[1])[1]
            max_x = max(vertices, key=lambda t: t[0])[0]
            max_y = max(vertices, key=lambda t: t[1])[1]
            cv.rectangle(img, (min_x, min_y), (max_x, max_y), (255, 255,
                         255), cv.cv.CV_FILLED)
            fontThickness = 2
            if  ((max_y-min_y)*0.02) < 0.5:
                fontThickness = 1
            cv.putText(
                img,
                text,
                (min_x, (min_y + max_y) / 2),
                cv.FONT_HERSHEY_SIMPLEX,
                (max_y-min_y)*0.015,
                (0, 0, 0),
                1,
                cv.CV_AA,
                )
            self.c.setFont('Helvetica', 0.5*(max_y-min_y))
            self.c.drawString(min_x, height - (min_y + max_y) / 2, text)
        cvImg = cv.cvtColor(img, cv.cv.CV_BGR2RGB)  # for Qt display
        setupLogging.logging.debug('Image with ROI saved')
        self.c.save()
        return cvImg
    # Handwriting text detection using state of the art method. 
    def imageAzureHandwriting(self):
        image_path = self.imagePath
        subscription_key = 'e7a1767260db447ca17ab7815dd7a3c9'
        assert subscription_key
        vision_base_url = \
            'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/'
        text_recognition_url = vision_base_url + 'RecognizeText'

        # using image in disk

        image_data = open(image_path, 'rb').read()
        headers = {'Ocp-Apim-Subscription-Key': subscription_key,
                   'Content-Type': 'application/octet-stream'}
        params = {'handwriting': True}
        response = requests.post(text_recognition_url, headers=headers,
                                 params=params, data=image_data)
        response.raise_for_status()
        _operation_url = response.headers['Operation-Location']
        analysis = {}
        while not 'recognitionResult' in analysis:
            setupLogging.logging.info('Polling azure GET')
            response_final = \
                requests.get(response.headers['Operation-Location'],
                             headers=headers)
            analysis = response_final.json()
            time.sleep(1)
        qimg = self.azureCVDispProcessing(analysis=analysis)
        return (qimg, analysis)
    # Denoises the raw input image of the prescription
    def imageDenoising(self, img):
        img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        return img
    # Converts the colour imge of the prescription to a black and white image with black text and white background
    def imageBinarization(self, img):
        img_sobel = cv.Sobel(img, cv.CV_8U, 1, 0, 3)
        img_threshold = cv.threshold(img_sobel, 0, 255, cv.THRESH_OTSU
                + cv.THRESH_BINARY)[1]
        img_threshold = 255 - img_threshold
        return img_threshold
    # Detects the line of texts in the binarised image
    def imageLOTDetection(self, img):
        return img
    # Draws ROI into the image from the detected ROIs
    def imageWordROIDetection(self, img):
        imageWordROIDetected = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
        for roi in self.wordROI:
            cv.rectangle(imageWordROIDetected, (roi[0], roi[2]),
                         (roi[1], roi[3]), (0, 255, 0), 2)
        return imageWordROIDetected

    def imageNNWordDetection(self, img):
        return img

    def imageWordSpellcorrection(self):
        img_path = str(self.imagePath)
        img = cv.imread(img_path)
        self.wordListCorrected = correctPage(self.wordList, self.wordROIFlag)
        for i in range(len(self.wordListCorrected)):
            min_x, max_x, min_y, max_y = self.wordROI[i]
            text = self.wordListCorrected[i]
            cv.rectangle(img, (min_x, min_y), (max_x, max_y), (255, 255,
                         255), cv.cv.CV_FILLED)
            fontThickness = 2
            if  ((max_y-min_y)*0.02) < 0.5:
                fontThickness = 1
            cv.putText(
                img,
                text+ '{' + str(self.wordROIFlag[i]) + '}',
                (min_x, (min_y + max_y) / 2),
                cv.FONT_HERSHEY_SIMPLEX,
                (max_y-min_y)*0.015,
                (0, 0, 0),
                1,
                cv.CV_AA,
                )
            self.pdf.setFont('Helvetica', 0.5*(max_y-min_y))
            self.pdf.drawString(min_x, self.height - (min_y + max_y) / 2, text )
        self.pdf.save()
        return img
    # Using trained deep neural network model to detect split characters
    def charToNN(self, charImg):
        cvImgResized = cv.resize(255 - charImg, (50, 50)).reshape(1,
                2500)

        lab = LabelEncoder()
        l = map(chr, list(range(ord('0'), ord('9') + 1))
                + list(range(ord('A'), ord('Z') + 1))
                + list(range(ord('a'), ord('z') + 1)))
        lab.fit(l)
        len(lab.classes_)

        mlp = pkl.load(open('../classifier/classifier.bin', 'rb'))
        return (True, 'i', 0.0)
    def dpEval(self, dpMatrix):
        return (0.0, 'a')
    # Using our improved algorithm for splitting handwritten words into chracters and hence detecting words
    def wordImgToNN(self, wordImg):
        (height, width) = wordImg.shape
        windowMinSize = 1
        windowSize = 1
        windowSizeStep = 1
        prevX = 0
        detectedWord = ''
        detectionArray = [0]
        for i in range(0, width):
            if prevX + windowSize > width:
                break
            (detected, charDetected, _) = self.charToNN(wordImg[0:
                    height, prevX:prevX + windowSize])
            if detected == True:
                prevX = prevX + windowSize
                windowSize = windowMinSize
                detectedWord += charDetected
                detectionArray.append(prevX)
            else:
                windowSize += windowSizeStep
        return (detectedWord, detectionArray)
    # Uses probabilistic model for finding the most probable word represented by a ROI
    def wordTree(
        self,
        startPos,
        prevProb,
        dpMatrix,
        heap,
        maxAggregation=3,
        ):

        for i in range(1, maxAggregation + 1):
            (_detected, detectedChar, detectionProb) = \
                dpMatrix[startPos][i]
            if len(heap[i + startPos]) > 10:
                if heapq.nsmallest(1, heap)[0].first > detectionProb \
                    * prevProb:
                    return
            heapq.heappush(heap, (detectionProb, detectedChar))
    # Used improved=II method for finding the best probabilistic match of an ROI to a word in the vocabulary
    def wordImgToNNTree(self, wordImg):
        (height, width) = wordImg.shape
        windowSize = 10
        maxAggregation = 3
        nWindows = width / windowSize + 1
        self.dpMatrix = [[(False, 'a', 0.0) for _x in range(nWindows)]
                         for _y in range(nWindows)]
        for i in range(nWindows):
            for j in range(1, maxAggregation + 1):
                imgToTest = wordImg[0:height, i * windowSize:min(width,
                                    (i + j) * windowSize)]
                (_, _wide) = wordImg.shape
                if _wide <= 0:
                    continue
                setupLogging.logging.debug(i * windowSize, (i + j)
                        * windowSize, width)
                (detected, detectedChar, detectionProb) = \
                    self.charToNN(imgToTest)
                self.dpMatrix[i][j] = (detected, detectedChar,
                        detectionProb)

        heap = [[(0.0, '')] for i in range(nWindows)]
        self.wordTree(0, 1, self.dpMatrix, heap, 3)
    # Takes each ROI and prepares it for CNN input and then implements our improved-I algorithm
    def wordImgToNNDP(self, wordImg):
        (height, width) = wordImg.shape
        windowSize = 1
        maxAggregation = 4
        maxRows = width / windowSize + 1
        dpMatrix = [[(False, 'a', 0.0) for _x in range(maxRows)]
                    for _y in range(maxAggregation)]
        for i in range(0, maxRows):
            x = i * windowSize
            for j in range(1, maxAggregation):
                if x > width:
                    continue
                if x + windowSize * j > width:
                    continue
                (detected, detectedChar, probChar) = \
                    self.charToNN(wordImg[0:height, x:x + windowSize
                                  * j])
                dpMatrix[i][j] = (detected, detectedChar, probChar)

        (detectedWord, detectionArray) = self.dpEval(dpMatrix)

        return (detectedWord, detectionArray)

    def wordCorrection(self):
        pass
    # Takes roi pilygons and makes a list of ROIs and it's bounding rectangles for further processing
    def imageWordToList(self, bImg):
        self.wordROIFlag = []
        self.wordList = []
        if len(bImg.shape) == 2:
            binarisedImg = cv.cvtColor(bImg, cv.COLOR_GRAY2RGB)
        else:
            binarisedImg = bImg

        for polygon in self.azurePolygons:
            vertices = [(polygon[0][i], polygon[0][i + 1]) for i in
                        range(0, len(polygon[0]), 2)]
            _text = polygon[1]
            self.wordList.append(_text)
            min_x = min(vertices, key=lambda t: t[0])[0]
            min_y = min(vertices, key=lambda t: t[1])[1]
            max_x = max(vertices, key=lambda t: t[0])[0]
            max_y = max(vertices, key=lambda t: t[1])[1]
            self.wordROI.append((min_x, max_x, min_y, max_y))
            mid = (min_y+max_y)/2
            if(mid < 0.3*self.height):
                self.wordROIFlag.append(-1)
            elif(mid< 0.56*self.height):
                self.wordROIFlag.append(0)
            else:
                self.wordROIFlag.append(1)
            roi = binarisedImg[min_y:max_y, min_x:max_x]
            self.wordROIList.append(roi)
        return self.wordROIList



			