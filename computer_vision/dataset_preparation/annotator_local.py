import sys
import os
import time
import threading
import tkinter as tk
import requests
import random


import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def print_text(img, text, coords=(0,0), color=(255, 255, 255),
               size=1.6, thikness=5):
  cv2.putText(img, str(text), coords,
              cv2.FONT_HERSHEY_SIMPLEX, size,
              (0, 0, 0), thikness*4)
  cv2.putText(img, str(text), coords,
              cv2.FONT_HERSHEY_SIMPLEX, size,
              color, thikness)
  return img

def print_text_rus(img, text, coords=(0,0), color=(255, 255, 255),
               size=1.6, thikness=5):
  
  b,g,r = color
  fontpath = "arial.ttf"
  font = ImageFont.truetype(fontpath, 32)
  img_pil = Image.fromarray(img)
  draw = ImageDraw.Draw(img_pil)
  
  draw.text((coords[0] - 1, coords[1] - 1),  text, font = font, fill = (0, 0, 0, 0))  
  draw.text(coords,  text, font = font, fill = (b, g, r, 0)) 
  img = np.array(img_pil)
  return img

      
def rgb_hack(rgb):
    return "#%02x%02x%02x" % rgb

SERVER_IP = 'http://127.0.0.1:8081'

config = ['class_1', 'class_2', 'class_3']

s0 = '''Нажмите "Сохранить", затем "Следующее изображение",\n''' \
     '''чтобы открыть следующее изображение'''

s1 = '''Пробел - закончить выделение\n''' \
     '''ESC - отменить выделение'''

text_var = None
get_button_text = None

bboxes = []
state = 0

master = None
user_id = None
image = None
file_name = None

CONF_FILE = 'conf.svz'
DATASET_PATH = 'data'
OUTPUT_DATASET_PATH = 'annotated'

files = os.listdir(DATASET_PATH)
random.shuffle(files)

def cv_process():
  global image, state, selected_class, bboxes, text_var

  bboxes = []

  while True:
    if image is None:
      time.sleep(0.2)
      continue
    
    frame = image.copy()
    for bbox in bboxes:
      cv2.rectangle(frame,
                    (bbox[0][0], bbox[0][1]),
                    (bbox[0][0] + bbox[0][2], bbox[0][1] + bbox[0][3]),
                    (0, 255 ,0), 1)
      
      frame = print_text(frame, bbox[1],
                 (bbox[0][0], bbox[0][1]),
                 (255, 255, 255),
                 0.7, 2)
    
    cv2.imshow('', frame)
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:
      break

    if state == 1:
        state = 0
        out = frame.copy()    
        cv2.rectangle(out, (0, 0), (out.shape[1], out.shape[0]),
                    (0, 255, 255), 5)
        text_var.set(s1)
        bbox = cv2.selectROI("", out, fromCenter=False, showCrosshair=True)
        text_var.set(s0)

        if bbox != (0, 0, 0, 0):
          bboxes.append((bbox, selected_class.get()))

    elif state == -1:
        break
  
  cv2.destroyAllWindows()

def select_click():
  global state 
  state = 1

def delete_click():
  global bboxes
  if len(bboxes) >= 1:
      bboxes.pop(-1)

def save_click():
  global bboxes, file_name, image, text_var
  if True: #len(bboxes) >= 1:
    text_var.set('Идет сохранение')
    height, width = image.shape[:2]
    with open('{}/{}.txt'.format(OUTPUT_DATASET_PATH, file_name.split('.')[0]), 'w') as f:
      for box in bboxes:
        x, y, w, h = box[0]
        
        x = round((x + w // 2) / width, 4)
        y = round((y + h // 2) / height, 4)
        w = round(w / width, 4)
        h = round(h / height, 4)
        
        class_name = box[1]
        f.write('{} {} {} {} {} \n'.format(class_name, x, y, w, h))

    cv2.imwrite('{}/{}'.format(OUTPUT_DATASET_PATH, file_name), image)
  text_var.set(s0)



def get_click():
  global user_id, image, file_name, text_var, bboxes, get_button_text, files
  print(1)
  get_button_text.set("Следующее изображение")
  text_var.set(s0)

  bboxes = []
  
  if len(files) <= 0:
    text_var.set(s0)
  else:
    print('Loading new image')
    file_name = files[0]
    files.pop(0)
    print(file_name)
    image = cv2.imread('{}/{}'.format(DATASET_PATH, file_name))
    #image = cv2.resize(image, (1280, 720), interpolation=cv2.INTER_AREA)
    os.remove('{}/{}'.format(DATASET_PATH, file_name))

    file_name = '{}.jpg'.format(str(time.ctime()).replace(':', '_'))

    print(file_name)

      
def close_click():
  global master, state 
  state = -1
  master.destroy()
  
def tk_process():
  global master, user_id, state, selected_class, bboxes, text_var, get_button_text
  try:
    master = tk.Tk()
    master.title("Annotator")
    
    master.config(bg=rgb_hack((152, 215, 0)))

    text_var = tk.StringVar()
    text_var.set('Нажмите "Открыть картинку"')

    tk.Label(master, textvariable=text_var, anchor='w',
             font=("Times New Roman", 12),
             bg=rgb_hack((152, 215, 0)),
             width=50, height=2).grid(sticky="W", row=0, column=0, columnspan=3)
##    tk.Label(master, text=s0, anchor='w',
##           font=("Times New Roman", 12),
##             bg=rgb_hack((152, 215, 0))).grid(sticky="W", row=1, column=0)
    user_id = tk.IntVar()

    get_button_text = tk.StringVar()
    get_button_text.set('Открыть картинку')
    
    get_button = tk.Button(master, textvariable=get_button_text, bg="white",
            width=20, height=2, command=get_click)
    get_button.grid(row=1, column=0)

    select_button = tk.Button(master, text="Выделить", bg="white",
            width=20, height=2, command=select_click)
    select_button.grid(row=1, column=1)

    save_button = tk.Button(master, text="Сохранить", bg="white",
            width=20, height=2, command=save_click)
    save_button.grid(row=1, column=2)

    delete_button = tk.Button(master, text="Удалить", bg="white",
            width=20, height=2, command=delete_click)
    delete_button.grid(row=2, column=1)
   

    close_button = tk.Button(master, text="Закрыть", bg="white",
            width=20, height=2, command=close_click)
    close_button.grid(row=2, column=2)

    selected_class = tk.IntVar()
    selected_class.set(0)

    for i, k in enumerate(config):
      tk.Radiobutton(text='{} - {}'.format(i, k),
                     variable=selected_class,
                     value=i,
                     bg=rgb_hack((152, 215, 0))).grid(sticky="W", row=i + 3, column=0)

    master.call('wm', 'attributes', '.', '-topmost', True)
    master.mainloop()
    
  except KeyboardInterrupt:
    master.destroy()


if __name__ == '__main__':
  if not os.path.exists(CONF_FILE):
    f = open(CONF_FILE, 'w')
    f.close()
  processes = []
  processes.append(StoppableThread(target=cv_process, args=()))
  processes.append(StoppableThread(target=tk_process, args=()))
##  processes.append(threading.Thread(target=cv_process, args=())) 
##  processes.append(threading.Thread(target=tk_process, args=()))
  for p in processes:
    p.start()
    
  while True:
    for i, p in enumerate(processes):
      if not p.is_alive():
        for j, pp in enumerate(processes):
          if i == j:
            continue
          pp.stop()
        sys.exit()
    
  

