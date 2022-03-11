import cv2
import imutils
import numpy as np

# Чтение изображения
img = cv2.imread('sample.jpg')
# img = cv2.imread('sample_binary.png')



### OpenCV ###
# """
# Разделить и объединить цветовые каналы изображения
b,g,r=cv2.split(img)
res=cv2.merge((b,g,r))
# """


# """
# 2D cвёртка
kernel = np.ones((5,5),np.float32)/25
conv = cv2.filter2D(img,-1,kernel)
# """


# """
# Размытие
kernel = (5,5)
blur = cv2.blur(img, kernel)
# """


# """
# Размытие по Гауссу
kernel = (5,5)
gaussianBlur = cv2.GaussianBlur(img, kernel, 0)
# """


# """
# Медианный фильтр
medianBlur = cv2.medianBlur(img, 3)
# """


# """
# Морфологические операции (Эрожн дилейшн опенинг клозинг)

# """


# """
# Флип

# """


# """
# Изменение цветовых схем
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# """


# """
# Совместить изображения
stacked_h = np.hstack([img, img])
stacked_v = np.vstack([img, img])
# """



### imutils ###
# """
# Повысить контраст и яркость
adj = imutils.adjust_brightness_contrast(gray, brightness=50.0, contrast=50.0)
# """


# """
# Скелетонизация
gray_sk = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
skeleton_imutils = imutils.skeletonize(gray_sk, size=(3, 3))
# """


# """
# Контуры Canny
gray_canny = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canny_imutils = imutils.auto_canny(gray_canny)
# """


# """
# Показать изображение
cv2.imshow('result', binary)
cv2.waitKey(0)
cv2.destroyAllWindows()
# """
