import sys
import os
import cv2
import numpy as np
import time
import threading

import ip_cam_module
import functions


def video_record():
    global c, img_buf, lock
    w, h = 1920, 1080
    frame_rate = 30
    codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    vid_out = cv2.VideoWriter('video.mp4',
                              codec, frame_rate,
                              (w, h))
    img = None
    while img is None:
        img = c.get_img()
        
    print('Record!')
    
    for i in range(1000):
        print(i)
        
        img = c.get_img()

        out = functions.fix_collision(img)
        out = cv2.resize(out, (1920, 1080), interpolation = cv2.INTER_AREA)
        
        vid_out.write(out)

    vid_out.release()
    print('Finish!')


if __name__ == '__main__':
    lock = threading.Lock()

    img_buf = None
    
    c = ip_cam_module.IPCamera()
    c.start()
    threading.Thread(target=video_record, args=()).start()
