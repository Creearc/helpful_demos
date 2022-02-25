import sys
import cv2
import numpy as np
import time


class Video():
    def __init__(self, path):
        self.path = path
        self.cam = cv2.VideoCapture(self.path)

        self.frame_count = int(self.cam.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = int(self.cam.get(cv2.CAP_PROP_FPS))
        self.w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))      


    def get_img(self, first_frame=0, last_frame=None, step=1):
        if last_frame is None:
            last_frame=self.frame_count

        self.cam.set(cv2.CAP_PROP_POS_FRAMES, first_frame)
        for frame_number in range(first_frame, last_frame, step):
            #self.cam.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
            #self.cam.set(1, frame_number-1)
            ret, img = self.cam.read()
            if not ret:
                time.sleep(0.1)
                continue
            yield frame_number, img


if __name__ == '__main__':
    try:
        path = 'D:/exercise_tracker/Robot trainer video/IMG_0340.mp4'
        c = Video(path)
        for frame_number, img in c.get_img(first_frame=200):
            cv2.imshow('img', img)
            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()
        
    except KeyboardInterrupt:
        sys.exit()
