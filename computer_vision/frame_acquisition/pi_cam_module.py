import cv2
import numpy as np
import time
import io
from threading import Condition
import threading
from multiprocessing import Process, Value, Queue
import picamera

main_frame = None
lock = threading.Lock()


class Camera():
    def __init__(self, resolution=(640, 480), framerate=90,
                             mode='auto', white_balance='auto',
                             effect='none',
                             show_fps=False):
        self.resolution = resolution
        self.framerate = framerate
        self.show_fps = show_fps

        self.image = None
        self.mode = mode
        self.white_balance = white_balance
        self.effect = effect

    def start(self):
        self.p = threading.Thread(target=self.process, args=()).start()

    def process(self):
        global main_frame, lock
        with picamera.PiCamera(resolution=self.resolution,
                                                     framerate=self.framerate) as camera:
            output = StreamingOutput()
            camera.start_recording(output, format='mjpeg')
            camera.exposure_mode = self.mode
            camera.awb_mode = self.white_balance
            camera.image_effect = self.effect

            t = time.time()

            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame

                try:
                    img = cv2.imdecode(np.frombuffer(frame, np.uint8), 1)
                except:
                    continue

                h, w = img.shape[:2]
                self.image = img.reshape((h, w, 3))   

                if self.show_fps:
                    print(1 / (time.time() - t))
                    t = time.time()

    def get(self):
        with lock:
            if self.image is None:
                return None
            else:
                return self.image.copy()

if __name__ == '__main__':
    c = Camera(resolution=(1920, 1080), framerate=30, show_fps=True)
    c.start()
    
    while True:
        img = c.get()
        if img is None:
            print('empty')
            continue
