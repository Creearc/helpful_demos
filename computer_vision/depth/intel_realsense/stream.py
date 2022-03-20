import pyrealsense2.pyrealsense2 as rs
from multiprocessing import Process, Queue, Value
import numpy as np
import cv2
import time
import imutils
import os

from flask import Response
from flask import Flask
from flask import render_template
from flask import request

def save_img(img):
  path = 'out/'
  t = time.time()
  cv2.imwrite('{}{}.png'.format(path, t), img)

  print('Saved {}.png'.format(t))

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
  global save, obj_class
  if request.method == 'POST':
    save.value = 1
  return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")

def generate():
  global img_q, save
  frame = None
  while True:
    if not img_q.empty():
      frame = img_q.get_nowait()
    if frame is None: continue
    (flag, encodedImage) = cv2.imencode(".jpg", frame)
    if not flag:
      continue   
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
          bytearray(encodedImage) + b'\r\n')

def capture():
  global img_q, save
  w, h = 640, 480

  # Configure depth and color streams
  pipeline = rs.pipeline()
  config = rs.config()
  config.enable_stream(rs.stream.depth, w, h, rs.format.z16, 30)
  config.enable_stream(rs.stream.color, w, h, rs.format.bgr8, 30)
  
  # Start streaming
  profile = pipeline.start(config)

  # Getting the depth sensor's depth scale (see rs-align example for explanation)
  depth_sensor = profile.get_device().first_depth_sensor()
  depth_scale = depth_sensor.get_depth_scale()
  print("Depth Scale is: " , depth_scale)

  # We will be removing the background of objects more than
  #  clipping_distance_in_meters meters away
  clipping_distance_in_meters = 1 #1 meter
  clipping_distance = clipping_distance_in_meters / depth_scale

  # Create an align object
  # rs.align allows us to perform alignment of depth frames to others frames
  # The "align_to" is the stream type to which we plan to align depth frames.
  align_to = rs.stream.color
  align = rs.align(align_to)

  thr = 150
  l = 10
  while True:
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)

    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
        
    if not aligned_depth_frame or not color_frame:
      continue

    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    grey_color = 153

    out = np.zeros((h, w, 4),np.uint8)
    
    depth_image_3d = np.dstack((depth_image,depth_image,depth_image))
    out[:,:,:3] = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), 0, color_image)
    out[:,:,3] = np.where((depth_image > clipping_distance) | (depth_image <= 0), 0, 255)
    
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    
    images = np.hstack((color_image, depth_colormap, out[:,:,:3]))
    
    if not img_q.full():
      img_q.put_nowait(images)

    if save.value == 1:
      save_img(out)
      save.value = 0

img_q = Queue(1)
save = Value('i', 0)
p = Process(target=capture, args=())
p.start()
while img_q.empty():
  time.sleep(0.001)

app.run(host="0.0.0.0", port=8000, debug=True,
        threaded=True, use_reloader=False)
