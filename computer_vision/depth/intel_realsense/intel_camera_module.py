import pyrealsense2.pyrealsense2 as rs
import threading
import numpy as np
import cv2
import time
import imutils
import os


class RealsenseCamera:
    def __init__(self,
                 w=640, h=480,
                 debug=False):

        self.w = w
        self.h = h
        
        self.lock = threading.Lock()
        self.debug = debug
        self.depth_image = None
        self.color_image =None
        self.stop = False

        # Configure depth and color streams
        pipeline = rs.pipeline()
        config = rs.config()

        config.enable_stream(rs.stream.depth,
                             self.w, self.h, rs.format.z16, 30)
        config.enable_stream(rs.stream.color,
                             self.w, self.h, rs.format.bgr8, 30)        
        print('[RealsenseCamera] Ready')


    def get_img(self):
        with self.lock:
            return [self.color_image, depth_image]

    def process(self):
        # Start streaming
        profile = pipeline.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print("[RealsenseCamera] Depth Scale is: " , depth_scale)

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        align_to = rs.stream.color
        align = rs.align(align_to)

        while not self.stop:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not aligned_depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            with self.lock:
                self.depth_image = depth_image.copy()
                self.color_image = color_image.copy()
      


    def start(self):
        self.c = threading.Thread(target=self.process, args=())
        self.c.start()

        
