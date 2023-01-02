import cv2
import multiprocessing
from multiprocessing import Pipe
import mss
import numpy as np
import threading
import time


class Screen():

    def __init__(self, screen_width=640, screen_height=480):
        self.image = None
        self.sct = mss.mss()
        self.monitor = {"top": 0, "left": 0, "width": screen_width, "height": screen_height}
        self.lock = threading.Lock()
        self.stop = False


    def start(self):
        self.c =  threading.Thread(target=self.process, args=())
        self.c.start()


    def stop(self):
        self.stop = True 


    def get_img(self):
        if self.image is None:
            return
        #(B, G, R, A) = cv2.split(self.image)
        #self.image = cv2.merge([B, G, R])
        with self.lock:
            return self.image


    def process(self):
        while not self.stop:
            img = np.array(self.sct.grab(self.monitor))
            
            with self.lock:
                self.image = img.copy()


if __name__=="__main__":

    rec = True

    width = 640
    height = 480

    if rec:
        fps = 30.0
        codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        out = cv2.VideoWriter('{}.mp4'.format(str(time.ctime()).replace(':', '_')),
                                  codec, fps,
                                  (width, height))
    s = Screen(screen_width=width, screen_height=height)
    s.start()
    
    while True:
        
        img = s.get_img()
        
        if img is None:
            #print('empty' + str(time.time()))
            continue
        
        cv2.imshow('img', img)
        if rec:        
            out.write(img)
        
        if cv2.waitKey(1) == 27:
            break

    s.stop = True
    if rec:
        out.release()
    cv2.destroyAllWindows()

    
