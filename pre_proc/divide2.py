import cv2
import numpy as np

gray = cv2.imread("../temp/roiImg/36.jpg",0)

hasText = 0
cv2.imshow("aefd",gray)
morphKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, morphKernel)
morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 1))
connected = cv2.morphologyEx(grad, cv2.MORPH_CLOSE, morphKernel)
mask = np.zeros(grad.shape[:2], dtype="uint8");
contours, hierarchy = cv2.findContours(connected, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
idx = 0
while idx >= 0:
    x,y,w,h = cv2.boundingRect(contours[idx]);
    img = np.zeros((h,w))
    if(w>0.4*h):
        for i in range(0,h):
         	for j in range(0,w):
         		img[i][j] = gray[y+i][x+j]
       #this is the output imag
        print "got one"
       ##===================================================##
        cv2.imwrite('./output/' + str(hasText) + '.png', img)  #  
       ##===================================================##
    	hasText += 1
    idx = hierarchy[0][idx][0]
