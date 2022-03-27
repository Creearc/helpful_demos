import os
import random
import cv2
import imutils
from imutils import paths
import numpy as np
import pandas as pd
import time

from multiprocessing import Process, Value, Queue, Pool

def get_contours(img):
    cnts, hierarchy = cv2.findContours(img,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for cnt in cnts:
        rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
        x1 = min(rect[0][0], rect[1][0], rect[2][0], rect[3][0])
        x2 = max(rect[0][0], rect[1][0], rect[2][0], rect[3][0])
        y1 = min(rect[0][1], rect[1][1], rect[2][1], rect[3][1])
        y2 = max(rect[0][1], rect[1][1], rect[2][1], rect[3][1])
        boxes.append(((x1, y1), (x2, y2))) 
    return boxes

def crop_by_countour(img, cnt):
    x1, y1, x2, y2 = cnt[0][0], cnt[0][1], cnt[1][0], cnt[1][1]
    return img[y1 : y2, x1 : x2]

def get_mask(img, thr1=0, thr2=255):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(gray, thr1, 255, cv2.THRESH_BINARY)
    ret, mask2 = cv2.threshold(gray, thr2, 255, cv2.THRESH_BINARY_INV)
    return cv2.bitwise_and(mask, mask2)

def adjust_gamma(img, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(img, table)

def random_img(path):
    l = os.listdir(path)
    ll = l[random.randint(0, len(l) - 1)]
    #print('{}{}'.format(path, ll))
    return cv2.imread('{}{}'.format(path, ll), cv2.IMREAD_UNCHANGED)

def random_size(img, s_min=0.8, s_max=1.3):
    out = imutils.resize(img, width = int(img.shape[1] * random.uniform(s_min, s_max)))
    return out

def random_position(x_l, y_l):
    return random.randint(x_l[0], x_l[1]), random.randint(y_l[0], y_l[1])


def combine_imgs(img1, img2, mask, x, y):
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    x11, x12 = np.clip(x - w2 // 2, 0, w1 - 1), np.clip(x + w2 // 2, 0, w1 - 1)
    y11, y12 = np.clip(y - h2 // 2, 0, h1 - 1), np.clip(y + h2 // 2, 0, h1 - 1)
    x21 = x11 - (x - w2 // 2)
    y21 = y11 - (y - h2 // 2)
    x22 = np.clip(x21 + x12 - x11, 0, w2)
    y22 = np.clip(y21 + y12 - y11, 0, h2)
    out = img1.copy()

    alpha = mask[y21 : y22, x21 : x22].astype(float) / 255
    foreground = cv2.multiply(alpha, img2[y21 : y22, x21 : x22].astype(float))
    background = cv2.multiply(1.0 - alpha, out[y11 : y12, x11 : x12].astype(float))
    out[y11 : y12, x11 : x12] = cv2.add(foreground, background)
    return out

def make_xml(filename, cnt, ext, save_dir, b_size):
    x1, y1, x2, y2 = cnt[0][0], cnt[0][1], cnt[1][0], cnt[1][1]
    with open('template_bbox.xml') as temp:
        tmp = temp.read()
        xml = tmp.format('{}.{}'.format(filename, ext), '{}\\{}.{}'.format(save_dir, filename,ext), b_size[0], b_size[1], 3, x1, y1, x2, y2)
        new_xml = open('{}\\{}.xml'.format(save_dir, filename), 'w') 
        new_xml.write(xml)
        new_xml.close()


#__________________________________________________________________________

def gen(out_img_count = 3000, img_dir = 'objects/', save_dir = 'output/'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    backgrounds_dir = 'backgrounds/'
    branches_dir = 'branches/'
    ext = 'jpg'

    # background
    b_gamma = (0.6, 1.7) 
    b_size = (720, 405)
    b_blur = 1

    # bottle
    o_gamma = (0.5, 1.5)
    o_scale = (0.9, 1.1)
    o_pos_x = (50, 50)
    o_pos_y = (10, 10)
    o_rotation = (-15, 15)

    # noise
    s_count = (0, 0)
    s_gamma = (0.4, 2.4)
    s_scale = (0.8, 1.1)
    s_distance_min, s_distance_max = 150, 450
    #s_distance_min, s_distance_max = 400, 500
    s_blur = [1, 5]
    s_rotation = (-5, 5)

    #__________________________________________________________________________
    #random.seed(seed)

    while len(os.listdir(save_dir)) < out_img_count * 2:
        #try:
            t = time.time()
            filename = str(time.time())
            # background
            out = random_img(backgrounds_dir)[:,:,:3]

            rand_bkg_gamma = random.uniform(b_gamma[0], b_gamma[1])
            out = adjust_gamma(out, rand_bkg_gamma)
            if random.randint(0, 1) == 1:
                out = cv2.flip(out, 1)

            # bottle
            lum = random_img(img_dir)
            lum = random_size(lum, o_scale[0], o_scale[1])
            lum = imutils.rotate(lum, random.randint(o_rotation[0], o_rotation[1]))
            if random.randint(0, 1) == 1:
                    lum = cv2.flip(lum, random.randint(-1, 1))
                    
            mask = lum[:,:,3]
            lum = lum[:,:,:3]
            
            mask = cv2.medianBlur(mask, 9)

            lum = adjust_gamma(lum, rand_bkg_gamma)
            #lum = adjust_gamma(lum, random.uniform(o_gamma[0], o_gamma[1]))

            c = ((0, 0), (lum.shape[1], lum.shape[0]))

            h, w = out.shape[:2]
            o_x, o_y = random_position((o_pos_x[0], w - o_pos_x[1]),
                                                                 (o_pos_y[0], h - o_pos_y[1]))

            # branches
            for branches_count in range(random.randint(s_count[0], s_count[1])):
                s = random_img(branches_dir)

                #s = adjust_gamma(s, rand_bkg_gamma)
                #s = adjust_gamma(s, random.uniform(s_gamma[0], s_gamma[1]))

                s = random_size(s, s_scale[0], s_scale[1])
                if random.randint(0, 1) == 1:
                    s = cv2.flip(s, random.randint(-1, 1))

                s = imutils.rotate(s, random.randint(s_rotation[0], s_rotation[1]))
                mask1 = s[:,:,3]
                blur_p = s_blur[random.randint(0, len(s_blur) - 1)]
                s = cv2.GaussianBlur(s,(blur_p, blur_p), 0)
                mask1 = cv2.GaussianBlur(mask1,(blur_p, blur_p), 0)

                angle = random.uniform(0, 6.28)
                l = random.randint(s_distance_min, s_distance_max)
                s_x = int(np.cos(angle) * l)
                s_y = int(np.sin(angle) * l)
                
                out = combine_imgs(out, s[:,:,:3], mask1, o_x + s_x, o_y + s_y)
                
            # bottle
            out = combine_imgs(out, lum, mask, o_x, o_y)

            o_h, o_w = lum.shape[:2]
            c = ((np.clip(o_x - o_w // 2, 0, b_size[0]),
                        np.clip(o_y - o_h // 2, 0, b_size[0])),
                     (np.clip(o_x + o_w // 2, 0, b_size[0]),
                        np.clip(o_y + o_h // 2, 0, b_size[0])))
            c = ((o_x - o_w // 2, o_y - o_h // 2),
                     (o_x + o_w // 2, o_y + o_h // 2))


            

            #out = cv2.medianBlur(out, b_blur)
            b_h1, b_w1 = out.shape[:2]
            out = cv2.resize(out, b_size, cv2.INTER_CUBIC)
            b_h, b_w = out.shape[:2]
            k2, k1 = b_h / b_h1, b_w / b_w1
            c = ((int(c[0][0] * k1), int(c[0][1] * k2)), (int(c[1][0] * k1), int(c[1][1] * k2)))
            #out[c[0][1]:c[1][1],c[0][0]:c[1][0]] = cv2.medianBlur(out[c[0][1]:c[1][1],c[0][0]:c[1][0]], 3)
            if c[1][0] - c[0][0] < 15 or c[1][1] - c[0][1] < 15:
                continue
            if not True:
                cv2.rectangle(out, (c[0][0], c[0][1]), (c[1][0], c[1][1]), (255, 0, 0), 2)
                cv2.imshow("out", out)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            cv2.imwrite( '{}\\{}.{}'.format(save_dir, filename, ext), out)

            make_xml(filename, c, ext, save_dir, b_size)

if __name__ == '__main__':
    arr = [
            {'count' : 3,
             'img_dir' : 'objects/metal/',
             'save_dir' : 'output/metal/'},
            {'count' : 3,
             'img_dir' : 'objects/plastic/',
             'save_dir' : 'output/plastic/'},
            {'count' : 3,
             'img_dir' : 'objects/wood/',
             'save_dir' : 'output/wood/'},

          ]

    for i in range(len(arr)):
        Process(target=gen, args=(arr[i]['count'], arr[i]['img_dir'], arr[i]['save_dir'],)).start()




