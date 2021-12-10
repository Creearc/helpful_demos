import sys
import os
import cv2
import imutils
import numpy as np
import time
from multiprocessing import Process, Value, Queue
import socketserver
from threading import Condition
from http import server

PAGE="""\
<html>
<head>
<title>USB Camera</title>
</head>
<body>
<center><img src="stream.mjpg" width=100% ></center>
</body>
</html>
"""


      

class StreamingHandler(server.BaseHTTPRequestHandler):
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
          frame = c.get_img()
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

class Camera:
  def __init__(self, src=0, WIDTH=1280, HEIGHT=720,
               CODEC=cv2.VideoWriter_fourcc('M','J','P','G')):
    self.src = src
    self.WIDTH = WIDTH
    self.HEIGHT = HEIGHT
    self.CODEC = CODEC

    self.cam = cv2.VideoCapture(self.src)
    self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.WIDTH)
    self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.HEIGHT)
    self.cam.set(cv2.CAP_PROP_FOURCC, self.CODEC)
    self.cam.set(cv2.CAP_PROP_FPS, 25)
    self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    self.img_s = Queue(2)

  def get_img(self):
    while self.img_s.empty():
      pass
    return self.img_s.get()

  def process(self):
    
    while True:
      ret, img = self.cam.read()    
      if not ret:
        continue
      if self.img_s.full():
        self.img_s.get()
      self.img_s.put(img)
   
  def start(self):
    c = Process(target=self.process, args=())
    c.start()



if __name__ == '__main__':
  import time
  c = Camera()
  c.start()
  address = ('', 8000)
  server = StreamingServer(address, StreamingHandler)
  server.serve_forever()

