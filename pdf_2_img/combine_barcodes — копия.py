#combine_barcodes.exe C:/Users/Саша/Downloads/Пропуск2112.pdf C:/Users/Саша/Downloads/Упаковка2112.pdf

import os
''' pip install pdf2jpg '''
from pdf2jpg import pdf2jpg
import cv2
import numpy as np
import imutils
import time

import sys
fl = []
if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        print(sys.argv[i])
        fl.append(sys.argv[i])
else:
    fl.append('C:/Users/Alexandr/Downloads/Пропуск06031.pdf')
    fl.append('C:/Users/Alexandr/Downloads/Упаковка06031.pdf')


output = 'tmp'
result_folder = 'results'
PADDING = 50
ADD_STEP = 4

fix_name = lambda x: x.replace('Пропуск', 'Pass').replace('Упаковка', 'Pack').replace('.pdf', '')
kernel = np.ones((5, 5), np.uint8) 

def extract_barcode(img, clockwise=True):
    tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tmp = cv2.threshold(tmp, 250, 255, cv2.THRESH_BINARY_INV)[1]
##    cv2.imshow('1', tmp)
    tmp_2 = tmp.copy()
    tmp_2 = cv2.dilate(tmp_2, kernel, iterations=2)
##    cv2.imshow('2', tmp_2)
    cnts = cv2.findContours(tmp_2, cv2.RETR_EXTERNAL,
                          cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    tmp = cv2.cvtColor(tmp, cv2.COLOR_GRAY2BGR)
    
    if len(cnts) == 0:
        return 

    result = []
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        result.append(img[y : y+h, x : x+w])
        result[-1] = cv2.rotate(result[-1],
                                cv2.ROTATE_90_CLOCKWISE if clockwise else cv2.ROTATE_90_COUNTERCLOCKWISE)
##    cv2.waitKey(0)
    return result


def place_barcodes(barcodes, img_result, date, x=PADDING, y=PADDING, list_number=0):
    for img in barcodes:
        h, w = img.shape[:2]

        if x + w + ADD_STEP > W - PADDING:
            y += h + ADD_STEP
            x = PADDING
        if y + h + ADD_STEP > H - PADDING:
            x, y = PADDING, PADDING
            cv2.imwrite('{}/result_{}_{}.png'.format(result_folder, date, list_number), img_result)
            img_result = img_result_template.copy()
            list_number += 1

        img_result[y : y+h, x : x+w] = img

        x += w + ADD_STEP
    cv2.imwrite('{}/result_{}_{}.png'.format(result_folder, date, list_number), img_result)
    return img_result, x, y, list_number
            

if __name__ == '__main__':
    try:
        if os.path.exists(output):
            for folder in os.listdir(output):
                for file in os.listdir('{}/{}'.format(output, folder)):
                    os.remove('{}/{}/{}'.format(output, folder, file))
                os.removedirs('{}/{}'.format(output, folder))
            os.removedirs(output)
    except Exception as e:
        print(e)
        
    os.makedirs(output)

    if not os.path.exists(result_folder): os.makedirs(result_folder)

    for f in fl:
        result = pdf2jpg.convert_pdf2jpg(f, output, pages="ALL")

    packs_images = []
    pass_images = []

    for folder in os.listdir(output):
        folder_new = fix_name(folder)
        os.rename('{}/{}'.format(output, folder),
                  '{}/{}'.format(output, folder_new))
        
        for file in os.listdir('{}/{}'.format(output, folder_new)):
            file_new = fix_name(file)
            os.rename('{}/{}/{}'.format(output, folder_new, file),
                      '{}/{}/{}'.format(output, folder_new, file_new))
            img = cv2.imread('{}/{}/{}'.format(output, folder_new, file_new))
            if 'Pass' in file_new:
                pass_images.append(img)
            elif 'Pack' in file_new:
                packs_images.append(img)

    print(len(packs_images), len(pass_images))

    H, W = pass_images[0].shape[:2]
    img_result_template = np.ones((H, W, 3), dtype="uint8") * 255
    img_result = img_result_template.copy()
    
    packs_barcodes = []
    for img in packs_images:
        packs_barcodes += extract_barcode(img)

    pass_barcodes = []
    for img in pass_images:
        pass_barcodes += extract_barcode(img, False)

    print(len(packs_barcodes), len(pass_barcodes))

    list_number = 0
    date = time.strftime('%d%m%y')
    x, y = PADDING, PADDING
    
    for i in range(2):
        img_result, x, y, list_number = place_barcodes(packs_barcodes, img_result,
                                                       date, x, y, list_number)

    for i in range(len(packs_barcodes)):
        img_result, x, y, list_number = place_barcodes(pass_barcodes, img_result,
                                                       date, x, y, list_number)
            
