import os
import random
import cv2
import imutils
import numpy as np
import time


def random_img(path):
    l = os.listdir(path)
    ll = l[random.randint(0, len(l) - 1)]
    return cv2.imread('{}{}'.format(path, ll), cv2.IMREAD_UNCHANGED), ll

def random_position(x_l, y_l):
    if x_l[1] - x_l[0] < 0:
        x_l = (x_l[0], x_l[0] + 1)
        
    if y_l[1] - y_l[0] < 0:
        y_l = (y_l[0], y_l[0] + 1)
        
    return random.randint(x_l[0], x_l[1]), random.randint(y_l[0], y_l[1])

def random_size(img, s_min=0.8, s_max=1.3):
    out = imutils.resize(img, width = int(img.shape[1] * random.uniform(s_min, s_max)))
    return out

def adjust_gamma(img, gamma=1.0):
  invGamma = 1.0 / gamma
  table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
  return cv2.LUT(img, table)

def generate_noise(shape, repeats=3, dilate=3, blur=5):
    kernel = np.ones((3, 3), np.uint8)
    
    result = np.zeros((shape), np.uint8) + 255 // 2

    for i in range(repeats):      
        gauss = np.random.normal(0, 255, result.size)
        gauss = gauss.reshape(result.shape).astype('uint8')
        if dilate > 0:
            gauss = cv2.dilate(gauss, kernel, iterations=dilate)
        
        #gauss = cv2.normalize(gauss, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        result = result // 2 + gauss // 2
        if blur > 0:
            result = cv2.medianBlur(result, blur)

    result = cv2.normalize(result, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    return result


def combine_images(mask, obj, o_x, o_y):
    out = mask.copy()

    obj_mask = obj[:,:,3].copy()
    obj_mask = cv2.cvtColor(obj_mask, cv2.COLOR_GRAY2BGR)

    h, w = obj.shape[:2]
    o_y, o_x = o_y - h // 2, o_x - w // 2
    part = out[o_y : o_y + h, o_x : o_x + w]
    part = np.where(obj_mask <= 250, part, obj[:,:,:3])
    #part = cv2.medianBlur(part, 5)
    out[o_y : o_y + h, o_x : o_x + w] = part
    
    #cv2.rectangle(out, (o_x, o_y), (o_x + w, o_y + h), (255, 0, 0), 2)
    return out

def combine_masks(mask, obj, o_x, o_y):
    out = mask.copy()
    
    h, w = obj.shape
    o_y, o_x = o_y - h // 2, o_x - w // 2
    part = out[o_y : o_y + h, o_x : o_x + w]
    part = np.where(obj == 0, part, obj)
    part = cv2.medianBlur(part, 5)
    out[o_y : o_y + h, o_x : o_x + w] = part

    return out

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

def write_annotations(path, name, data, class_label, classes, img, debug=False):
    height, width = img.shape[:2]
    with open('{}/{}.txt'.format(path, name), 'w') as f:
        for i in range(len(data)):
            label = classes.index(class_label)

            for (x1, y1), (x2, y2) in data[i]:
                w = x2 - x1
                h = y2 - y1

                x = (x1 + w / 2) / width
                y = (y1 + h / 2) / height
                w = w / width
                h = h / height

                f.write('{} {} {} {} {}\n'.format(label, x, y, w, h))

                if debug:
                    cv2.rectangle(img,
                                  (int(width * x) - int(width * w / 2), int(height * y) - int(height * h / 2)),
                                  (int(width * x) + int(width * w / 2), int(height * y) + int(height * h / 2)),
                                  (0, 0, 255), 1)
                    cv2.imshow("out", img)
                    cv2.waitKey(0)
                

def make_yaml(file_path, name, dataset_path, classes):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        
    with open('{}/{}.yaml'.format(file_path, name), 'w') as f:
        f.write('path: {}\n'.format(dataset_path))
        f.write('train: {}\n'.format('images/train'))
        f.write('val: {}\n'.format('images/val'))

        f.write('nc: {}\n'.format(len(classes)))
        f.write('names: {}\n'.format(classes))

def generate(classes,
             out_img_count_train=100,
             out_img_count_val=10,
             class_name='rubbish',
             imgs_dir='rubbish/',
             backgrounds_dir='backgrounds/',
             save_dir='cocos/coco_set_6',
             is_train=True,

             obj_count=(1, 9),
             obj_scale=(0.8, 1.1),
             obj_rotation=(-15, 15),
             obj_gamma = (0.7, 1.3),

             list_rotation=(-2, 2),
             debug=False): 


    b_gamma = (0.4, 2.7)

    t = time.time()    
    for folder, out_img_count in (['train', out_img_count_train],
                                  ['val', out_img_count_val]):

        output_images = '{}/images/{}'.format(save_dir, folder)
        output_labels = '{}/labels/{}'.format(save_dir, folder)

        if not os.path.exists(output_images):
            os.makedirs(output_images)
        if not os.path.exists(output_labels):
            os.makedirs(output_labels)

        last_percent = -1
        for count in range(out_img_count):
            percent = int(count / out_img_count * 100)
            if percent > last_percent:
                last_percent = percent
                #print('{}% {}/{}'.format(percent, count, out_img_count))
            
            result, name = random_img(backgrounds_dir)
            try:
                h, w = result.shape[:2]
            except:
                print(name)
                continue

            obj, name = random_img(imgs_dir)
            if random.randint(0, 1) == 1:
                obj = cv2.rotate(obj, cv2.ROTATE_90_CLOCKWISE)
            else:
                obj = cv2.rotate(obj, cv2.ROTATE_90_COUNTERCLOCKWISE)

            
            try:
                obj = random_size(obj, s_min=obj_scale[0], s_max=obj_scale[1])
            except:
                print(name)
                continue
            
            obj = imutils.rotate(obj, random.randint(obj_rotation[0], obj_rotation[1]))

            if obj.shape[1] > w or obj.shape[0] > h:
                obj = cv2.resize(obj, (int(obj.shape[1] * 0.9), int(obj.shape[0] * 0.9)))

            obj = adjust_gamma(obj, random.uniform(obj_gamma[0], obj_gamma[1]))

            o_x, o_y = random_position((5 + obj.shape[1] // 2, w - obj.shape[1] // 2 - 5),
                                       (5 + obj.shape[0] // 2, h - obj.shape[0] // 2 - 5))

            result = combine_images(result, obj, o_x, o_y)
            obj_data = [((o_x - obj.shape[1] // 2, o_y - obj.shape[0] // 2),
                         (o_x + obj.shape[1] // 2, o_y + obj.shape[0] // 2))] 
            

            zzz = []

            shape = (result.shape[0], result.shape[1])
            
            zzz.append(cv2.resize(generate_noise((shape[0] // 10, shape[1] // 10),
                                 repeats=1,
                                 dilate=3,
                                 blur=5), (shape[1], shape[0])))

            zzz.append(cv2.resize(generate_noise((shape[0] // 2, shape[1] // 2),
                                 repeats=1,
                                 dilate=1,
                                 blur=3), (shape[1], shape[0])))

            result = cv2.addWeighted(result, 0.7, cv2.cvtColor(zzz[0], cv2.COLOR_GRAY2BGR), 0.3, -20)
            result = cv2.addWeighted(result, 0.9, cv2.cvtColor(zzz[1], cv2.COLOR_GRAY2BGR), 0.1, -10)

            result = adjust_gamma(result, random.uniform(b_gamma[0], b_gamma[1]))
            
            name = str(time.time()).replace('.', '')
            write_annotations(output_labels, name, [obj_data], class_name, classes, result)
            cv2.imwrite('{}/{}.jpg'.format(output_images, name), result) 
            
            if debug:
                cv2.imshow("out", result)
                
                for d in obj_data:
                    cv2.rectangle(result, d[0], (d[1]), (0, 0, 255), 1)

                cv2.imshow("out2", result)
                
                cv2.waitKey(0)
                #cv2.destroyAllWindows()
                
    print(time.time()- t)



if __name__ == '__main__':
    classes = ['aluminium', 'bottles_colored', 'bottles_milk', 'bottles_transparent', 'cups', 'glass']

    dataset_path = 'cocos/coco_set_5'
    make_yaml('cocos', 'coco_set_5', dataset_path, classes)

##    generate(classes,
##             out_img_count_train=2000,
##             out_img_count_val=500,
##             class_name='cups',
##             imgs_dir='cups/',
##             backgrounds_dir='backgrounds/',
##             save_dir=dataset_path,
##
##             obj_count=(1, 3),
##             obj_scale=(0.6, 0.8),
##             obj_rotation=(-10, 10),
##             obj_gamma = (0.8, 1.6),
##
##             debug = not True)
##
##    generate(classes,
##             out_img_count_train=2000,
##             out_img_count_val=500,
##             class_name='aluminium',
##             imgs_dir='aluminium/',
##             backgrounds_dir='backgrounds/',
##             save_dir=dataset_path,
##
##             obj_count=(1, 3),
##             obj_scale=(0.2, 0.8),
##             obj_rotation=(-10, 10),
##             obj_gamma = (0.2, 1.0),
##
##             debug= not True)
##    
##    generate(classes,
##             out_img_count_train=2000,
##             out_img_count_val=500,
##             class_name='bottles_colored',
##             imgs_dir='bottles_colored/',
##             backgrounds_dir='backgrounds/',
##             save_dir=dataset_path,
##
##             obj_count=(1, 3),
##             obj_scale=(0.2, 0.8),
##             obj_rotation=(-10, 10),
##             obj_gamma = (0.2, 1.0),
##
##             debug=not True)
##
##    generate(classes,
##             out_img_count_train=2000,
##             out_img_count_val=500,
##             class_name='bottles_milk',
##             imgs_dir='bottles_milk/',
##             backgrounds_dir='backgrounds/',
##             save_dir=dataset_path,
##
##             obj_count=(1, 3),
##             obj_scale=(0.2, 0.8),
##             obj_rotation=(-10, 10),
##             obj_gamma = (0.2, 1.0),
##
##             debug=not True)
##
##    generate(classes,
##             out_img_count_train=2000,
##             out_img_count_val=500,
##             class_name='glass',
##             imgs_dir='glass/',
##             backgrounds_dir='backgrounds/',
##             save_dir=dataset_path,
##
##             obj_count=(1, 3),
##             obj_scale=(0.2, 0.8),
##             obj_rotation=(-10, 10),
##             obj_gamma = (0.2, 1.0),
##
##             debug=not True)

    generate(classes,
             out_img_count_train=2000,
             out_img_count_val=500,
             class_name='bottles_transparent',
             imgs_dir='bottles_transparent/',
             backgrounds_dir='backgrounds/',
             save_dir=dataset_path,

             obj_count=(1, 3),
             obj_scale=(0.2, 0.8),
             obj_rotation=(-10, 10),
             obj_gamma = (0.2, 1.0),

             debug=not True)
