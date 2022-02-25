import cv2
import numpy as np

img = cv2.imread('tesa1.jpg')
cv2.imshow('origin', img)


res = cv2.Canny(img,250,255)
rows = img.shape[0]
circles = cv2.HoughCircles(res, cv2.HOUGH_GRADIENT, 1, rows / 8,
                               param1=100, param2=30,
                               minRadius=10, maxRadius=300)
for i in circles[0, :]:
  center = (int(i[0]), int(i[1])) 
  radius = i[2]
  print(radius * 2)
  cv2.circle(res, center, int(radius), (255, 0, 255), 3)

cv2.imshow('out', res)

cv2.waitKey(0)
cv2.destroyAllWindows()
