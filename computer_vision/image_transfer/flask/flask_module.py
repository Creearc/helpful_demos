import time
import threading

import numpy as np
import cv2
import imutils

from flask import Response
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def index():
  return """
<html>
  <head>
    <title>Camera</title>
  </head>
  <body>
    <h1>Camera</h1>
    <img src="{{ url_for('video_feed') }}">
  </body>
</html>
"""

@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")


def generate():
  global lock, img_q, img_s
  frame = None
  while True:
    with lock:
      if not (img_s is None):
        frame = img_s
      else:
        continue
    (flag, encodedImage) = cv2.imencode(".jpg", frame)
    if not flag:
      continue   
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
          bytearray(encodedImage) + b'\r\n')


def camera_watch():
  global lock, img_s
  cap = cv2.VideoCapture(0)
  while True:
    t = time.time()
    
    ret, frame = cap.read()

    with lock:
      if img_s is None:
        img_s = frame.copy()
    #print(1 / (time.time() - t))


img_s = None
lock = threading.Lock()

tr1 = threading.Thread(target=camera_watch, args=())
tr1.start()

app.run(host="0.0.0.0", port=8000, debug=False,
        threaded=True, use_reloader=False)
