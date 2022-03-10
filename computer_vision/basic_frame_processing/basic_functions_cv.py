import numpy as np
import cv2

def restruct_bbox(bbox):
    '''
    Реструктурирует Bounding Box из формы (x, y, w, h) в форму (x1, y1, x2, y2)
    '''   
    assert (isinstance(bbox, tuple) or isinstance(bbox, list)) and len(bbox) == 4, "На входе должен быть tuple их 4 элементов"
    return (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])


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


if __name__ == '__main__':
    pass
