import sys
import os
import cv2
import imutils
import numpy as np
import time
import threading

from flask import Response
from flask import Flask
from flask import render_template

import functions

lock = threading.Lock()

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")


@app.route("/video_feed")
def video_feed():
  return Response(generate(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")

def generate():
  global c
  while True:
    out = c.get_img2()
    if out is None:
      time.sleep(0.1)
      continue
    out = cv2.resize(out, (1920 // 4, 1080 // 4), interpolation = cv2.INTER_AREA)
    (flag, encodedImage) = cv2.imencode(".jpg", out)
    if not flag:
      time.sleep(0.1)
      continue
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

  
def camera_quality(img):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  return cv2.Laplacian(gray, cv2.CV_64F).var()

def save_img(img):
  path = 'data'
  cv2.imwrite('{}/{}.jpg'.format(path, len(os.listdir(path))), img)

def hamming(a, b):
  return bin(int(a) ^ int(b)).count("1")

def dhash(img, hashSize=3):
  if hashSize != None:
    img = cv2.resize(img, (hashSize, hashSize))
    img = cv2.blur(img, (3, 3))
  diff = img[:, 1:] > img[:, :-1]
  return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

class Camera:
  def __init__(self, src="rtsp://admin:admin@192.168.0.20:8554/CH001.sdp"):
    self.src = src
    self.lock = threading.Lock()

    self.img = None
    self.img2 = None

  def get_img(self):
    with self.lock:
      return self.img

  def get_img2(self):
    with self.lock:
      return self.img2

  def img_to_img2(self, img):
    with self.lock:
      self.img2 = img.copy()

  def process(self):
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
    self.cam = cv2.VideoCapture(self.src,
                            cv2.CAP_FFMPEG)
    mx = 500
    i = 0
    t = time.time()
    h_old, h = 0, 0
    while True:
      ret, img = self.cam.read()    
      if not ret:
        print(time.ctime(), 'No frame')
        time.sleep(5.0)
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.cam = cv2.VideoCapture(self.src,
                                cv2.CAP_FFMPEG)
        continue
      
      h = dhash(img, hashSize=3)
      d = hamming(h, h_old)
##      if  d > 6:
##        save_img(img)
      h_old = h
      with self.lock:
        self.img = img
      
      i += 1
      if i == mx:
        i = 0
        fps = mx / (time.time() - t)
        t = time.time()
        print('Camera quality = {} FPS = {}'.format(int(camera_quality(img)),
                                                    fps))
   
  def start(self):
    c = threading.Thread(target=self.process, args=())
    c.start()


def image_processing():
  global c
  while True:
    img = c.get_img()
    if img is None:
      time.sleep(0.1)
      continue
    img = functions.make_beautiful_size(img)
    c.img_to_img2(img)

if __name__ == '__main__':
  import time
  c = Camera()
  c.start()
  threading.Thread(target=image_processing, args=()).start()
  app.run(host='0.0.0.0', port=58800, debug=False, threaded=True, use_reloader=False)

