
import cv2
import numpy as np
import time

import threading
from threading import Condition
from multiprocessing import Process, Value, Queue

import io
import picamera

import zmq_module


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

class Camera():
    def __init__(self,
                 resolution=(640, 480),
                 framerate=90,
                 mode='auto',
                 white_balance='auto',
                 effect='none',
                 multiprocessing=False,
                 show_fps=False):

        self.resolution = resolution
        self.framerate = framerate
        self.show_fps = show_fps

        self.image = None
        self.mode = mode
        self.white_balance = white_balance
        self.effect = effect

        self.multiprocessing = multiprocessing
        self.stop = False

        if not self.multiprocessing:
            import threading
            from threading import Condition
            self.lock = threading.Lock()

        else:
            from multiprocessing import Process, Value, Queue
            self.image_q = Queue(1)

    def start(self):
        if not self.multiprocessing:
            self.c = threading.Thread(target=self.process, args=())
            self.c.start()
        else:
            self.c = Process(target=self.process, args=())
            self.c.start()

    def stop(self):
        self.stop = True


    def process(self):
        with picamera.PiCamera(resolution=self.resolution,
                               framerate=self.framerate) as camera:
            output = StreamingOutput()
            camera.start_recording(output, format='mjpeg')
            camera.exposure_mode = self.mode
            camera.awb_mode = self.white_balance
            camera.image_effect = self.effect

            t = time.time()

            while True:
                if self.stop:
                    break

                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                try:

                    img = cv2.imdecode(np.frombuffer(frame, np.uint8), 1)
                except:
                    print('\033[31m[RPI Camera] Frame decode error\033[0m')
                    time.sleep(0.1)
                    continue

                h, w = img.shape[:2]
                img = img.reshape((h, w, 3))

                if not self.multiprocessing:
                    with self.lock:
                        self.image = img.copy()
                else:
                    if not self.image_q.full():
                        self.image_q.put_nowait(img.copy())

                if self.show_fps:
                    print('\033[34m[RPI Camera] FPS: {}\033[0m'.format(1 / (time.time() - t)))
                    t = time.time()


    def get_img(self):
        if not self.multiprocessing:
            with self.lock:
                return self.image
        else:
            if not self.depth_q.empty():
                return self.image_q.get_nowait()


if __name__ == '__main__':
    c = Camera(resolution=(3840, 2160), framerate=30, show_fps=False)
    c.start()

    codec = cv2.VideoWriter_fourcc('m', 'j', 'p', 'g')
    vid_out = cv2.VideoWriter('{}.avi'.format(str(time.ctime()).replace(':', '_')),
                              codec, 25,
                             (1920, 1080))

    serv = zmq_module.ZMQ_transfer()
    serv.run()
    
    while True:
        img = c.get_img()
        if img is None:
            print('empty')
            continue
        else:
            print(img.shape)
            img_fhd = cv2.resize(img, (1920, 1080), interpolation = cv2.INTER_AREA)
            vid_out.write(img_fhd)
            serv.put_img(img_fhd)
