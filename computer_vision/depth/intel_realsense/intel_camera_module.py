import pyrealsense2.pyrealsense2 as rs
import threading
from multiprocessing import Process, Queue, Value
import numpy as np
import cv2
import time
import imutils
import os


class RealsenseCamera:
    def __init__(self,
                 w=640, h=480,
                 multiproc=False,
                 debug=False):

        self.debug = debug

        self.w = w
        self.h = h

        self.depth_image = None
        self.color_image = None
        self.stop = False

        self.multiprocessing = multiproc

        if not self.multiprocessing:      
            self.lock = threading.Lock()
            
        else:
            self.depth_q = Queue(1)
            self.color_q = Queue(1)

        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.config.enable_stream(rs.stream.depth,
                             self.w, self.h, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color,
                             self.w, self.h, rs.format.bgr8, 30)        
        print('[RealsenseCamera] Ready')


    def get_img(self):
        if not self.multiprocessing:
            with self.lock:
                return [self.color_image, self.depth_image]
        else:
            if not self.depth_q.empty(): 
                self.depth_image = self.depth_q.get_nowait()
            if not self.color_q.empty():
                self.color_image = self.color_q.get_nowait()
            return [self.color_image, self.depth_image]

    def process(self):
        # Start streaming
        profile = self.pipeline.start(self.config)

        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print("[RealsenseCamera] Depth Scale is: " , depth_scale)

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        align_to = rs.stream.color
        align = rs.align(align_to)

        while not self.stop:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not aligned_depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            if not self.multiprocessing:
                with self.lock:
                    self.depth_image = depth_image.copy()
                    self.color_image = color_image.copy()
            else:
                if not self.depth_q.full():
                    self.depth_q.put_nowait(depth_image.copy())
                if not self.color_q.full():
                    self.color_q.put_nowait(color_image.copy())
      


    def start(self):
        if not self.multiprocessing:
            self.c = threading.Thread(target=self.process, args=())
            self.c.start()
        else:
            self.c = Process(target=self.process, args=())
            self.c.start()

        
