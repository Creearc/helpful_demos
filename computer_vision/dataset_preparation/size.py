import os
import random
import cv2
import imutils
from imutils import paths
import numpy as np

def prepare_img_size(size, path):
  for imagePath in paths.list_images(path):
    out = cv2.imread(imagePath)
    if isinstance(size, tuple):
      out = cv2.resize(out, size, cv2.INTER_AREA)
    else:
      out = imutils.resize(out, width=size)
    cv2.imwrite(imagePath, out)


prepare_img_size((1280, 720),
                 'backgrounds')
