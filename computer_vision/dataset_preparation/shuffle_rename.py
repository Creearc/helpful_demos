import os
import cv2
import random

from modules import video_module
source_path = 'images/train_orig'
new_path =  'images/train'

files = os.listdir(source_path)
random.shuffle(files)

for i, file_name in enumerate(files):

    img = cv2.imread('{}/{}'.format(source_path, file_name))
    name = '{}/{}.jpg'.format(new_path, i)
    cv2.imwrite(name, img)
    print(name)
