import sys
import os
import cv2
import numpy as np
import time


VIDEO_PATHS = ['A:/Projects/sveza/namazka/namazka_2/result_0_1.avi',
               'A:/Projects/sveza/namazka/namazka_2/result_0_2.avi',
               'A:/Projects/sveza/namazka/namazka_2/result_0_3.avi',
               'A:/Projects/sveza/namazka/namazka_2/result_1_0.avi']

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
    videos = [cv2.VideoCapture(path) for path in VIDEO_PATHS]

    w, h = 1920*2, 1080*2
    frame_rate = 30
    codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    vid_out = cv2.VideoWriter('video.mp4',
                              codec, frame_rate,
                              (w, h))

    while True:
        imgs = [video.read()[1] for video in videos]
        if any([img is None for img in imgs]):
            break

        img = np.vstack([np.hstack(imgs[:2]),
                         np.hstack(imgs[2:])])
        vid_out.write(img)
    vid_out.release()
    
    

