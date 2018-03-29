#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import prescription
import setupLogging
import qdarkstyle
import os
import cv2 as cv


class Window(QtGui.QMainWindow):

    image_path = ''
    # statusBar = None
    imageSeq = []
    currentSeq = -1
    processingComplete = False

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 1024, 768)
        desktop = QtGui.QDesktopWidget()
        self.screenSize = \
            desktop.availableGeometry(desktop.primaryScreen())
        self.setFixedSize(1024, 768)
        self.setWindowTitle('DigiCon')

        self.lbl = QtGui.QLabel(self)
        self.setCentralWidget(self.lbl)
        # Setting up progress bar view
        self.lbl.progressBar = QtGui.QProgressBar(self)
        self.lbl.progressBar.setGeometry(QtCore.QRect(20, 20, 1024, 30))
        self.lbl.progressBar.setRange(0, 1024)
        self.lbl.progressBar.setProperty('value', 1)
        self.lbl.progressBar.move(0, 500)
        self.lbl.progressBar.setVisible(False)
        # Setting up file open command
        openFile = QtGui.QAction('&File', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.file_open)
        # Setting up status bar
        self._statusBar = QStatusBar()
        self.setStatusBar(self._statusBar)
        self._statusBar.showMessage('Press N for next/ P for previous')
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().setVisible(False)
        
        self.home()
    # Sets up home page views and buttons
    def home(self):
        # Setting up process button
        self.process_btn = QtGui.QPushButton('Process', self)
        self.process_btn.clicked.connect(lambda : self.processImage())
        self.process_btn.resize(120, 30)
        self.process_btn.move(452, 540)
        self.process_btn.setVisible(False)
        # Sets up file open button
        self.open_btn = QtGui.QPushButton('Open an image', self)
        self.open_btn.clicked.connect(lambda : self.file_open())
        self.open_btn.resize(120, 30)
        self.open_btn.move(452, 540)
        # Sets up image preview
        self.image_btn = QtGui.QPushButton('', self)
        self.image_btn.setVisible(False)
        # Render view
        self.show()
    # File open handler function
    def file_open(self):
        # Gettign the image path and rescaling it to reduce further processing time
        self.image_path = QtGui.QFileDialog.getOpenFileName(self,
                'Open File')
        bigImage = cv.imread(str(self.image_path))
        (height, width, _) = bigImage.shape
        rescaledImg = cv.resize(bigImage, (1024 * width / height, 1024))
        cv.imwrite('../temp/output/input.jpg', rescaledImg)
        self.image_path = QtCore.QString('../temp/output/input.jpg')
        self.prescriptionInstance = \
            prescription.prescription(str(self.image_path))
        setupLogging.logging.debug('Image path is' + self.image_path)
        # Triggering some GUI changes on file opening
        icon = QtGui.QIcon()
        _inp = QtGui.QPixmap('../temp/output/input.jpg')
        inp = _inp.scaled(250, 420, QtCore.Qt.KeepAspectRatio)
        icon.addPixmap(inp)
        self.image_btn.setIcon(icon)
        self.image_btn.setIconSize(inp.rect().size())
        self.image_btn.resize(250, 420)
        self.image_btn.move(412, 40)
        self.image_btn.setVisible(True)

        self.open_btn.setVisible(False)
        self.lbl.progressBar.setVisible(True)
        self.process_btn.setVisible(True)
    # Progress update handler
    def progressBarUpdate(self):
        self.lbl.progressBar.setValue(self.progressBarCurrent)
        self.progressBarCurrent += self.progressBarIncrement
        self.lbl.progressBar.repaint()
    # The sequence of output handler
    def imageSeqHandler(self, _cvImg):
        if len(_cvImg.shape) == 2:
            cvImg = prescription.cv.cvtColor(_cvImg,
                    prescription.cv.COLOR_GRAY2RGB)
        else:
            cvImg = _cvImg
        (height, width, channel) = cvImg.shape
        bytesPerLine = channel * 3  # Error prone in case of binarized images
        _qImg = QtGui.QImage(cvImg, width, height, bytesPerLine,
                             QtGui.QImage.Format_RGB888)
        self.imageSeq.append(cvImg)
    # Hnadles the bookkeeping after each processing step like saving intermediate outputs for viewing later and updating views
    def processingStepsHandler(self, cvImg):
        self.imageSeqHandler(cvImg)
        self.progressBarUpdate()
    # Top level processing order handler. Calls functions upon the input prescription image and also does the bookkeeping stuff
    def processImage(self):
        self.progressBarIncrement = 1024 / 8
        self.progressBarCurrent = self.progressBarIncrement

        virginImg = prescription.cv.imread(str(self.image_path))

        self.processingStepsHandler(virginImg)
        denoisedImg = \
            self.prescriptionInstance.imageDenoising(virginImg)
        self.processingStepsHandler(denoisedImg)
        binarisedImg = \
            self.prescriptionInstance.imageBinarization(denoisedImg)
        self.processingStepsHandler(binarisedImg)
        (azuredImg, _azureAnalysis) = \
            self.prescriptionInstance.imageAzureHandwriting()

        _wordROIList = \
            self.prescriptionInstance.imageWordToList(binarisedImg)
        wordROIDetectedImg = \
            self.prescriptionInstance.imageWordROIDetection(binarisedImg)
        wordSpellcorrectedImg = \
            self.prescriptionInstance.imageWordSpellcorrection(azuredImg)
        self.processingStepsHandler(wordROIDetectedImg)
        self.processingStepsHandler(azuredImg)
        self.prescriptionInstance.wordCorrection()
        self.processingStepsHandler(wordSpellcorrectedImg)

        self.processingComplete = True
        (_height, _width, _) = self.imageSeq[0].shape
        self.saveIntermediateImgs()
        self.statusBar().setVisible(True)        
        self.rightKeyHandler()
        self.adjustSize()
        self.image_btn.setVisible(False)
        self.process_btn.setVisible(False)
        self.lbl.progressBar.setVisible(False)
    # Display/GUI changes on event handled by this function
    def dispalyHandler(self):
        self._statusBar.showMessage('Press N for next/ P for previous     Showing: '+ str(self.currentSeq+1) + '/6')
        setupLogging.logging.debug('display handler called')

        (currentWidth, currentHeight, _) = \
            self.imageSeq[self.currentSeq].shape
        newHeight = int(768 * currentHeight / currentWidth)
        scaledImage = cv.resize(self.imageSeq[self.currentSeq],
                                (newHeight, 768))

        prescription.cv.imwrite('../temp/disp.jpg', scaledImage)
        self.lbl.setPixmap(QtGui.QPixmap('../temp/disp.jpg'))
        self.lbl.repaint()
        self.setFixedSize(newHeight, 768)
        self.adjustSize()
    # P key press event handling helper function
    def leftKeyHandler(self):
        if self.processingComplete == False:
            return
        if self.currentSeq == 0:
            return
        self.currentSeq -= 1
        self.dispalyHandler()
    # N key press event handling helper function
    def rightKeyHandler(self):
        if self.processingComplete == False:
            return
        if self.currentSeq == len(self.imageSeq) - 1:
            return
        self.currentSeq += 1
        self.dispalyHandler()
    # Key press event handler function
    def keyPressEvent(self, event):
        setupLogging.logging.debug('keyPressEvent happened',
                                   self.currentSeq, len(self.imageSeq))
        if event.key() == QtCore.Qt.Key_P:
            setupLogging.logging.info('Left key pressed')
            self.leftKeyHandler()
        elif event.key() == QtCore.Qt.Key_N:
            setupLogging.logging.info('Right key pressed')
            self.rightKeyHandler()
        event.accept()
    # Makes a directory if it does not exist
    def makeDirectoryIfDNE(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    # Deletes all files and folders in a directory
    def cleanDirectory(self, directory):
        for the_file in os.listdir(directory):
            file_path = os.path.join(directory, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                setupLogging.logging.warning(e)
    # Saves all intemediate output images for debugging
    def saveIntermediateImgs(self):
        directory = '../temp/output/intermediateImgs/'
        self.makeDirectoryIfDNE(directory)
        self.cleanDirectory(directory)
        i = 0
        for img in self.imageSeq:
            cv.imwrite(directory + str(i) + '.jpg', img)
            i += 1