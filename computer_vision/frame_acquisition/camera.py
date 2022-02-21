# Модуль камеры
import sys
import os
import cv2
import imutils
import numpy as np
import time
from multiprocessing import Process, Value, Queue
                

class Camera:
    def __init__(self, src=0, WIDTH=1280, HEIGHT=720, function = lambda data : None):
        self.src = src
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        CODEC=cv2.VideoWriter_fourcc('M','J','P','G')

        self.cam = cv2.VideoCapture(self.src)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.WIDTH)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.HEIGHT)
        self.cam.set(cv2.CAP_PROP_FOURCC, CODEC)
        self.cam.set(cv2.CAP_PROP_FPS, 60)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.img_s = Queue(2)
        self.result = Queue(1)

    def is_face(self):
        return self.result.full()

    def get_img(self):
        while self.img_s.empty():
            pass
        return self.img_s.get()


    def process(self, debug=False):
        while True:
            ret, img = self.cam.read()

            if not ret:
                continue
            img = cv2.flip(img, 0)

            if self.img_s.full():
                self.img_s.get()
            self.img_s.put(img)

            if not (res is None):
                if self.result.empty():
                    self.result.put(res)
            else:
                if self.result.full():
                    self.result.get()
                
            if debug:
                if not (res is None):
                    cv2.rectangle(img, (res[0], res[1]), (res[2], res[3]), (0, 255, 0), 2)
                cv2.imshow('camera_output', img)
                cv2.waitKey(1)
            
    def start(self, debug=False):
        self.c = Process(target=self.process, args=(debug,))
        self.c.start()
        time.sleep(2.0)

    def stop(self):
        self.c.kill()
        cv2.destroyAllWindows()
        self.cam.release()


if __name__ == '__main__':
    try:
        c = Camera()
        c.start(True)
        time.sleep(50.0)
        c.stop()
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        sys.exit()
