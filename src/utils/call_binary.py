#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
from utils.binary import *
import sys

img = cv2.imread(sys.argv[1], 0)
img_gray = img
img_sobel = cv.Sobel(img_gray, cv.CV_8U, 1, 0, 3)
img_threshold = cv.threshold(img_sobel, 0, 255, cv.THRESH_OTSU
                             + cv.THRESH_BINARY)[1]
r1 = binary(img)
r = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
cv2.namedWindow('ddf', cv2.WINDOW_NORMAL)
cv2.imshow('ddf', r)
cv2.namedWindow('ddf2', cv2.WINDOW_NORMAL)
cv2.imshow('ddf2', r1)
cv2.namedWindow('ddf2er', cv2.WINDOW_NORMAL)
cv2.imshow('ddf2er', img_threshold)

cv2.waitKey(0)

			