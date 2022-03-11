# Pavel Slivnitsin. MDS2. Image retrieval - Exercise 3.1

# Import libraries
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import cv2

def conv(image, flt):
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

def glob_contrast(img):
    arr = np.asarray(img, dtype = 'uint8')
    for row in range(0, arr.shape[0]):
        for col in range(0, arr.shape[1]):
            arr[row][col] = arr[row][col]*0.5
#            print(arr[row][col])
            if arr[row][col][0] > 255:
                arr[row][col] = [255,255,255]
            elif arr[row][col][0] < 0:
                arr[row][col] = [0,0,0]
    return arr

def gaussian_blur(img):
    kernel = np.array([[0.0, 1.0, 2.0, 1.0, 0.0], 
                   [1.0, 3.0, 5.0, 3.0, 1.0],
                   [2.0, 5.0, 9.0, 5.0, 2.0],
                   [1.0, 3.0, 5.0, 3.0, 1.0],
                   [0.0, 1.0, 2.0, 1.0, 0.0]])
    kernel = kernel / np.sum(kernel)
    image_gauss = conv(img,kernel)
    return image_gauss

def difference_blur(img):
    #kernel = np.array([[-1.0,-1.0,-1.0], 
    #                   [-1.0, 8.0,-1.0],
    #                   [-1.0,-1.0,-1.0]])
    kernel = np.array([[ 0.0,   0.0,  -1.0,  0.0,  0.0], 
                       [ 0.0,  -1.0,  -2.0, -1.0,  0.0],
                       [-1.0,  -2.0,  16.0, -2.0, -1.0],
                       [ 0.0,  -1.0,  -2.0, -1.0,  0.0],
                       [ 0.0,   0.0,  -1.0,  0.0,  0.0]])
    kernel = kernel / (np.sum(kernel) if np.sum(kernel)!=0 else 1) #25
    image_gauss = conv(img,kernel)
    return image_gauss
    
def median_filter(img, window):
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

# Image load 
img = cv2.imread('samp.jpg')
cv2.imshow('samp.jpg',img)
#cv2.imwrite('samp.jpg',res)
#'''
# a) ----------------------------------------------------------------- a)

#Global contrast change (manually)
plt.hist(img.flatten(),256,[0,256], color = 'r')
res = glob_contrast(img)
cv2.imshow('resa1.jpg',res)
plt.hist(res.flatten(),256,[0,256], color = 'b')

#Global contrast change (library)            ++++++++++++++++++++++++++++++++
img2 = cv2.imread('samp.jpg')
arr = np.asarray(img2, dtype = 'uint8')
res = cv2.multiply(arr, 0.5)
b,g,r=cv2.split(res)
res=cv2.merge((b,b,b))
#res=cv2.convertScaleAbs(arr, 1, 0.5)
cv2.imshow('resa2.jpg',res)
plt.hist(res.flatten(),256,[0,256], color = 'g')
plt.show()
#'''
# b) ----------------------------------------------------------------- b)
#Gaussian blur (manually)
img = cv2.imread('samp.jpg')
image_gauss = gaussian_blur(img)
cv2.imshow('resb1.jpg',image_gauss)

#Gaussian blur (library)
res2 = cv2.GaussianBlur(img, (5,5), 0)
cv2.imshow('resb2.jpg',res2)
#'''
# c) ----------------------------------------------------------------- c)
#Difference filter (manually)
img = cv2.imread('samp.jpg')
image = difference_blur(img)
cv2.imshow('resc1.jpg',image)

#Difference filter (library)
kernel = np.array([[ 0.0,   0.0,  -1.0,  0.0,  0.0], 
                   [ 0.0,  -1.0,  -2.0, -1.0,  0.0],
                   [-1.0,  -2.0,  16.0, -2.0, -1.0],
                   [ 0.0,  -1.0,  -2.0, -1.0,  0.0],
                   [ 0.0,   0.0,  -1.0,  0.0,  0.0]])

kernel = kernel/(np.sum(kernel) if np.sum(kernel)!=0 else 1)
#filter the source image
res = cv2.filter2D(img,-1,kernel)
cv2.imshow('resc2.jpg',res)

# d) ----------------------------------------------------------------- d)
#Median filter (manually)
img = cv2.imread('samp.jpg')
image_median = median_filter(img,3)
cv2.imshow('resd1.jpg', image_median)

#Median filter (library)
res = cv2.medianBlur(img,3)
cv2.imshow('resd2.jpg',res)
#'''
cv2.waitKey(0)
cv2.destroyAllWindows()