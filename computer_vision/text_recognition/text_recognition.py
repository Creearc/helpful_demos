from pytesseract import Output
import pytesseract
import cv2
import pygame
import sys


def write(text, x, y, screen, color=(200, 200, 200), size=150):
  font = pygame.font.SysFont("Arial", size)
  text = font.render(text, 1, color)
  text_rect = text.get_rect(center=(x, y))
  screen.blit(text, text_rect)

def recognition(img, screen):
  rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  rgb = cv2.resize(rgb, (W, H))
  
  results = pytesseract.image_to_data(rgb, output_type=Output.DICT, lang="rus")
  rgb = rgb.swapaxes(0, 1)
  pygame.surfarray.blit_array(screen, rgb)
  

  for i in range(len(results["text"])):
    x = results["left"][i]
    y = results["top"][i]
    w = results["width"][i]
    h = results["height"][i]

    text = results["text"][i]
    conf = int(float(results["conf"][i]))

    if conf > 50:
      if False:
        print("Confidence: {}".format(conf))
        print("Text: {}".format(text))
        print("")
      
      pygame.draw.rect(screen, (20, 20, 20), (x, y, w, h), 1)
      write(text, x + w // 2, y - h, screen, color=(20, 20, 0), size=h*2)
  pygame.display.update()


if __name__ == '__main__':
  try:
    #pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
    pygame.init()

    W = int(1920 // 1.5)
    H = int(1080 // 1.5)

    W = 640
    H = 480

    pygame.display.set_caption("OpenCV camera stream on Pygame")
    screen = pygame.display.set_mode([W, H])
    clock = pygame.time.Clock()
    camera = True
    if camera:
      cap = cv2.VideoCapture(0)
    else:
      img = cv2.imread('1.jpg')

    run = True
    while run:
      if camera:
        ret, img = cap.read()
        if not ret:
          run = False
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          run = False
      recognition(img, screen)
      pygame.display.flip()
      clock.tick(120)

    pygame.quit()
  except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()

    


