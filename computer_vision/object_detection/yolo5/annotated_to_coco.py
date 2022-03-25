import os
import cv2


def recompute_txt(filename, width, height):
    out = []
    with open(filename, 'r') as f:
        for line in f:
            label, x, y, w, h = [int(i) for i in line.split()]
        
            x = (x + w // 2) / width
            y = (y + h // 2) / height
            w = w / width
            h = h / height

            out.append((label, x, y, w, h))
        
    return out
    

folder_path = 'A:\Projects\Rebroskleyka\dataset_annotaion_prog/annotated'.replace('\\', '/')
output_path = 'coco_set_1'
output_images = '{}/images/train'.format(output_path)
output_labels = '{}/labels/train'.format(output_path)

if not os.path.exists(output_path):
    os.makedirs(output_path)   
    os.makedirs(output_images)
    os.makedirs(output_labels)

for file in os.listdir(folder_path):
    if file[-4:] == '.txt':
        print('{}/{}.jpg'.format(folder_path, file[:-4]))
        img = cv2.imread('{}/{}.jpg'.format(folder_path, file[:-4]))
        h, w = img.shape[:2]
        data = recompute_txt('{}/{}'.format(folder_path, file), w, h)
        with open('{}/{}.txt'.format(output_labels, file[:-4]), 'w') as f:
            for element in data:
                f.write('{}\n'.format(' '.join([str(i) for i in element])))

        with open('{}/{}.jpg'.format(folder_path, file[:-4]), 'rb') as src:
            with open('{}/{}.jpg'.format(output_images, file[:-4]), 'wb') as dst:
                dst.write(src.read())

