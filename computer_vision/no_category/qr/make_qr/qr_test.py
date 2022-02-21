# -*- coding: utf-8 -*-
import hashlib
import cv2

def create_qr(text):
  import qrcode
  
  qr = qrcode.QRCode(
      version=1,
      error_correction=qrcode.constants.ERROR_CORRECT_L,
      box_size=20,
      border=2,
  )
  
  qr.add_data(s)
  qr.make(fit=True)

  img = qr.make_image(fill_color="#ffffff", back_color="#1b75bb")
  text = hashlib.sha224(text.encode('utf-8')).hexdigest()
  text = str(text) + '.png'
  img.save(text)
  return text

if __name__ == '__main__':
  s = 'https://github.com/Creearc/helpful_demos'
  img_name = create_qr(s)
  img = cv2.imread(img_name)
  cv2.imshow('', img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
