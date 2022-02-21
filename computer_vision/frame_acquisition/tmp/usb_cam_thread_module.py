import sys
import cv2
import numpy as np
import time
from multiprocessing import Process, Value, Queue


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

        self.img_s = Queue(2)
        

    def start(self, debug=False):
        self.c = Process(target=self.process, args=())
        self.c.start()

    def stop(self):
        self.c.kill()
        self.cam.release()

    def process(self):
        while self.cam.isOpened():
            ret, img = self.cam.read()
            if not ret:
                time.sleep(0.1)
                continue

            if self.img_s.full():
                self.img_s.get()
            self.img_s.put(img)

    def get_img(self):
        if self.img_s.full():
            return self.img_s.get()
        else:
            return None


if __name__ == '__main__':
    try:
        c = Camera()
        c.start(True)
        time.sleep(50.0)
        c.stop()
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        sys.exit()