import sys
import os
import cv2
import numpy as np
import time
import threading

lock = threading.Lock()

    
def camera_quality(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


class IPCamera:
    def __init__(self, src="rtsp://admin:admin@192.168.0.20:8554/CH001.sdp", debug=False):
        self.src = src
        self.lock = threading.Lock()
        self.debug = debug
        self.img = None


    def get_img(self):
        with self.lock:
            return self.img


    def process(self):
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.cam = cv2.VideoCapture(self.src, cv2.CAP_FFMPEG)

        mx = 500
        i = 0
        t = time.time()
        
        while True:
            ret, img = self.cam.read()    
            if not ret:
                print(time.ctime(), 'No frame')
                time.sleep(5.0)
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
                self.cam = cv2.VideoCapture(self.src, cv2.CAP_FFMPEG)
                continue
            
            with self.lock:
                self.img = img
            
            if self.debug:
                i += 1
                if i == mx:
                    i = 0
                    fps = mx / (time.time() - t)
                    t = time.time()
                    print('Camera quality = {} FPS = {}'.format(int(camera_quality(img)), fps))
     

    def start(self):
        c = threading.Thread(target=self.process, args=())
        c.start()


if __name__ == '__main__':
    import time
    c = IPCamera(debug=True)
    c.start()
