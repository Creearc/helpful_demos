# Модуль крыльчатки
import sys
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


class Rotator:
  def __init__(self, STEP_PIN=24, DIR_PIN=23, ENABLE_PIN=16):
    ### Пины
    self.STEP_PIN = STEP_PIN
    self.DIR_PIN = DIR_PIN
    self.ENABLE_PIN = ENABLE_PIN
    GPIO.setup(self.STEP_PIN, GPIO.OUT)
    GPIO.setup(self.DIR_PIN, GPIO.OUT)
    GPIO.setup(self.ENABLE_PIN, GPIO.OUT)
    self.process = GPIO.PWM(STEP_PIN, 1)

    ### Переменные
    self.frequency = 100
    self.left = True

  def change_dir(self):
    self.left = not self.left
    if self.left:
      GPIO.output(self.DIR_PIN, GPIO.LOW)
    else:
      GPIO.output(self.DIR_PIN, GPIO.HIGH)
      
  # Запуск крыльчатки
  def start(self):
    print('Запущен двигатель')
    if self.left:
      GPIO.output(self.DIR_PIN, GPIO.LOW)
    else:
      GPIO.output(self.DIR_PIN, GPIO.HIGH)
    self.process.ChangeFrequency(self.frequency)
    self.process.start(50)

  # Остановка крыльчатки
  def stop(self):
    self.process.stop()

if __name__ == '__main__':
  try:
    r = Rotator()
    while True:
      r.start()
      time.sleep(1.0)
      r.stop()
        
  except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()

