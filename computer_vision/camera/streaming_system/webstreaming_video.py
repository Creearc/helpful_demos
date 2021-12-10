import os
import sys
import threading
import argparse
import time
import math

import numpy as np
import cv2
import imutils

import paho.mqtt.client as paho
from paho.mqtt import publish

from flask import Response
from flask import Flask
from flask import render_template

codec = cv2.VideoWriter_fourcc('M','J','P','G')

class WebcamVideoStream:
    def __init__(self, src='/dev/video0'):
        print('Camera %s init...' % src)
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, args["width"])
        self.cap.set(cv2.CAP_PROP_FOURCC, codec)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args["height"])
        self.cap.set(cv2.CAP_PROP_FPS, args["fps"])           
        (self.grabbed, self.frame) = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def get(self, var1):
        self.cap.get(var1)
        
    def start(self):
        if self.started:
            print('[!] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            #s = time.time()
            self.grabbed, self.frame = self.cap.read()
            #print(1/(time.time() - s))

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
        return frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()

def HAAR(image):
  image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  cascade = cv2.CascadeClassifier("face.xml")
  rects = cascade.detectMultiScale(image, scaleFactor=1.1,
                                     minNeighbors=5, minSize=(30, 30),
                                     flags = cv2.CASCADE_SCALE_IMAGE)
                     
  if len(rects) == 0: return []
  rects[:,2:] += rects[:,:2]
  box = []
  for x1, y1, x2, y2 in rects:
     box.append((x1, y1, x2-x1, y2-y1))
  return box


app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")


def send():
    global c, lock
    h, w = args["height"] // args["frame_size"], args["width"] // args["frame_size"]
    if args["is_black"] == 1:
        out = np.zeros((h, w * len(c)), np.uint8)
    else:
        out = np.zeros((h, w * len(c), 3), np.uint8)
    img = None
    print('Streaming started...')
    while True: 
        for i in range(len(c)):
            with lock:
                img = c[i].read()
            if img is None:
                continue
            img = imutils.resize(img, width=w, inter=cv2.INTER_NEAREST)
            if args["is_black"] == 1:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            out[0 : h, w * i : w * (i + 1)] = img
        (flag, encodedImage) = cv2.imencode(".jpg", out)
        if not flag:
            continue
        publish.multiple([{'topic': IP, 'payload': bytearray(encodedImage)}], hostname=BROKER, port=PORT)

def generate():
    global c, lock
    h, w = args["height"] // args["frame_size"], args["width"] // args["frame_size"]
    if args["is_black"] == 1:
        out = np.zeros((h, w * len(c)), np.uint8)
    else:
        out = np.zeros((h, w * len(c), 3), np.uint8)
    img = None
    while True:
        for i in range(len(c)):
            with lock:
                img = c[i].read()    
            if img is None:
                continue
            img = cv2.flip(img, 0)
            if args["method"] == 'HAAR':
                
                boxes = HAAR(img)
                for box in boxes:
                    (xs, ys, ws, hs) = [int(vs) for vs in box]
                    
                    py = D(hs + ys)
                    px = Dx(xs + ws / 2, py, hs + ys)
                    
                    cv2.rectangle(img, (xs, ys), (xs + ws, ys + hs), (255, 255, 255), 3)
                    cv2.putText(img, str(px)[:5], (xs, ys + 40), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)
                    cv2.putText(img, str(px)[:5], (xs, ys + 40), cv2.FONT_ITALIC, 1, (250, 250, 250), 1)
                    cv2.putText(img, str(py)[:5], (xs, ys + 80), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)
                    cv2.putText(img, str(py)[:5], (xs, ys + 80), cv2.FONT_ITALIC, 1, (250, 250, 250), 1)
            img = imutils.resize(img, width=w, inter=cv2.INTER_NEAREST)
            if args["is_black"] == 1:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            out[0 : h, w * i : w * (i + 1)] = img       
        (flag, encodedImage) = cv2.imencode(".jpg", out)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                bytearray(encodedImage) + b'\r\n')


