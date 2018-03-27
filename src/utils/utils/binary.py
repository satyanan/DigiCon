import cv2 as cv
import numpy as np

def resize(img):
  # resizing image for standardization
  x,y = img.shape[:2]
  x=float(1200/float(x))
  y=float(1200/float(y))
  res = cv.resize(img,None,fx=float(x), fy=float(y), interpolation = cv.INTER_LINEAR)
  return res
# ******************** Image smoothing ************************
def convolutional_blur(img):
  # simple 2D convolutional image filter / averaging
  kernel = np.ones((3,3),np.float32)/25 #creates a 3X3 kernel of ones 
  dst = cv.filter2D(img,-1,kernel)
  return dst
def gaussian_blur(img):
  # gaussian blurring 
  gaussian = cv.GaussianBlur(img,(3,3),0)
  return gaussian
def median_blur(img):
  # median blurring- highly effective against salt and pepper noise
  median= cv.medianBlur(img,5)
  return median
def bilateralFilter(img):
  # Bilateral Filtering- highly effective in noise removal while keeping edges sharp
  bilateral= cv.bilateralFilter(img,9,75,75) 
  return bilateral
def smooth_image(img):
  # blur the image to reduce noise 
  dst= median_blur(img)
  dst= gaussian_blur(dst)
  dst= bilateralFilter(dst)
  return dst
# ************************** Binarization *****************
def adaptive_thresholding(img):
  # adaptive mean binary threshold
  th4 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)
  
  th5 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
  cv.imshow("ddfcdsa",th5)
  cv.waitKey(0)
  return th5
def otsu_binarisation(img):
  # global thresholding
  ret1,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
  # Otsu's thresholding
  ret2,th2 = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
  # Otsu's thresholding after Gaussian filtering
  blur = cv.GaussianBlur(img,(3,3),0)
  ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
  return th3
def hist_equalise(img):
  eq=cv.equalizeHist(img)
  return eq

def binary(img):
# For handwritten notes the sequence of preprocessing should be as follows:- 
# resizing
# Clustering if loading in color else load in grayscale 
# Image filtering to reduce noise in grayscale image, the choise of filters depends on the type of noise 
# Histogram Equalisation 
# Thresholding 
# Binarization
# Smoothing ----- this is only necessary for handwritten mode, and not for the screep capture mode
  # img=resize(img)
  th = img
  th = smooth_image(img) 
  th = adaptive_thresholding(th)
  th = otsu_binarisation(th)
  th = smooth_image(th)
  print(img.shape)
  print(th.shape)
  return th
