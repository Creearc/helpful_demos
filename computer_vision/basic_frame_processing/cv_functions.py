import numpy as np
import cv2
import imutils


def restruct_bbox(bbox):
    '''
    Реструктурирует Bounding Box из формы (x, y, w, h) в форму (x1, y1, x2, y2)
    '''   
    assert (isinstance(bbox, tuple) or isinstance(bbox, list)) and len(bbox) == 4, "На входе должен быть tuple их 4 элементов"
    return (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])


def crop_by_countour(img, cnt):
    '''

    '''  
    x1, y1, x2, y2 = cnt[0][0], cnt[0][1], cnt[1][0], cnt[1][1]
    return img[y1 : y2, x1 : x2]


####################################################################
def res_img(img, width = None, height = None): # ???
    '''

    '''
    if width is None and not (height is None):
        out = imutils.resize(img, height = height)
    elif height is None and not (width is None):
        out = imutils.resize(img, width = width)
    elif width is None and height is None:
        out = img
    else:
        out = imutils.resize(img, width = width, height = height)
    return out
####################################################################


def get_contours_bboxes(img):
    '''
    Определение ограничивающих рамок по контурам
    '''  
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


def replace_region_from_img(img, new_part, region):
    '''
    Заменяет часть изображения img изображением new_part
    '''  
    img[region[1]:region[3], region[0]:region[2]] = new_part
    return img


def rotate_img(img, angle):
    '''
    Поворачивает изображение img на угол angle
    '''
    (h, w) = img.shape[:2]
    (cX, cY) = (w//2, h//2)
    m = cv2.getRotationMatrix2D((cX, cY), angle, 1.0) 
    return cv2.warpAffine(img, m, (w, h))


def hsv_threshold(img, h1=20, s1=10, v1=0, h2=70, s2=100, v2=100):
    '''
    Фильтрует BRG изображение img по HSV цветовой схеме, в диапазоне от (h1,s1,v1) до (h2,s2,v2)
    '''
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h1 = np.interp(h1, [0, 360], [0, 255])
    s1 = np.interp(s1, [0, 100], [0, 255])
    v1 = np.interp(v1, [0, 100], [0, 255])
    h2 = np.interp(h2, [0, 360], [0, 255])
    s2 = np.interp(s2, [0, 100], [0, 255])
    v2 = np.interp(v2, [0, 100], [0, 255])

    h_min = np.array((h1, s1, v1), np.uint8)
    h_max = np.array((h2, s2, v2), np.uint8)
    thresh = cv2.inRange(hsv, h_min, h_max)
    return thresh


def fix_fisheye1(image, camera_matrix = None, dist_coefs = None):
    '''

    '''
    if camera_matrix is None:
        camera_matrix = np.array([[1.65860429e+03, 0.00000000e+00, 1.92502145e+03],
                                  [0.00000000e+00, 1.76279078e+03, 1.06850525e+03],
                                  [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    if dist_coefs is None:
        dist_coefs = np.array([-0.26573577,  0.1363063,   0.00139622, -0.00174522, -0.07017501])

    dst = cv2.undistort(image, camera_matrix, dist_coefs, None, None)

    return dst


def fix_fisheye2(image, camera_matrix = None, dist_coefs = None):
    '''

    '''
    if camera_matrix is None:
        camera_matrix = np.array([[1.65860429e+03, 0.00000000e+00, 1.92502145e+03],
                                  [0.00000000e+00, 1.76279078e+03, 1.06850525e+03],
                                  [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    if dist_coefs is None:
        dist_coefs = np.array([-0.26573577,  0.1363063,   0.00139622, -0.00174522, -0.07017501])

    h, w = image.shape[:2]
    w1, h1 = 5 * w, 5 * h

    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w1, h1))
    mapx, mapy = cv2.initUndistortRectifyMap(camera_matrix, dist_coefs, None, newcameramtx, (w1, h1), 5)
    dst = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

    x, y, w, h = roi
    x += 200
    dst = dst[y:y + h, x:x + w]
    print(dst.shape)
    return dst


if __name__ == '__main__':
    pass
