import threading
from multiprocessing import Process, Value, Queue
from flask import Flask, render_template, Response
import sys
import numpy as np
import cv2
import imutils
import time

import test_camera as camera
from yolo import nn as yolo
import test_move_detector as move_detector
import test_knife as knife

MARKERS = [(273, 733), (364, 58),
                         (1601, 72), (1676, 761)]

FAKE_LINE = [(0, 253), (1919, 253+36)]

SHPON_REGION = (17, 70, 1891, 665)
SHPON_REGION_COORDS = [(SHPON_REGION[0], SHPON_REGION[1]),
                                                 (SHPON_REGION[0] + SHPON_REGION[2],
                                                    SHPON_REGION[1] + SHPON_REGION[3])]
SHPON_REGION_CENTER = (SHPON_REGION_COORDS[0][0] + SHPON_REGION_COORDS[1][0]) // 2
SHPON_TEMPLATE = np.zeros((SHPON_REGION[3] * 3, SHPON_REGION[2], 3), np.uint8)

KNIFE_REGION = (280, 890, 40, 10)

W, H = 1920, 1080

lock = threading.Lock()

def hamming(a, b):
    return bin(int(a) ^ int(b)).count("1")

def dhash(img, hashSize=3):
    img = cv2.resize(img, (hashSize, img.shape[0]))
    img = cv2.blur(img, (3, 3))
    diff = img[:, 1:] > img[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def draw_points(frame, points):
    font = cv2.FONT_HERSHEY_SIMPLEX 
    for i in range(len(points)):
        cv2.circle(frame,(points[i][0], points[i][1]), 3, (0,0,255), -1)
        cv2.putText(frame, str(i + 1), (points[i][0], points[i][1]), font,
                                0.8, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, str(i + 1), (points[i][0], points[i][1]), font,
                                0.8, (255, 255, 255), 1, cv2.LINE_AA)
    return frame

def extract_shpon_part(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

    kernel = np.ones((7, 7), np.uint8)
    gray = cv2.erode(gray, kernel, iterations = 2)
    gray = cv2.dilate(gray ,kernel, iterations = 2)

    gray = cv2.GaussianBlur(gray,(7, 7), 0)

    edges = cv2.Canny(gray, 100, 150, apertureSize = 3)
    #cv2.imshow("epart", edges)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 1, np.array([]),
                                                    100, 50)
    if not(lines is None):
        for line in lines:
            [[x1, y1, x2, y2]] = line
            cv2.line(gray,(x1, y1), (x2, y2), 50, 2)
            

    #cv2.imshow("gpart", gray)

    gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)

    gray[y : y + h, x : x + w] = 255

    out = cv2.bitwise_and(frame, frame, mask=gray).astype(np.uint8)
    out = out[y : y + h, :] 
    return out

def change_perspective(frame, w, h, markers):
    rect = np.array(markers, dtype = "float32")
    x_min = min(markers[0][0], markers[1][0]) 
    x_max = max(markers[2][0], markers[3][0]) 
    y_min = min(markers[0][1], markers[3][1]) 
    y_max = max(markers[1][1], markers[2][1]) 
    dst = np.array([(x_min, y_min), (x_min, y_max),
                                    (x_max, y_max), (x_max, y_min)],
                                     dtype = "float32")
    
    M = cv2.getPerspectiveTransform(rect, dst)
    frame = cv2.warpPerspective(frame, M, (w, h))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)
    result = frame[y : y + h, x : x + w, :]  
    return result

def img_perspective_plus_fake_lines(img):
    img = change_perspective(img, W, H, MARKERS)

    cv2.rectangle(img, FAKE_LINE[0], FAKE_LINE[1],
                                (255, 255, 255), -1)
    cv2.rectangle(img, FAKE_LINE[0],
                                (400, FAKE_LINE[1][1]),
                                (0, 0, 0), -1)
    cv2.rectangle(img, (FAKE_LINE[1][0] - 400, FAKE_LINE[0][1]),
                                FAKE_LINE[1],
                                (0, 0, 0), -1)

    cv2.rectangle(img, (KNIFE_REGION[0], KNIFE_REGION[1]),
                                    (KNIFE_REGION[0] + KNIFE_REGION[2],
                                     KNIFE_REGION[1] + KNIFE_REGION[3]),
                                    (0, 0, 255),
                                    1)
    return img

def cals_sizes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)
    frame = frame[y:y + h, x:x + w, :]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

    #kernel = np.ones((5,5), np.uint8)
    #gray = cv2.erode(gray, kernel, iterations = 2)

    #cv2.imshow("part", frame)
    #cv2.imshow("gpart", gray)
    return frame