def record(path):
    global c
    while True:
        l = len(os.listdir(path))
        h, w = args["height"], args["width"]
        video = []
        v = []
        f = []
        for i in range(len(c)):
            v.append(l + i)
            video.append(cv2.VideoWriter(path + str(v[i]) +'.avi', codec, args["quality"], (w, h)))
            print('Recording to ' + path + str(v[i]) +'.avi')
            f.append(0)
        while True:
            for i in range(len(c)):
                with lock:
                    img = c[i].read()
                if img is None:
                    continue
                f[i] += 1
                if f[i] % 1000 == 0:
                    size = os.popen("du " + path + str(v[i]) + '.avi').read().split('\t')[0]
                    print('{}: {}b'.format(i, size))
                    if int(size) > 1900000:
                        break
                video[i].write(img)

		
outputFrame = None
lock = threading.Lock()
out = None
c = []

BROKER = '192.168.9.8'
PORT = 56008

IP = os.popen("""ifconfig eth0 | grep inet | awk '{ print $2 }'""").read().split('\n')[0]
print('My IP is %s' % IP)

F = 5.5 * 300 / 1.75 # Tur
alpha = 0
Hc = 0
Hch = 0

D = lambda x:  - math.tan(alpha - math.atan((args["height"] / 2 - x) / F)) * Hc
Dx = lambda x, d, y: - (args["width"] / 2 - x) * ((Hc ** 2 + d ** 2)
                                                  / ((args["height"] / 2 - y) ** 2 + F ** 2)) ** 0.5 

def found_cameras(c):
    print("Searching for cameras...")
    out = os.popen("v4l2-ctl --list-devices").read().split('\n')
    for i in range(len(out)):
        if out[i].find('CAMERA') != -1 or out[i].find('Camera') != -1:
            camera = out[i + 1].strip()
            print('Camera %s founded' % camera)
            c.append(WebcamVideoStream(camera).start())
            if len(c) == args["cameras"]:
              break
    print('All cameras connected.')

        

if __name__ == '__main__':
        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--ip", type=str, default='0.0.0.0',
                        help="ip address of the device")
        ap.add_argument("-p", "--port", type=int, default=8000,
                        help="ephemeral port number of the server (1024 to 65535)")
        ap.add_argument("-s", "--frame_size", type=int, default=1)
        ap.add_argument("-b", "--is_black", type=int, default=1)
        ap.add_argument("-q", "--quality", type=float, default=90.0)
        ap.add_argument("-w", "--width", type=int, default=1280)
        ap.add_argument("-u", "--height", type=int, default=720)
        ap.add_argument("-f", "--fps", type=int, default=20)
        ap.add_argument("-c", "--cameras", type=int, default=1)
        ap.add_argument("-v", "--record", type=int, default=0)
        ap.add_argument("-m", "--mqtt", type=int, default=0)
        ap.add_argument("-M", "--method", type=str, default=None)
        ap.add_argument("-a", "--angle", default = 125.0, type = float,
                        help = "angle between camera and verticake axe")
        ap.add_argument("-H", "--camera_hight", default = 3.0, type = float,
                        help = "hight of camera position")
        ap.add_argument("-o", "--object_hight", default = 1.75, type = float,
                        help = "hight of objects")
        args = vars(ap.parse_args())

        found_cameras(c)

        if args["method"] is not None:
          alpha = args["angle"] * 3.14 / 180
          Hc = args["camera_hight"]
          Hch = args["object_hight"]

        if args["record"] > 0:
            out = os.popen("ls /media/usb1/").read().split('\n')
            if len(out) == 1:
              path = 'Video/'
            else:
              path = '/media/usb1/Video/'
            tr = threading.Thread(target=record, args=(path, ))
            tr.start()

        if args["mqtt"] == 1:
            tr1 = threading.Thread(target=send, args=())
            tr1.start()
        else:
            app.run(host=args["ip"], port=args["port"], debug=False, threaded=True, use_reloader=False)
        
            
            
        
            
        
