import numpy as np
import cv2
import imutils

class MoveDetector:
  def __init__(self):
    self.frame = None
    self.old_frame = None

    self.moving = False
    self.old_moving = False
  
  def analyse(self):
    gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    val = 0
    mx = 0

    if not(self.old_frame is None):
      hsv = np.zeros_like(self.frame)
      hsv[...,1] = 255
      
      flow = cv2.calcOpticalFlowFarneback(self.old_frame, gray, None, pyr_scale = 0.5,
                                          levels = 3,
                                          winsize = 11, iterations = 3, poly_n = 2,
                                          poly_sigma = 1.1, flags = 0)

      mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
      gray_2 = cv2.threshold(mag.astype(np.uint8), 1, 255, cv2.THRESH_BINARY)[1]

      cnts = cv2.findContours(gray_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      cnts = imutils.grab_contours(cnts)
      if len(cnts) > 0:
        val = cv2.contourArea(max(cnts, key=cv2.contourArea))
        
      #cv2.imshow('gray_2', gray_2)
        
    self.old_frame = gray.copy()
    frame = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) > 0:
      mx = cv2.contourArea(max(cnts, key=cv2.contourArea))
        
    #print('Mx: {} Val: {}'.format(mx, val))
    #cv2.imshow("moving", frame)
    return not (mx > 4000 and val == 0.0)

  def is_shpon_not_moving(self):
    self.old_moving = self.moving
    self.moving = self.analyse()
    return self.old_moving and not self.moving
