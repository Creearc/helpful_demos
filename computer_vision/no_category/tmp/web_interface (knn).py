import sys
import os
import threading
import multiprocessing as mp
import time
import pickle
import numpy as np
import cv2
import imutils
from http import server
import socketserver

CLUSTERS_PATH = 'clusters'

PAGE = """\
<html>
<head>
<title>Eyes</title>
</head>
<body>
<center><h1>Clusters</h1></center>
<center><img src="stream.mjpg" width=100% ></center>
</body>
</html>
"""


class Server():
  def __init__(self, ip='', port=8080):
    self.address = (ip, port)

  def start(self):    
    self.p = threading.Thread(target=self.process, args=()).start()

  def process(self):
    server = StreamingServer(self.address, StreamingHandler)
    server.serve_forever()
    

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

    

def load(file):
  try:
    with open(file, 'rb') as f:
      data = pickle.load(f)
    return data
  except:
    print('Error while opening {} file'.format(file))

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

def matchKeyPointsKNN(featuresA, featuresB, ratio):
  rawMatches = bf.knnMatch(featuresA, featuresB, 2)
  matches = []

  for m,n in rawMatches:
    if m.distance < n.distance * ratio:
        matches.append(m)
  return matches

def getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh):
    ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
    ptsB = np.float32([kpsB[m.trainIdx] for m in matches])
  
    (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
        reprojThresh)

    return (H, status)
  
def combine_arr2(arr):
  middle = arr[len(arr) // 2]
  orig = middle[2]
  result = np.zeros((orig.shape[0] * 3, orig.shape[1] * 3, 3), np.uint8)
  result_eye = np.zeros((orig.shape[0] * 3, orig.shape[1] * 3, 3), np.uint8)

  radius = 25
  color = 35
  thickness = -1
  
  for i in range(len(arr)):
    if i == len(arr) // 2:
      continue
    img = arr[i][2]
    img_eye = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    cv2.circle(img_eye, arr[i][3], radius, color, thickness)

    matches = matchKeyPointsKNN(arr[i][1], middle[1], ratio=0.75)

    M = getHomography(arr[i][0], middle[0], arr[i][1], middle[1], matches, reprojThresh=4)
    (H, status) = M

    width = orig.shape[1] + img.shape[1]
    height = orig.shape[0] + img.shape[0]

    tmp = cv2.warpPerspective(img, H, (width, height))
    img_eye = cv2.warpPerspective(img_eye, H, (width, height))
    gray = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
    mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

    tmp_0 = result[orig.shape[0]:orig.shape[0]+height,
                   orig.shape[1]:orig.shape[1]+width,:3]

    tmp = cv2.bitwise_and(tmp, tmp, mask=mask)
    tmp_0 = cv2.bitwise_and(tmp_0, tmp_0, mask=cv2.bitwise_not(mask))
        
    result[orig.shape[0]:orig.shape[0]+height,
           orig.shape[1]:orig.shape[1]+width] = cv2.add(tmp_0, tmp)

    result_eye[orig.shape[0]:orig.shape[0]+height,
               orig.shape[1]:orig.shape[1]+width,2] += img_eye
    result_eye = np.where((result_eye > 200), 200, result_eye)

  result[orig.shape[0]:orig.shape[0]*2, orig.shape[1]:orig.shape[1]*2] = orig

  img_eye = np.zeros((orig.shape[0], orig.shape[1]), np.uint8)
  cv2.circle(img_eye, middle[3], radius, color, thickness)
  result_eye[orig.shape[0]:orig.shape[0]*2, orig.shape[1]:orig.shape[1]*2, 2] += img_eye
  result_eye = cv2.blur(result_eye, (9, 9))

  result = cv2.add(result_eye, result)
  result = np.where((result_eye == 0), result//2, result)
     
  gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
  thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)

  c = max(cnts, key=cv2.contourArea)
  (x, y, w, h) = cv2.boundingRect(c)
  result = result[y:y + h, x:x + w, :]
  
  return result

def plitka(imgs, x, y, size):
  global main_frame, lock
  for i in range(y):
    for j in range(x):
      if i * x + j < len(imgs):
        if imgs[i * x + j] is None:
          continue
        with lock:
          main_frame[i * size[1] : (i + 1) * size[1],
              j * size[0] : (j + 1) * size[0]] = imgs[i * x + j]

def make_cluster_img():
  global images, lock, size
  old_len = []
  while True:
    with lock:
      ln = len(images)
      
    for index in range(ln):
      old_len.extend([[] for i in range(ln - len(old_len))])
        
      if '{}.cl'.format(index) in os.listdir(CLUSTERS_PATH):      
        data = load('{}/{}.cl'.format(CLUSTERS_PATH, index))
        if data is None:
          continue
        if data == []:
          print('{}/{}.cl no data'.format(CLUSTERS_PATH, index))
          return
        if len(data) == old_len[index]: 
          with lock:
            images[index] = None
          continue

        old_len[index] = len(data)
        result = combine_arr2(data)
        result = cv2.resize(result, size)
        with lock:
          images[index] = result.copy()
        print('Index {}, data count {}'.format(index, len(data)))
    
size = (300, 150)
images = []
main_frame = np.zeros((size[1] * 20, size[0] * 5, 3), np.uint8)
lock = threading.Lock()
     
if __name__ == '__main__':
  clusters = 0
  
  server_obj = Server()
  server_obj.start()

  threading.Thread(target=make_cluster_img, args=()).start()
  
  while True:
    ln = len(os.listdir(CLUSTERS_PATH))
    if clusters != ln:
      with lock:
        images = [None for i in range(ln)]
      clusters = ln

    with lock:
      out = images.copy()
    plitka(out, 5, 20, size)



