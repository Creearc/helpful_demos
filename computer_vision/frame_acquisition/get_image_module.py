import sys
import cv2
import numpy as np
import time


class Camera():
    def __init__(self, src=0, WIDTH=1280, HEIGHT=720, use_buffer=True):
        self.src = src
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        CODEC = cv2.VideoWriter_fourcc('M','J','P','G')

        self.cam = cv2.VideoCapture(self.src)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.WIDTH)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.HEIGHT)
        self.cam.set(cv2.CAP_PROP_FOURCC, CODEC)
        self.cam.set(cv2.CAP_PROP_FPS, 60)
        if use_buffer:
            self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)


    def stop(self):
        self.cam.release()        


    def get_img(self):
        while self.cam.isOpened():
            ret, img = self.cam.read()
            if not ret:
                time.sleep(0.1)
                continue
            yield img


if __name__ == '__main__':
    try:
        c = Camera(0)
        for img in c.get_img():
            cv2.imshow('img', img)
            if cv2.waitKey(1) == 27:
                break
        c.stop()
        cv2.destroyAllWindows()
        
    except KeyboardInterrupt:
        sys.exit()
