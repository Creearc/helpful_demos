import cv2
import imutils
import numpy as np

img = cv2.imread('../sample_binary.png')

img = imutils.resize(img, width=640)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

new = imutils.skeletonize(gray, size=(3, 3))
cv2.imshow('skeletonize', np.hstack([gray, new]))

new = imutils.auto_canny(gray)
cv2.imshow('auto_canny', np.hstack([gray, new]))

new1 = imutils.adjust_brightness_contrast(gray, brightness=50.0, contrast=50.0)
# new2 = imutils.adjust_brightness_contrast(gray, brightness=0.0, contrast=100.0)
cv2.imshow('adjust_brightness_contrast', np.hstack([gray, new1]))
cv2.waitKey(0)
cv2.destroyAllWindows()
