import os
import cv2
import numpy as np

def rotate_img(img, angle):
  (h, w) = img.shape[:2]
  (cX, cY) = (w // 2, h // 2)

  M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
  return cv2.warpAffine(img, M, (w, h))

dataset_path = 'dataset'
dataset_output_path = 'dataset2'

paths = ['1']


for folder in paths:
  for img_name in os.listdir('{}/{}'.format(dataset_path, folder)):
    img = cv2.imread('{}/{}/{}'.format(dataset_path, folder, img_name))

##    for angle in [0, 90, 180, 270]:
##      img2 = rotate_img(img, angle)
##      cv2.imwrite('{}/{}/{}_{}'.format(dataset_output_path,
##                                       folder, angle, img_name), img2)
