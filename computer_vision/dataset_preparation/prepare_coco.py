import os
import random

folder_path = 'annotated'
output_path = '../results/chaos_5'
#output_path = '../results/manual_5'

classes = ['list', 'torcevoye smech', 'rubbish', 'zazor', 'nahlest', 'zakor', 'water', 'zalom', 'smallhole']
classes = ['list', 'chaos', 'person']
val_percent = 0.2


def make_yaml(file_path, name, dataset_path, classes):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        
    with open('{}/{}.yaml'.format(file_path, name), 'w') as f:
        f.write('path: {}\n'.format(dataset_path))
        f.write('train: {}\n'.format('images/train'))
        f.write('val: {}\n'.format('images/val'))

        f.write('nc: {}\n'.format(len(classes)))
        f.write('names: {}\n'.format(classes))

make_yaml('/'.join(output_path.split('/')[:-1]),
          output_path.split('/')[-1],
          '/home/alexandr/datasets/yolo5/cocos/{}'.format(output_path.split('/')[-1]),
          classes)

for tmp_folder in ('train', 'val'):

        output_images = '{}/images/{}'.format(output_path, tmp_folder)
        output_labels = '{}/labels/{}'.format(output_path, tmp_folder)

        if not os.path.exists(output_images):
            os.makedirs(output_images)
        if not os.path.exists(output_labels):
            os.makedirs(output_labels)
    
counter = 0
files_names = os.listdir(folder_path)
val_step = int(len(files_names) * 0.5 * val_percent)
print('Val', val_step, 'Train', int(len(files_names) * 0.5 - val_step))

tmp_folder = 'val'
output_images = '{}/images/{}'.format(output_path, tmp_folder)
output_labels = '{}/labels/{}'.format(output_path, tmp_folder)

files = []
for file in files_names:        
    if file[-4:] == '.txt':
        files.append(file)

random.shuffle(files)

for file in files:
    try:
        with open('{}/{}.jpg'.format(folder_path, file[:-4]), 'rb') as src:
            with open('{}/{}.jpg'.format(output_images, file[:-4]), 'wb') as dst:
                dst.write(src.read())

            
        with open('{}/{}.txt'.format(folder_path, file[:-4]), 'r') as src:
            with open('{}/{}.txt'.format(output_labels, file[:-4]), 'w') as dst:
                dst.write(src.read())

    except:
        print(file)
        continue
            
    counter += 1
    if counter > val_step:
        tmp_folder = 'train'
        output_images = '{}/images/{}'.format(output_path, tmp_folder)
        output_labels = '{}/labels/{}'.format(output_path, tmp_folder)
            
