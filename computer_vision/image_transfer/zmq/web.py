import threading
import time

import numpy as np
import cv2

from flask import Response
from flask import Flask
from flask import render_template

import zmq_module

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")


@app.route("/video_feed")
def video_feed():
  return Response(generate(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")

def generate():
  while True:
    img = rec.get_img()
    if img is None:
      time.sleep(0.1)
      continue
    (flag, encodedImage) = cv2.imencode(".jpg", img)
    if not flag:
      time.sleep(0.1)
      continue
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')


if __name__ == '__main__':
  rec = zmq_module.ZMQ_receiver('192.168.68.205', 5005)
  rec.run()
  
  app.run(host='0.0.0.0', port=58800, debug=False, threaded=True, use_reloader=False)
