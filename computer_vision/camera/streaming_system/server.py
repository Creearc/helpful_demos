import os
import sys
import argparse
import time
from flask import Response
from flask import Flask
from flask import render_template
import threading

import cv2
import imutils
import numpy as np

import paho.mqtt.client as paho
from paho.mqtt import publish

BROKER = 'localhost'
PORT = 56008
outputFrame = None
lock = threading.Lock()

timestump = 0

IPS = ['192.168.9.9', '192.168.9.10']
IPS_ids = {}
imgs = []
for i in range(len(IPS)):
  imgs.append(b'')
  IPS_ids[IPS[i]] = i

out = []

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/video1")
def video1():
  return Response(generate(),
                  mimetype = "multipart/x-mixed-replace; boundary=frame")



def generate():
  global out
  while True:
    with lock:
      img = out.copy()
    (flag, encodedImage) = cv2.imencode(".jpg", img)
    if not flag:
      continue
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
          bytearray(encodedImage) + b'\r\n')


def oneframe():
  global imgs, out
  w, h = 1280 * 2, 720
  if args["is_black"] == 1:
    out1 = np.zeros((h * len(imgs), w), np.uint8)
  else:
    out1 = np.zeros((h * len(imgs), w, 3), np.uint8)
  img = None
  font = cv2.FONT_HERSHEY_SIMPLEX
  while True:
    for i in range(len(imgs)):
      with lock:
        img = imgs[i]
      if img == b'':
        continue
      img = np.asarray(bytearray(img), dtype="uint8")
      if args["is_black"] == 1:
        img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
      else:
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
      img = imutils.resize(img, height=h, inter=cv2.INTER_NEAREST)
      h1, w1 = img.shape[:2]
      out1[h * i : h * i + h1, 0 : w1] = img

    cv2.putText(out1, time.ctime(), (50, 50), font, 1, (0, 0, 0), 16)
    cv2.putText(out1, time.ctime(), (50, 50), font, 1, (255, 255, 255), 2)
    with lock:
      out = out1.copy()


def record():
  global out
  path = '/media/linaro/Transcend/Video/'
  while True:
    codec = cv2.VideoWriter_fourcc('M','J','P','G')
    l = len(os.listdir(path))
    h, w = 720*2, 1280*2
    if args["is_black"] == 1:
      video = cv2.VideoWriter(path + str(l) +'.avi', codec, args["quality"], (w, h), 0)
    else:
      video = cv2.VideoWriter(path + str(l) +'.avi', codec, args["quality"], (w, h))
    print('Recording to ' + path + str(l) +'.avi')
    f = 0
    while True:
      with lock:
        img = out.copy()
      
      if img is None or len(img) ==  0:
        continue
      f += 1
      if  f % 1000 == 0:
        size = os.popen("du " + path + str(l) + '.avi').read().split('\t')[0]
        print(size)
        if int(size) > 1700000:
            break
      img = imutils.resize(img, height=h, inter=cv2.INTER_NEAREST)
      video.write(img)


def on_connect(client, userdata, flags, rc):
  print("Connected with result code %s" % str(rc))

def on_message(client, userdata, message):
  global imgs, timestump
  #print('Message from %s' % message.topic)
  with lock:
    imgs[IPS_ids[message.topic]] = message.payload
  timestump = time.time()

def mqtt_thread():
  client = paho.Client(client_id="subscriber-1")
  client.on_connect = on_connect
  client.on_message = on_message
  client.connect(BROKER, PORT, 60)

  for topic in IPS:
    print(topic)
    client.subscribe(topic, qos=0)
  print("Subscribed!")
  
  client.loop_forever()
        
if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument("-i", "--ip", type=str, default='0.0.0.0',
                  help="ip address of the device")
  ap.add_argument("-p", "--port", type=int, default=8000,
                  help="ephemeral port number of the server (1024 to 65535)")
  ap.add_argument("-r", "--row", type=int, default=2)
  ap.add_argument("-q", "--quality", type=float, default=90.0)
  ap.add_argument("-w", "--width", type=int, default=1280)
  ap.add_argument("-u", "--height", type=int, default=720)
  ap.add_argument("-b", "--is_black", type=int, default=1)
  ap.add_argument("-v", "--record", type=int, default=0)
  args = vars(ap.parse_args())
  
  if args["record"] > 0:
    tr = threading.Thread(target=record, args=())
    tr.start()

  tr1 = threading.Thread(target=oneframe, args=())
  tr1.start()
  
  tr2 = threading.Thread(target=mqtt_thread, args=())
  tr2.start()

  print('Server activated!')
  app.run(host=args["ip"], port=args["port"], debug=False,
          threaded=True, use_reloader=False)
  
