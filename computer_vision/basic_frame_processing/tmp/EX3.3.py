# Pavel Slivnitsin. MDS2. Image retrieval - Exercise 3.3
# https://docs.opencv.org/master/d9/d61/tutorial_py_morphological_ops.html 

# Import libraries
import numpy as np
import cv2

img = cv2.imread('1.png')
cv2.imshow('1.png',img)

kernel = np.ones((3,3),np.uint8)

'''
res = cv2.erode(img,kernel,iterations = 1)
res = cv2.dilate(res,kernel,iterations = 1)
cv2.imshow('res1.png',res)

res = cv2.dilate(img,kernel,iterations = 1)
res = cv2.erode(res,kernel,iterations = 1)
cv2.imshow('res2.png',res)
'''

res = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel) # opening
cv2.imshow('res3.png',res)

'''
res = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel) # closing
cv2.imshow('res4.png',res)

res = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel) 
res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel) 
cv2.imshow('res5.png',res)

res = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel) 
res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, kernel) 
cv2.imshow('res6.png',res)

res = cv2.dilate(img,kernel,iterations = 1)
res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel) # opening
res = cv2.erode(res,kernel,iterations = 1)
cv2.imshow('res7.png',res)

res = cv2.dilate(img,kernel,iterations = 1)
res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel) # opening
res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel) # opening
cv2.imshow('res8.png',res)

'''
cv2.waitKey(0)
cv2.destroyAllWindows()