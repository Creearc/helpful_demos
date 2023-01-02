import os
import cv2
import imageio

PATH = 'E:/slides/Tue_Dec_20_11_04_57_2022.mp4'
OUTPUT_FILE = 'test3.gif'

VIDEO_STEP = 10
GIF_FRAME_DURATION = 0.15
SIZE = (852, 480)

def create_gif(inputPath, outputPath, delay, finalDelay, loop):
    imagePaths = sorted(list(paths.list_images(inputPath)))

    lastPath = imagePaths[-1]
    imagePaths = imagePaths[:-1]
    cmd = "convert -delay {} {} -delay {} {} -loop {} {}".format(
            delay, " ".join(imagePaths), finalDelay, lastPath, loop,
            outputPath)
    print(cmd)
    os.system(cmd)


frames = []
video = cv2.VideoCapture(PATH)
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

with imageio.get_writer(OUTPUT_FILE, mode="I", duration=GIF_FRAME_DURATION) as writer:
    for i in range(0, frame_count - 1, VIDEO_STEP):
        video.set(1, i)
        ret, img = video.read()
        img = cv2.resize(img, SIZE, cv2.INTER_AREA)
        writer.append_data(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
