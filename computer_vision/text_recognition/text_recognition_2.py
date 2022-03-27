from easyocr import Reader
import cv2

def cleanup_text(text):
  return "".join([c if ord(c) < 128 else "" for c in text]).strip()


langs = 'en'.split(",")
print("[INFO] OCR'ing with the following languages: {}".format(langs))

image = cv2.imread('1.jpg')

print("[INFO] OCR'ing input image...")
reader = Reader(langs, gpu=False)
results = reader.readtext(image)

for (bbox, text, prob) in results:
  print("[INFO] {:.4f}: {}".format(prob, text))

  (tl, tr, br, bl) = bbox
  tl = (int(tl[0]), int(tl[1]))
  tr = (int(tr[0]), int(tr[1]))
  br = (int(br[0]), int(br[1]))
  bl = (int(bl[0]), int(bl[1]))

  text = cleanup_text(text)
  cv2.rectangle(image, tl, br, (0, 255, 0), 2)
  cv2.putText(image, text, (tl[0], tl[1] - 10),
              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

cv2.imshow("Image", image)
cv2.waitKey(0)
