'''sudo apt update; sudo apt install poppler-utils'''
import os
import cv2
import numpy as np
import imutils
import time
import zipfile

import sys
fl = []
if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        print(sys.argv[i])
        fl.append(sys.argv[i])
else:
    fl.append('C:/Users/Саша/Downloads/ПропускH.pdf')
    fl.append('C:/Users/Саша/Downloads/УпаковкаH.pdf')


output = 'tmp'
result_folder = 'results'
PADDING = 50
ADD_STEP = 4

fix_name = lambda x: x.replace('Пропуск', 'Pass').replace('Упаковка', 'Pack').replace('.pdf', '')
kernel = np.ones((5, 5), np.uint8)

def zip(folder, output_folder, name):
    name = "{}.zip".format(name)
    output_file = "{}/{}".format(output_folder, name)
    print(folder)
    with zipfile.ZipFile(output_file, "w") as zf:
        #zf.write(folder)
        for filename in os.listdir(folder):
            zf.write(os.path.join(folder, filename),
                     filename)
                
    return name


def extract_barcode(img, clockwise=True):
    tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tmp = cv2.threshold(tmp, 250, 255, cv2.THRESH_BINARY_INV)[1]
    tmp_2 = tmp.copy()
    tmp_2 = cv2.dilate(tmp_2, kernel, iterations=2)
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

    return result


def place_barcodes(barcodes, img_result, date, W, H, x=PADDING, y=PADDING, list_number=0,
                   img_result_template=None, PADDING=1, ADD_STEP=1):
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


def clear(output):
    try:
        if os.path.exists(output):
            for folder in os.listdir(output):
                for file in os.listdir('{}/{}'.format(output, folder)):
                    os.remove('{}/{}/{}'.format(output, folder, file))
                os.removedirs('{}/{}'.format(output, folder))
            os.removedirs(output)
    except Exception as e:
        print(e)
        

def main(files, output, result_folder, PADDING, ADD_STEP):
    clear(result_folder)
    clear(output)
        
    os.makedirs(output)

    if not os.path.exists(result_folder): os.makedirs(result_folder)

    for f in files:
        name = f.split('/')[-1].split('.')[0]
        os.makedirs('{}/{}'.format(output, name))
        os.system('''pdftoppm files/{}.pdf {}/{}/{} -png -scale-to-x 2479 -scale-to-y 3508'''.format(name, output, name, name))

    packs_images = dict()
    pass_images = dict()
    
    for folder in os.listdir(output):
        folder_new = fix_name(folder)
        os.rename('{}/{}'.format(output, folder),
                  '{}/{}'.format(output, folder_new))

        if 'Pass' in folder_new:
            key = folder_new[len('Pass') : ]
            pass_images[key] = []
        elif 'Pack' in folder_new:
            key = folder_new[len('Pack') : ]
            packs_images[key] = []
        
        for file in os.listdir('{}/{}'.format(output, folder_new)):
            file_new = fix_name(file)
            os.rename('{}/{}/{}'.format(output, folder_new, file),
                      '{}/{}/{}'.format(output, folder_new, file_new))
            img = cv2.imread('{}/{}/{}'.format(output, folder_new, file_new))

            if 'Pass' in file_new:
                pass_images[key].append(img)
            elif 'Pack' in file_new:
                packs_images[key].append(img)

    H, W = pass_images[key][0].shape[:2]
    img_result_template = np.ones((H, W, 3), dtype="uint8") * 255
    img_result = img_result_template.copy()
    
    packs_barcodes = dict()
    for key, imgs in packs_images.items():
        packs_barcodes[key] = []
        for img in imgs:
            packs_barcodes[key] += extract_barcode(img)

    pass_barcodes = dict()
    for key, imgs in pass_images.items():
        pass_barcodes[key] = []
        for img in imgs:
            pass_barcodes[key] += extract_barcode(img, False)

    list_number = 0
    date = time.strftime('%d%m%y')
    x, y = PADDING, PADDING

    for key in packs_barcodes:
        print(key, len(packs_barcodes[key]), len(pass_barcodes[key]))
        for i in range(2):
            img_result, x, y, list_number = place_barcodes(packs_barcodes[key], img_result,
                                                       date, W, H, x, y, list_number,
                                                       img_result_template, PADDING, ADD_STEP)

        for i in range(len(packs_barcodes[key])):
            img_result, x, y, list_number = place_barcodes(pass_barcodes[key], img_result,
                                                       date, W, H, x, y, list_number,
                                                       img_result_template, PADDING, ADD_STEP)

    clear(output)
    return len(os.listdir(result_folder)) > 0

    
if __name__ == '__main__':
    main(fl)
            
