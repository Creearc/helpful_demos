import threading
import time
import zmq
import numpy as np
import cv2
import pickle


class ZMQ_receiver:
  def __init__(self, ip='127.0.0.1', port=5003):
    self.ip = ip
    self.port = port

    self.img = None
    self.lock = threading.Lock()

  def connect(self):
    context = zmq.Context()
    self.socket = context.socket(zmq.REQ)
    self.socket.RCVTIMEO = 1000
    self.socket.connect("tcp://{}:{}".format(self.ip, self.port))

  def run(self):
    threading.Thread(target=self.zmq_thread, args=()).start()

  def zmq_thread(self):
    self.connect()

    print('[ZMQ receiver] Server is ready')

    while True:    
      try:
        self.socket.send_string('image', zmq.NOBLOCK)
        msg = self.socket.recv() 
      except Exception as e:
        print(e)
        print('[ZMQ receiver] No connection')
        self.connect()
        time.sleep(0.1)
        continue
      
      img = pickle.loads(msg)
      if img is None:
        continue
      
      with self.lock:
        self.img = img.copy()

  def get_img(self):
    with self.lock:
      img = self.img
    return img
    

class ZMQ_transfer:
  def __init__(self, ip='0.0.0.0', port=5003):
    self.ip = ip
    self.port = port

    self.img = None
    self.lock = threading.Lock()

  def bind(self):
    context = zmq.Context()
    self.socket = context.socket(zmq.REP)
    self.socket.RCVTIMEO = 1000
    self.socket.bind("tcp://{}:{}".format(self.ip, self.port))

  def run(self):
    threading.Thread(target=self.zmq_thread, args=()).start()

  def zmq_thread(self):
    self.bind()

    print('[ZMQ transfer] Server is ready')

    while True:
      try:
        msg = self.socket.recv().decode() 
      except Exception as e:
        print(e)
        print('[ZMQ transfer] No connection')
        time.sleep(0.1)
        continue
      
      with self.lock:
        img = self.img

      msg = pickle.dumps(img)
      self.socket.send(msg, zmq.NOBLOCK)

  def put_img(self, img):
    with self.lock:
      if not (img is None):
        self.img = img.copy()
      else:
        print('[ZMQ transfer] Img is None')


if __name__ == '__main__':
  FOLDER_PATH = '../../data/'
  IMG_NAME = 'sample.jpg'

  serv = ZMQ_transfer()
  serv.run()

  rec = ZMQ_receiver()
  rec.run()
  
  
  def show_thread():
    while True:    
      frame = rec.get_img()

      if frame is None:
        time.sleep(0.4)
        continue

      cv2.imshow('', frame)
      cv2.waitKey(1)

  def read_imgs_thread():
    while True:
      frame = cv2.imread('{}{}'.format(FOLDER_PATH, IMG_NAME))

      cv2.putText(frame, str(time.time()),
                  (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.6,
                  (0, 0, 255), 2)
      
      serv.put_img(frame)

  threading.Thread(target=show_thread, args=()).start()
  threading.Thread(target=read_imgs_thread, args=()).start()
