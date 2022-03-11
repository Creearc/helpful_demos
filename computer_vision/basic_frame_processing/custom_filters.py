import numpy as np
import cv2


def convolution(image, flt):
    '''

    '''
    iw,ih,id = image.shape
    fw,fh = flt.shape
    out = np.zeros((iw-fw+1,ih-fh+1,id))    
    for d in range(id):
        for h in range(ih-fh+1):
            for w in range(iw-fw+1):
                out[w,h,d] = np.sum(flt * image[w:w+fh, h:h+fw, d])
                if out[w,h,d] > 255:
                    out[w,h,d] = 255
                elif out[w,h,d] < 0:
                    out[w,h,d] = 0
    if id == 1:
        return np.resize(out, (out.shape[0], out.shape[1])).astype(np.uint8)
    else:
        return out.astype(np.uint8)


def global_contrast(img):
    '''

    '''
    arr = np.asarray(img, dtype = 'uint8')
    for row in range(0, arr.shape[0]):
        for col in range(0, arr.shape[1]):
            arr[row][col] = arr[row][col]*0.5 # changeable coef?
            if arr[row][col][0] > 255:
                arr[row][col] = [255,255,255]
            elif arr[row][col][0] < 0:
                arr[row][col] = [0,0,0]
    return arr


def gaussian_blur(img, kernel = None):
    '''

    '''
    if kernel is None:
        kernel = np.array([[0.0, 1.0, 2.0, 1.0, 0.0], 
                           [1.0, 3.0, 5.0, 3.0, 1.0],
                           [2.0, 5.0, 9.0, 5.0, 2.0],
                           [1.0, 3.0, 5.0, 3.0, 1.0],
                           [0.0, 1.0, 2.0, 1.0, 0.0]])
    
    kernel = kernel / np.sum(kernel)
    image_gauss = convolution(img, kernel)
    return image_gauss


def difference_blur(img):
    '''

    '''
    kernel = np.array([[ 0.0,   0.0,  -1.0,  0.0,  0.0], 
                       [ 0.0,  -1.0,  -2.0, -1.0,  0.0],
                       [-1.0,  -2.0,  16.0, -2.0, -1.0],
                       [ 0.0,  -1.0,  -2.0, -1.0,  0.0],
                       [ 0.0,   0.0,  -1.0,  0.0,  0.0]])
    kernel = kernel / (np.sum(kernel) if np.sum(kernel)!=0 else 1) #25
    image_gauss = convolution(img, kernel)
    return image_gauss
    

def median_filter(img, window):
    '''

    '''
    out = img.copy()
    h, w, c = img.shape
    for x in range(window // 2, w - window // 2):
        for y in range(window // 2, h - window // 2):
            for d in range(c):
                arr = []
                for i in range(x - 1, x + 2):
                    for j in range(y - 1, y + 2):
                        arr.append(img[j, i, d])
                arr.sort()
                out[y, x, d] = arr[len(arr) // 2]
    return out
