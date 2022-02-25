import sys
import numpy as np
import cv2 as cv

hsv_min = np.array((51, 11, 48), np.uint8)  #белый 64, 10, 56
hsv_max = np.array((64, 10, 56), np.uint8) # 51°, 11%, 48%
color_red = (0,0,255)

if __name__ == '__main__':
    fn = 'tesa1.jpg'
    img = cv.imread(fn)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    thresh = cv.inRange(hsv, hsv_min, hsv_max)
    moments = cv.moments(thresh, 1)
    dM01 = moments['m01']
    dM10 = moments['m10']
    dArea = moments['m00']

    contours0, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        if len(cnt)>200:
            ellipse = cv.fitEllipse(cnt)
            cv.ellipse(img,ellipse,(0,0,255),2)
            x = int(dM10 / dArea)
            y = int(dM01 / dArea)
            cv.circle(img, (x, y), 5, color_red, 2)
            cv.putText(img, "x=%d, y=%d" % (x,y), (x+10,y-10), 
                cv.FONT_HERSHEY_SIMPLEX, 1, color_red, 2)

    cv.imshow('contours', img)

    cv.waitKey()
    cv.destroyAllWindows()