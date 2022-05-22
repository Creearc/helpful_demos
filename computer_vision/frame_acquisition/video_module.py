import sys
import cv2
import numpy as np
import time


class Video():
    def __init__(self,
                 path,
                 first_frame=0,
                 last_frame=None,
                 step=1,
                 fake_camera=False,
                 infinite=False,
                 multiprocessing=False,
                 show_fps=False):
        
        self.cam = cv2.VideoCapture(path)

        self.frame_count = int(self.cam.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = int(self.cam.get(cv2.CAP_PROP_FPS))
        self.w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.first_frame = first_frame
        self.last_frame = self.frame_count if last_frame is None else last_frame
        self.step = step

        self.image = None
        self.show_fps = show_fps

        self.fake_camera = fake_camera
        self.infinite = infinite

        self.multiprocessing = multiprocessing
        self.close = False

        if fake_camera:
            self.start()
            

    def start(self):
        if not self.multiprocessing:
            import threading
            self.lock = threading.Lock()
            self.c = threading.Thread(target=self.process, args=())
            self.c.start()
        else:
            from multiprocessing import Process, Value, Queue
            self.image_q = Queue(1)
            self.c = Process(target=self.process, args=())
            self.c.start()


    def stop(self):
        self.close = True


    def process(self):
        t = time.time()

        frame_number = self.first_frame
        while frame_number < self.last_frame:
            if self.close:
                break
            
            self.cam.set(1, frame_number)
            ret, img = self.cam.read()
            if not ret:
                print('\033[31m[Video] No Frame\033[0m')
                time.sleep(0.1)
                continue

            print(type(img))

            if not self.multiprocessing:
                with self.lock:
                    self.image = img.copy()
            else:
                if not self.image_q.full():
                    self.image_q.put_nowait(img.copy())

            frame_number += self.step
                    
            if frame_number >= self.last_frame:
                if self.infinite:
                    frame_number = self.first_frame
                else:
                    self.cam.release()

            if self.show_fps:
                print('\033[34m[Video] FPS: {}\033[0m'.format(1 / (time.time() - t)))
                t = time.time()
            
        self.cam.release()
                

    def get_img(self, loop=False):
        if self.fake_camera:
            if not self.multiprocessing:
                with self.lock:
                    return self.image
            else:
                if not self.depth_q.empty(): 
                    return self.image_q.get_nowait()
        else:
            if loop:
                frame_number = self.first_frame
                
                while frame_number < self.last_frame:
                    self.cam.set(1, frame_number)
                    ret, img = self.cam.read()
                    if not ret:
                        print('\033[31m[Video] No Frame\033[0m')
                        time.sleep(0.1)
                        continue

                    yield frame_number, img

                    frame_number += self.step
                    
                    if frame_number >= self.last_frame:
                        if self.infinite:
                            frame_number = self.first_frame
                        else:
                            self.cam.release()        
                    
            else:
                ret, img = self.cam.read()
                return img


if __name__ == '__main__':
    try:
        path = '../data/Run_Pavel_Run1.mp4'
        c = Video(path, fake_camera=False, infinite=True)
        for frame_number, img in c.get_img(loop=True):
            cv2.imshow('img', img)
            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()
        c.stop()

        path = '../data/Run_Pavel_Run1.mp4'
        c = Video(path, fake_camera=True, infinite=True)
        while True:
            img = c.get_img()
            print(type(img))
            if img is None:
                continue
            cv2.imshow('img', img)
            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()
        
    except KeyboardInterrupt:
        sys.exit()
