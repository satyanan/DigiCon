from PyQt4 import QtGui, QtCore
import prescription
import setupLogging
import qdarkstyle

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
        self.prescriptionInstance = prescription.prescription(str(self.image_path))
        setupLogging.logging.debug('Image path is' + self.image_path)

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
            cvImg = prescription.cv.cvtColor(_cvImg, prescription.cv.COLOR_GRAY2RGB)
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

        virginImg = prescription.cv.imread(str(self.image_path))

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
        NNTestImg = prescription.cv.imread("../temp/roiImg/32.jpg",0)
        # _NNTestDetectedWord, _NNTestDetectionArray = self.prescriptionInstance.wordImgToNN(NNTestImg)
        _detectedWordTree = self.prescriptionInstance.wordImgToNNTree(NNTestImg)

        # # To save image roi's to be used later I guess
        # i = 0
        # print(len(wordROIList))
        # for roiImg in wordROIList:
        #     i+=1
        #     logging.debug("saving "+ str(i))
        #     cv.imwrite("../temp/roiImg/"+str(i)+".jpg",roiImg)

        self.processingComplete = True
        self.lbl.setPixmap(QtGui.QPixmap("../test.jpg"))
        self.adjustSize()

        self.process_btn.setVisible(False)
        self.lbl.progressBar.setVisible(False)

    def dispalyHandler(self):
        print("display handler called")
        prescription.cv.imwrite("../temp/res.jpg",self.imageSeq[self.currentSeq])
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
            setupLogging.logging.info("Left key pressed")
            self.leftKeyHandler()
        elif event.key() == QtCore.Qt.Key_N:
            setupLogging.logging.info("Right key pressed")
            self.rightKeyHandler()
        event.accept()