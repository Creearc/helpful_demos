import os
import cv2
import imageio

PATH = 'E:/slides/Tue_Dec_20_10_40_31_2022.mp4'
OUTPUT_FILE = 'test2.gif'

VIDEO_STEP = 1
GIF_FRAME_dDURATION = 0.5

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

with imageio.get_writer(OUTPUT_FILE, mode="I", duration=GIF_FRAME_dDURATION) as writer:
    for i in range(10, frame_count - 1, VIDEO_STEP):
        video.set(1, i)
        ret, img = video.read()
        writer.append_data(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
