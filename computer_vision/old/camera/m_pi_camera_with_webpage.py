import cv2
import numpy as np
import time
import socketserver
import requests
import io
from threading import Condition
import threading
from multiprocessing import Process, Value, Queue
import picamera
from http import server

main_frame = None
lock = threading.Lock()

PAGE="""\
<html>
<head>
<title>RPI camera</title>
</head>
<body>
<center><h1>Test camera</h1></center>
<center><img src="stream.mjpg" width=90% ></center>
</body>
</html>
"""

def web_set(img):
  global main_frame, lock
  with lock:
    main_frame = img.copy()

class StreamingHandler(server.BaseHTTPRequestHandler):
    global main_frame, lock
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
              while True:
                with lock:
                  frame = main_frame.copy()
                ret, jpeg = cv2.imencode('.jpg', frame)
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(jpeg))
                self.end_headers()
                self.wfile.write(jpeg)
                self.wfile.write(b'\r\n')
         
            except Exception as e:
                print(str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class Server():
  def __init__(self, ip='', port=8080):
    self.address = (ip, port)

  def start(self):    
    self.p = threading.Thread(target=self.process, args=()).start()

  def process(self):
    server = StreamingServer(self.address, StreamingHandler)
    server.serve_forever()


class Camera():
  def __init__(self, resolution=(640, 480), framerate=90,
               mode='auto', white_balance='auto',
               effect='none',
               show_fps=False):
    self.resolution = resolution
    self.framerate = framerate
    self.show_fps = show_fps

    self.image = None
    self.mode = mode
    self.white_balance = white_balance
    self.effect = effect

  def start(self):
    self.p = threading.Thread(target=self.process, args=()).start()

  def process(self):
    global main_frame, lock
    with picamera.PiCamera(resolution=self.resolution,
                           framerate=self.framerate) as camera:
      output = StreamingOutput()
      camera.start_recording(output, format='mjpeg')
      camera.exposure_mode = self.mode
      camera.awb_mode = self.white_balance
      camera.image_effect = self.effect

      t = time.time()

      while True:
        with output.condition:
          output.condition.wait()
          frame = output.frame

        try:
          img = cv2.imdecode(np.frombuffer(frame, np.uint8), 1)
        except:
          continue

        h, w = img.shape[:2]
        self.image = img.reshape((h, w, 3))   

        if self.show_fps:
          print(1 / (time.time() - t))
          t = time.time()

  def get(self):
    with lock:
      if self.image is None:
        return None
      else:
        return self.image.copy()

if __name__ == '__main__':
  c = Camera(resolution=(1920, 1080), framerate=30, show_fps=True)
  c.start()
  s = Server()
  s.start()
  
  while True:
    img = c.get()
    if img is None:
      print('empty')
      continue

    web_set(img)
