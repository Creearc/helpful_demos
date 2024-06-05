import sys
import cv2
import numpy as np
import time


class Camera():
    def __init__(self, src=0, WIDTH=1280, HEIGHT=720, use_buffer=True, multiprocessing=False):
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

        self.image = None

        self.multiprocessing = multiprocessing
        self.stop = False

        if not self.multiprocessing:
            import threading
            self.run_method = threading
            self.lock = threading.Lock()
            
        else:
            import multiprocessing
            from multiprocessing import Queue
            self.run_method = multiprocessing
            self.image_q = Queue(1)


    def start(self):
        if not self.multiprocessing:
            self.c = self.run_method.Thread(target=self.process, args=())
            self.c.start()
        else:
            self.c = self.run_method.Process(target=self.process, args=())
            self.c.start()


    def stop(self):
        self.stop = True        


    def process(self):
        while self.cam.isOpened():
            ret, img = self.cam.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            if not self.multiprocessing:
                with self.lock:
                    self.image = img.copy()
            else:
                if not self.image_q.full():
                    self.image_q.put_nowait(img.copy())
        

    def get_img(self):
        if not self.multiprocessing:
            with self.lock:
                return self.image
        else:
            if not self.depth_q.empty(): 
                return self.image_q.get_nowait()


if __name__ == '__main__':
    try:
        c = Camera(0)
        c.start()
        
        while True:
            img = c.get_img()
            if img is None:
                print('empty')
                continue
            cv2.imshow('img', img)
            if cv2.waitKey(1) == 27:
                break
        c.stop = True
        cv2.destroyAllWindows()
        
    except KeyboardInterrupt:
        sys.exit()
