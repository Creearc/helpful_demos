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
    rec = ZMQ_receiver(ip='10.12.37.133',
                       port=5005)
    rec.run()
    
    
    def show_thread():
        while True:    
            frame = rec.get_img()

            if frame is None:
                time.sleep(0.4)
                continue

            cv2.imshow('', frame)
            cv2.waitKey(1)
            


    threading.Thread(target=show_thread, args=()).start()
