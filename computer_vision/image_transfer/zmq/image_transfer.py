import threading
import time
import zmq
import numpy as np
import cv2
import pickle


def server_thread():
  global frame_tmp, lock

  context = zmq.Context()
  socket = context.socket(zmq.REP)
  socket.RCVTIMEO = 5000
  socket.bind("tcp://0.0.0.0:{}".format(5003))

  print('Server is ready')

  while True:
    try:
      msg = socket.recv().decode() 
    except Exception as e:
      print(e)
      print('{} No connection'.format(time.ctime()))
      time.sleep(0.1)
      continue
    
    with lock:
      img = frame_tmp.copy()

    msg = pickle.dumps(img)
    socket.send(msg, zmq.NOBLOCK)

      
def main_thread():
  global frame_tmp, lock
  while True:
    frame = cv2.imread('{}{}'.format(FOLDER_PATH, IMG_NAME))

    cv2.putText(frame, str(time.time()),
                (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.6,
                (0, 0, 255), 2)
    
    with lock:
      frame_tmp = frame.copy()




if __name__ == '__main__':
  FOLDER_PATH = '../../data/'
  IMG_NAME = 'sample.jpg'
  lock = threading.Lock()

  frame_tmp = None
  
  threading.Thread(target=main_thread, args=()).start()
  threading.Thread(target=server_thread, args=()).start()