def img_function(img, out, pos, d0):
    global c, y
    step = 10
    #img = c.get_img().copy()
    #img = img_perspective_plus_fake_lines(img)

    part = extract_shpon_part(img[SHPON_REGION_COORDS[0][1]: SHPON_REGION_COORDS[1][1],
                                                                SHPON_REGION_COORDS[0][0]: SHPON_REGION_COORDS[1][0]])

    mn, ind = -1, 0
    if not(d0 is None):
        for i in range(part.shape[0] // step):
            d = dhash(part[i * step : (i + 1) * step, : ], hashSize=100)
            ham = hamming(d, d0)
            if mn == -1 or mn > ham:
                mn = ham
                ind = i

        #print(mn, ind, H)
        disp = part.shape[0] - ind * step
        out[pos - step : pos - step + (part.shape[0] - ind * step), :] = part[ind * step : , :]
    else:
        disp = part.shape[0]
        out[0 : part.shape[0], 0 : part.shape[1]] = part[:,:]
        
    d0 = dhash(part[-step : -1, : ], hashSize=100)
    pos += disp
    if pos + part.shape[0] > out.shape[0]:
            pos = 0

    y.put_img(out)
    return out, pos, d0


def stop_line():
    pass

def calc_sizes():
    pass

def main_thread():
    global c, y, full_image, orig_image
    md = move_detector.MoveDetector()
    kn = knife.Knife()
    out = SHPON_TEMPLATE.copy()
    pos = 0
    d0 = None
    while True:
        img = c.get_img()
        img = img_perspective_plus_fake_lines(img)
        if not orig_image.full():
                orig_image.put(img)
                
        #y.put_img(img)
        md.frame = img.copy()[SHPON_REGION_COORDS[1][1] - 100 : SHPON_REGION_COORDS[1][1],
                                                    SHPON_REGION_CENTER + 50 : SHPON_REGION_CENTER + 150] #####
        if md.is_shpon_not_moving():
            print('Shpon is not moving')
            out, pos, d0 = img_function(img, out, pos, d0)
        kn.frame = img.copy()[KNIFE_REGION[1] : KNIFE_REGION[1] + KNIFE_REGION[3],
                                                    KNIFE_REGION[0] : KNIFE_REGION[0] + KNIFE_REGION[2]] #####
        #if not(kn.frame is None): y.put_img(kn.frame)
        if kn.is_knife_moving():
            print('Knife detected')
            time.sleep(1.0)
            stop_line()
            #out, pos, d0 = img_function(img, out, pos, d0) #############
            out = cals_sizes(out)
            if not full_image.full():
                full_image.put(out)
            out = SHPON_TEMPLATE.copy()
            pos = 0
            d0 = None
                
def image_comp_thread():
    global y, full_image, orig_image, frame, frame0, lock
    with lock:
        frame0, frame = SHPON_TEMPLATE.copy(), np.hstack([SHPON_TEMPLATE.copy(), SHPON_TEMPLATE.copy()])
    while True:
        result = y.get_result()
        if not(result is None):
            [parts, defects] = result
            print(defects)
            tmp_h, tmp_w = parts.shape[:2]
            with lock:
                frame[0 : tmp_h, 0 : tmp_w] = parts

        if not full_image.empty():
            full_shpon = full_image.get()
            tmp_h, tmp_w = full_shpon.shape[:2]
            tmp_h2, tmp_w2 = frame.shape[:2]
            with lock:
                frame[0 : tmp_h2, 0 : tmp_w2 // 2] = SHPON_TEMPLATE.copy()
                frame[0 : tmp_h, tmp_w2 // 2 : (tmp_w2 // 2) + tmp_w] = full_shpon

        if not orig_image.empty():
            with lock:
                frame0 = orig_image.get()

app = Flask(__name__)

def get_frame():
    global frame, lock
    while True:
        with lock:
            img = frame.copy()
        if img is None:
            time.sleep(0.01)
            continue

        imgencode = cv2.imencode('.jpg', img)[1] 
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'
                b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')

def get_orig_frame():
    global frame0, lock
    while True:
        with lock:
            img = frame0.copy()
        if img is None:
            time.sleep(0.01)
            continue

        imgencode = cv2.imencode('.jpg', img)[1] 
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'
                b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')
        
@app.route("/video_feed")
def video_feed():
    return Response(get_frame(),
                                    mimetype = 'multipart/x-mixed-replace; boundary=frame')

@app.route("/video_feed_orig")
def video_feed_orig():
    return Response(get_orig_frame(),
                                    mimetype = 'multipart/x-mixed-replace; boundary=frame')

@app.route('/computed')
def computed():
    return render_template('computed.html')

@app.route('/')
def index():
    return render_template('index.html')
    

if __name__ == "__main__":
    full_image = Queue(1)
    orig_image = Queue(1)
    frame, frame0 = None, None
    threading.Thread(target=main_thread, args=()).start()
    
    
    c = camera.Camera()
    c.start()
    y = yolo.Yolo()
    y.start()
    
    img_q = np.zeros((10, 10, 3), np.uint8)

    threading.Thread(target=image_comp_thread, args=()).start()
    app.run(host='0.0.0.0', port=8080, debug=not True)
