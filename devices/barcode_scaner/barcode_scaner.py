import threading
import time

class Scaner:
  def __init__(self):
    self.lock = threading.Lock()
    self.code = None
    self.thrd = threading.Thread(target=self.process, args=())

  def get_code(self):
    with self.lock:
      code = self.code
      if self.code != None:
        self.code = None
    return code
    

  def start(self):
    if not self.thrd.is_alive():
      print('[BARCODE_SCANER] Запущено сканирование')
      self.thrd = threading.Thread(target=self.process, args=())
      self.thrd.start()
    else:
      print('[BARCODE_SCANER] Cканирование уже запущено')

  def process(self): 
    code = read()
    with self.lock:
      self.code = code
    print('[BARCODE_SCANER] Cканирование завершено')
  
def read():
  out = ''
  last = 0
  counter = 0 
  with open('/dev/usb/hiddev0', 'rb') as f:
    while True:
      tmp = f.read(8)
      try:
        tmp = tmp[3:].decode()[1]
        out = '{}{}'.format(out, tmp)
      except:
        print('[BARCODE_SCANER] Unsupported code')
        return None
  
      if ord(tmp) == 125 and last == 34:
        break
      else:
        last = ord(tmp)
      counter += 1
    return out.split('data')[-1][3:-2]
  




if __name__ == '__main__':
  s = Scaner()
  print('Reading')
  s.start()
  while True:
    print(1)
    code = s.get_code()
    if code != None:
      print(code)
    if not s.thrd.is_alive():
      s.start()
    time.sleep(0.2)
