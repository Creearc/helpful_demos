import zmq
import time
import sys
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://0.0.0.0:5555")

while True:
    msg = input("Пожалуйста, введите информацию для публикации:").strip()
    if msg == 'b': # Закрыть символ подключения
        sys.exit()
    socket.send(msg.encode('utf-8'))
