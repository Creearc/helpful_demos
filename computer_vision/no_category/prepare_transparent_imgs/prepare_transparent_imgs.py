import cv2
import numpy as np


def save_transparent_img(img, mask):

    if len(mask.shape) > 2:
        mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)

    #result = cv2.bitwise_and(img, img, mask=mask)
    result = np.dstack([img, mask])
    cv2.imwrite("result.png", result)

    return result


if __name__ == '__main__':

    img_name = 'img.jpg'
    mask_name = 'mask.png'
    img = cv2.imread(img_name)
    mask = cv2.imread(mask_name)
    result = save_transparent_img(img, mask)
    cv2.imshow("image", result)
    cv2.waitKey(0) 
    cv2.destroyAllWindows() 
