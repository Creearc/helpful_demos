#  python3 -m pip install pytelegrambotapi
import os
import time
import threading
import telebot
from telebot import types, util
import usb_cam_module
import cv2
import yolov5

TOKEN = 'token'
filename = 'ids.txt'
f = open(filename, 'a')
f.write('')
f.close()

lock = threading.Lock()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    global img, timeout
    idd = '{}\n'.format(message.chat.id)
    print(idd)
    f = open(filename, 'r')
    ids = f.readlines()
    f.close()
    if not(idd in ids):
        f = open(filename, 'a')
        f.write('{}\n'.format(idd))
        f.close()
        bot.send_message(idd, 'Внес вас в список')
        
    else:
        tmp = message.text.split()
        text, data = tmp[0], ' '.join(tmp[1:])
        if text == 'П':
            if img is None:
                bot.send_message(message.chat.id, 'Картинки нет!')
            else:
                name = 'data/{}.jpg'.format(str(time.time()).replace('.', '_'))
                cv2.imwrite(name, img)
                bot.send_photo(idd, photo=open(name, 'rb'))
        elif text == 'З':
            try:
                timeout = float(data)
                bot.send_message(message.chat.id, 'Задержка: {}'.format(timeout))
            except:
                bot.send_message(message.chat.id, 'Задержка должна быть быть указана числом')
            
        

def send_to_ids(text):
    global img, bot
    f = open(filename, 'r')
    for idd in f:
        if idd == '\n':
            continue
        try:
            bot.send_message(idd, text)
            name = 'data/{}.jpg'.format(str(time.time()).replace('.', '_'))
            cv2.imwrite(name, img)
            bot.send_photo(idd, photo=open(name, 'rb'))
        except:
            bot = telebot.TeleBot(TOKEN)
    time.sleep(5.0)
    f.close()


def user_checker():
    global img, timeout

    nn = yolov5.Yolov5('yolov5s.pt', [])
    users_data = ''
    time.sleep(2.0)
    print('Ready!')

    while True:
        img = c.get_img()
        if img is None:
          print('empty')
          time.sleep(0.1)
          continue

        detections = nn.detect(img)

        for detection in detections:
            if int(detection[-1]) == 0:
                send_to_ids('У вас гости!')
        time.sleep(timeout)
                
    
img = None
timeout = 10.1
c = usb_cam_module.Camera(0)
c.start()

threading.Thread(target=user_checker, args=()).start()
bot.infinity_polling(allowed_updates=util.update_types)
