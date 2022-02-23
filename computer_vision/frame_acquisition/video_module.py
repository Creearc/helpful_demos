import sys
import cv2
import numpy as np
import time


class Video():
    def __init__(self, path, use_buffer=True):
        self.path = path
        CODEC = cv2.VideoWriter_fourcc('M','J','P','G')
        self.cam = cv2.VideoCapture(self.path)

        self.frame_count = int(self.cam.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = int(self.cam.get(cv2.CAP_PROP_FPS))
        self.w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

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
        path = 'D:/exercise_tracker/Robot trainer video/IMG_0340.mp4'
        c = Video(path)
        for img in c.get_img():
            cv2.imshow('img', img)
            if cv2.waitKey(1) == 27:
                break
        c.stop()
        cv2.destroyAllWindows()
        
    except KeyboardInterrupt:
        sys.exit()
