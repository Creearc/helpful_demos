import os
import xml.etree.ElementTree as ET

labels = ['bottles']


def recompute_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    width = int(root.find('size').find('width').text)
    height = int(root.find('size').find('height').text)

    out = []

    for i, obj in enumerate(root.iter('object')):
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text),
             int(xmlbox.find('ymin').text),
             int(xmlbox.find('xmax').text),
             int(xmlbox.find('ymax').text))

        label = obj.find('name').text

        w = b[2] - b[0]
        h = b[3] - b[1]
        
        x = (b[0] + w // 2) / width
        y = (b[1] + h // 2) / height
        w = w / width
        h = h / height

        out.append((labels.index(label), x, y, w, h))
        
    return out
    

path = 'set_1'
output_path = 'coco_set_1'
output_images = '{}/images'.format(output_path)
output_labels = '{}/labels'.format(output_path)

if not os.path.exists(output_path):
    os.mkdir(output_path)   
    os.mkdir(output_images)
    os.mkdir(output_labels)

for folder in os.listdir(path):
    folder_path = '{}/{}'.format(path, folder)
    
    for file in os.listdir(folder_path):
        if file[-4:] == '.xml':
            data = recompute_xml('{}/{}'.format(folder_path, file))
            with open('{}/{}.txt'.format(output_labels, file[:-4]), 'w') as f:
                for element in data:
                    f.write('{}\n'.format(' '.join([str(i) for i in element])))
                    
        elif file[-4:] == '.jpg':
            with open('{}/{}'.format(folder_path, file), 'rb') as src:
                with open('{}/{}.jpg'.format(output_images, file[:-4]), 'wb') as dst:
                    dst.write(src.read())
