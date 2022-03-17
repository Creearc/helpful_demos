import threading
import time
import zmq
import numpy as np
import cv2
import pickle


def server_thread():
  global frame_tmp, lock

  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.RCVTIMEO = 5000
  socket.connect("tcp://127.0.0.1:{}".format(5003))

  print('Server is ready')

  while True:    
    try:
      socket.send_string('1', zmq.NOBLOCK)
      msg = socket.recv() 
    except Exception as e:
      print(e)
      print('No connection')
      context = zmq.Context()
      socket = context.socket(zmq.REQ)
      socket.RCVTIMEO = 5000
      socket.connect("tcp://127.0.0.1:{}".format(5003))
      time.sleep(0.1)
      continue
    
    img = pickle.loads(msg)
    with lock:
      frame_tmp = img.copy()


def main_thread():
  global  frame_tmp, lock
  while True:    
    with lock:
      frame = frame_tmp

    if frame is None:
      time.sleep(0.4)
      continue

    cv2.imshow('', frame)
    cv2.waitKey(1)



if __name__ == '__main__':
  FOLDER_PATH = '../../data/'
  IMG_NAME = 'sample.jpg'
  lock = threading.Lock()

  frame_tmp = None
  
  threading.Thread(target=main_thread, args=()).start()
  threading.Thread(target=server_thread, args=()).start()
