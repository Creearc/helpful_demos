import cv2

class Knife:
  def __init__(self):
    self.frame = None

    self.moving = False
    self.old_moving = False

  def analyse(self):
    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
    self.frame = cv2.threshold(self.frame, 40, 255, cv2.THRESH_BINARY)[1]
    self.frame = cv2.blur(self.frame, (5, 5))
    self.frame = cv2.threshold(self.frame, 200, 255, cv2.THRESH_BINARY)[1]
    h, w = self.frame.shape[:2]
    return self.frame[h // 2, int(w * 0.2)] != 0

  def is_knife_moving(self):
    self.old_moving = self.moving
    self.moving = self.analyse()
    return self.old_moving and not self.moving
    
  
