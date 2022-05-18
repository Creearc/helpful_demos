import os
import cv2
import time

from modules import video_module
video_path = 'video/test'
images_path = 'images/test'


for file in os.listdir(video_path):
    c = video_module.Video('{}/{}'.format(video_path, file))
    print('------------')
    print(file)
    print('------------')
    
    for frame_number, img in c.get_img(first_frame=0, step=30):
        name = '{}/{}.jpg'.format(images_path, time.time())
        cv2.imwrite(name, img)
        print(name)
