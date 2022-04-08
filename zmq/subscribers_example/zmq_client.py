import zmq
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect ("tcp://localhost:5555") # Несколько клиентов подключаются к одному адресу
socket.setsockopt (zmq.SUBSCRIBE, '123'.encode(' utf-8 ')) # фильтрация сообщений принимает только информацию, начинающуюся с 123
# socket.setsockopt (zmq.SUBSCRIBE, ''. encode ('utf-8')) # получать все сообщения
# Здесь необходимо использовать два случая для фильтрации сообщения, иначе сообщение не будет принято
while True:
    response = socket.recv().decode('utf-8')
    print("response: %s" % response)
