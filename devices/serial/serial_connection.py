import serial

class serial_obj:
  def __init__(self, port='/dev/ttyUSB0', bandwidth=9600): 
    self.ser = serial.Serial(port, bandwidth)

  def read_serial(self):
    s = b''
    while s == b'':
      s = self.ser.readline()
    try:
      out = int(s.decode())
    except:
      out = s.decode()
    return out

  def tell_serial(self, command):
    self.ser.write('{}\n'.format(command).encode())


if __name__ == "__main__":
  so = serial_obj()
  while True:
    print(so.read_serial())
