import numpy as np
import cv2

img = cv2.imread('tesa1.jpg')
cv2.imshow('tesa1.jpg',img)
res = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
res = cv2.Canny(img,200,255)
rows = img.shape[0]

res = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)


#'''
circles = cv2.HoughCircles(res, cv2.HOUGH_GRADIENT, 1, rows / 8,
                               param1=100, param2=30,
                               minRadius=10, maxRadius=300)
for i in circles[0, :]:
    center = (i[0], i[1])
    print(center)
    radius = i[2]
    cv2.circle(res, center, radius, (255, 0, 255), 3)
    cv2.putText(res, "D=%d" % (2*radius), (center[0] + radius, center[1] - radius), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
#'''


cv2.imshow('result.jpg',res) 
cv2.waitKey(0)
cv2.destroyAllWindows()