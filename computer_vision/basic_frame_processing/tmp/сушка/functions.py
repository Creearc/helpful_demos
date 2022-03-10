import cv2
import numpy as np
import imutils
import time


def fix_collision(image):
    camera_matrix = np.array([[1.20845286e+03, 0.00000000e+00, 9.21918463e+02],
                              [0.00000000e+00, 1.20327003e+03, 5.73021959e+02],
                              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist_coefs = np.array([-0.36139144, 0.20009385, -0.0034076, 0.00149487, -0.07083848])

    h, w = image.shape[:2]
    # New Image shape to generate
    w1, h1 = 5 * w, 5 * h
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w1, h1))

    mapx, mapy = cv2.initUndistortRectifyMap(camera_matrix, dist_coefs, None, newcameramtx, (w1, h1), 5)
    dst = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

    x, y, w, h = roi
    x += 200
    dst = dst[y:y + h, x:x + w]
    #  print(dst.shape)
    return dst


def cals_sizes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) == 0:
        return None

    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)
    return (x, y, w, h)


def restruct_region(region):
    return (region[0], region[1], region[0] + region[2], region[1] + region[3])


def extract_region_from_img(img, region):
    return img.copy()[region[1]: region[3], region[0]: region[2]]


def recalc_region_to_global(global_region, local_region):
    return (global_region[0] + local_region[0],
            global_region[1] + local_region[1],
            global_region[0] + local_region[2],
            global_region[1] + local_region[3])


def print_text(img, text, coords=(0, 0), color=(255, 255, 255),
               size=1.6, thikness=5):
    cv2.putText(img, str(text), coords,
                cv2.FONT_HERSHEY_SIMPLEX, size,
                (0, 0, 0), thikness * 4)
    cv2.putText(img, str(text), coords,
                cv2.FONT_HERSHEY_SIMPLEX, size,
                color, thikness)


px_to_sm_k = 8

SCALE_REGION = restruct_region((270, 880, 1600, 4))


def make_beautiful_size(img):
    out = fix_collision(img)
    out = cv2.resize(out, (1920, 1080), interpolation=cv2.INTER_AREA)

    tmp = extract_region_from_img(out, SCALE_REGION)
    scale_region = cals_sizes(tmp)
    cv2.rectangle(out, SCALE_REGION[:2], SCALE_REGION[2:],
                  (255, 255, 255), 2)

    if not (scale_region is None):
        shpon_width = scale_region[2]
        scale_region = restruct_region(scale_region)
        scale_region = recalc_region_to_global(SCALE_REGION, scale_region)

        cv2.rectangle(out, scale_region[:2], scale_region[2:],
                      (0, 0, 255), 2)

        print_text(out, shpon_width / 8,
                   (SCALE_REGION[0] - 200, SCALE_REGION[1]),
                   (255, 255, 255),
                   1.6, 5)

        print_text(out, time.ctime(),
                   (50, 50),
                   (255, 255, 255),
                   1.6, 5)
    return out
