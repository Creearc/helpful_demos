import threading
import time
import zmq
import numpy as np
import cv2

import pickle

from flask import Response
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")


@app.route("/video_feed")
def video_feed():
  return Response(generate(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")

def generate():
  global socket
  while True:
    try:
      msg = socket.recv()
    except Exception as e:
      print('No connection')
      time.sleep(0.1)
      continue
    socket.send_string('1', zmq.NOBLOCK)
    
    img = pickle.loads(msg)
    if img is None:
      time.sleep(0.1)
      continue
    (flag, encodedImage) = cv2.imencode(".jpg", img)
    if not flag:
      time.sleep(0.1)
      continue
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

def main_thread():
  while True:
    pass


if __name__ == '__main__':
  lock = threading.Lock()

  img = None

  ip = '0.0.0.0'

  context = zmq.Context()
  socket = context.socket(zmq.REP)
  socket.RCVTIMEO = 1000
  socket.connect("tcp://{}:{}".format(ip, 5001))
  
  app.run(host='0.0.0.0', port=58800, debug=False, threaded=True, use_reloader=False)
