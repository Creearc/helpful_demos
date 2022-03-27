import os
import random
import cv2
import imutils
from imutils import paths
import numpy as np
import pandas as pd
import time


def adjust_gamma(img, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(img, table)


def rotate(origin, point, angle):
  ox, oy = origin
  px, py = point
  qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
  qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
  return [int(qx), int(qy)]


def random_img(path):
    l = os.listdir(path)
    ll = l[random.randint(0, len(l) - 1)]
    all_path = '{}{}'.format(path, ll)
    im = cv2.imread('{}{}'.format(path, ll), cv2.IMREAD_UNCHANGED)
    return  im, all_path


def random_size(img, s_min=0.8, s_max=1.3):
    out = imutils.resize(img, width = int(img.shape[1] * random.uniform(s_min, s_max)))
    return out

def random_obj_num(count, s_min=0.8, s_max=1.3):
    num = random.randint(1, count)
    return num

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


def gen(out_img_count=10,
        img_dir = 'objects/',
        save_mask_dir = 'output/annotations/',
        save_dir = 'output/waste_train2021/'):
    font = cv2.FONT_HERSHEY_SIMPLEX
    counter = 10000000
    backgrounds_dir = 'backgrounds/'
    ext = 'jpg'
    ext_mask = 'png'

    # background
    b_gamma = (0.9, 2.4)
    b_size = (512, 512)
    b_blur = 4
    scale_coef = 4
    b_mega_size = (scale_coef * b_size[0], scale_coef * b_size[1])

    # object
    o_gamma = (0.9, 1.0)
    o_scale = (1.1, 1.4)
    o_pos_x = (250, b_mega_size[0]-250)
    o_pos_y = (250, b_mega_size[1]-250)
    #o_pos_x = (150, 150)
    #o_pos_y = (100, 50)
    o_rotation = (-10, -9)
    o_rotation = (-10, 10)
    
    while len(os.listdir(save_dir)) < out_img_count:
        t = time.time()
        filename = str(time.time())

        # background
        out, p = random_img(backgrounds_dir)
        out = out[:,:,:3]
        out = cv2.resize(out, b_mega_size, cv2.INTER_AREA)

        #'''
        rand_bkg_gamma = random.uniform(b_gamma[0], b_gamma[1])
        out = adjust_gamma(out, rand_bkg_gamma)
        if random.randint(0, 1) == 1:
            out = cv2.flip(out, 1)
        #'''

        # object
        obj_num = random_obj_num(4)
        for i in range(obj_num):
            o_img , p = random_img(img_dir)
            o_img  = random_size(o_img , o_scale[0], o_scale[1])
            
            r = random.randint(o_rotation[0], o_rotation[1])
            angle = r * np.pi/180
            o_img = imutils.rotate(o_img, r)

            mask = o_img[:,:,3]
            o_img = o_img[:,:,:3]

            mask = cv2.medianBlur(mask, 9)
            o_img = adjust_gamma(o_img, rand_bkg_gamma)
            c = ((0, 0), (o_img.shape[1], o_img.shape[0]))
            o_x, o_y = random_position(o_pos_x, o_pos_y)
            out = combine_imgs(out, o_img, mask, o_x, o_y)
            
            wimg = np.zeros((mask.shape[0],
                             mask.shape[1], 3),
                             np.uint8)
            wimg[:] = 255
            bimg = np.zeros((out.shape[0],
                             out.shape[1], 3),
                             np.uint8)
            final_mask = combine_imgs(bimg, wimg, mask, o_x, o_y)
            
            cl = p.split('/')[-1].split("_")[0]
            cv2.imwrite( '{}\\{}_{}_{}.{}'.format(save_mask_dir, counter, cl, i, ext_mask), final_mask)
        

        o_h, o_w = o_img.shape[:2]
        c = ((np.clip(o_x - o_w // 2, 0, b_mega_size[0]),
                    np.clip(o_y - o_h // 2, 0, b_mega_size[0])),
                 (np.clip(o_x + o_w // 2, 0, b_mega_size[0]),
                    np.clip(o_y + o_h // 2, 0, b_mega_size[0])))

        #out = cv2.medianBlur(out, b_blur)
        out = cv2.resize(out, b_size, cv2.INTER_CUBIC)
        c = ((c[0][0] // 4, c[0][1] // 4), (c[1][0] // 4, c[1][1] // 4))

        if not True:
            cv2.rectangle(out, (c[0][0], c[0][1]), (c[1][0], c[1][1]), (255, 0, 0), 2)
            cv2.imshow("out", out)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        cv2.imwrite( '{}\\{}.{}'.format(save_dir, str(counter), ext), out)
        #print(counter)
        counter += 1




out_img_count = 5
t = time.time()
gen(out_img_count = out_img_count)
print((time.time() - t) / out_img_count)