import cv2
import imutils
import numpy as np
from modules import video_module
import json


def restruct_region(region):
    return (region[0], region[1], region[0] + region[2], region[1] + region[3])


def extract_region_from_img(img, region):
    return img.copy()[region[1]: region[3], region[0]: region[2]]


def replace_region_from_img(img, new_part, region):
    #new_part = cv2.cvtColor(new_part, cv2.COLOR_GRAY2BGR)
    img[region[1]:region[3], region[0]:region[2]] = new_part
    return img


def rotate_img(img, angle):
    (h, w) = img.shape[:2]
    (cX, cY) = (w//2, h//2)
    m = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    return cv2.warpAffine(img, m, (w, h))


def fix_collision(image):

    """
    camera_matrix = np.array([[1.75977641e+03, 0.00000000e+00, 2.01115728e+03],
                              [0.00000000e+00, 1.74776016e+03, 1.47151927e+03],
                              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist_coefs = np.array([-0.25099909,  0.08783225,  0.00517914,  0.00276792, -0.03165758])

    camera_matrix = np.array([[552.96835229,   0.,         641.40396193],
                              [  0.,         587.82320188, 356.31799613],
                              [  0.,           0.,           1.        ]])
    dist_coefs = np.array([-0.26961139,  0.14805475,  0.00131773, -0.00173458, -0.08004486])
    """
    camera_matrix = np.array([[1.65860429e+03, 0.00000000e+00, 1.92502145e+03],
                              [0.00000000e+00, 1.76279078e+03, 1.06850525e+03],
                              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist_coefs = np.array([-0.26573577,  0.1363063,   0.00139622, -0.00174522, -0.07017501])

    h, w = image.shape[:2]
    # New Image shape to generate
    w1, h1 = w, h
    # w1, h1 = 5 * w, 5 * h

    # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w1, h1))
    # mapx, mapy = cv2.initUndistortRectifyMap(camera_matrix, dist_coefs, None, newcameramtx, (w1, h1), 5)
    # dst = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

    dst = cv2.undistort(image, camera_matrix, dist_coefs, None, None)

    # x, y, w, h = roi
    # x += 200
    # dst = dst[y:y + h, x:x + w]
    # print(dst.shape)
    return dst


def cals_sizes(gray, th):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((7, 7), np.uint8)
    # gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel=kernel)
    gray = cv2.erode(gray, kernel, iterations=5)
    gray = cv2.dilate(gray, kernel, iterations=5)

    # gray = cv2.medianBlur(gray, 3)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    _, gray = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)

    count = cv2.countNonZero(gray)

    return gray, count


def print_text(img, text, coords=(0, 0), color=(255, 255, 255),
               size=1.6, thikness=5):
    cv2.putText(img, str(text), coords,
                cv2.FONT_HERSHEY_SIMPLEX, size,
                (0, 0, 0), thikness * 4)
    cv2.putText(img, str(text), coords,
                cv2.FONT_HERSHEY_SIMPLEX, size,
                color, thikness)


def get_config(config_path):
    with open('data/confs/{}.json'.format(config_path), encoding="utf8") as config_file:
        config_file_json = json.load(config_file)
    return config_file_json


def hsv_filter(img, h1=20, s1=10, v1=0, h2=70, s2=100, v2=100):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h1 = np.interp(h1, [0, 360], [0, 255])
    s1 = np.interp(s1, [0, 100], [0, 255])
    v1 = np.interp(v1, [0, 100], [0, 255])
    h2 = np.interp(h2, [0, 360], [0, 255])
    s2 = np.interp(s2, [0, 100], [0, 255])
    v2 = np.interp(v2, [0, 100], [0, 255])

    h_min = np.array((h1, s1, v1), np.uint8)
    h_max = np.array((h2, s2, v2), np.uint8)
    thresh = cv2.inRange(hsv, h_min, h_max)
    return thresh


def count_short_parts(gr, count_long, count_short):
    # gr = cv2.threshold(gr.copy(), 0, 255, cv2.THRESH_BINARY)[1]
    cnts = cv2.findContours(gr.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    if len(cnts) != 0:
        for cnt in cnts:
            (x, y, w, h) = cv2.boundingRect(cnt)
            print((x, y, w, h))
            if w > 240:
                count_long += 1
            else:
                count_short += 1
    return count_long, count_short


def nothing(*arg):
    pass


config_num = "20190112050754_0003"
config = get_config(config_num)
rec = not True

cv2.namedWindow("wait_key", cv2.WINDOW_NORMAL)
cv2.moveWindow("wait_key", 0, 700)
cv2.resizeWindow("wait_key", 300, 8)
cv2.createTrackbar('wait_key', 'wait_key', 1, 50, nothing)
wait_key = 1

SCALE_REGION = restruct_region(config["region"])
max_px = SCALE_REGION[2]

coef = int(5900/max_px)
arr_len = 3
out_pr = 0
out_pr_list = 0
arr = [0 for i in range(arr_len)]
arr_list = [0 for j in range(arr_len)]

old_perc = 0
count_long = 0
count_short = 0

if __name__ == '__main__':
    path = config["path"]
    c = video_module.Video(path)

    if rec:
        rec_name = '{}_out.mp4'.format(config_num)
        forucc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        out_video = cv2.VideoWriter(rec_name, forucc, c.frame_rate, (1280, 720))

    if "last_frame" in config.keys():
        last_frame = config["last_frame"]
    else:
        last_frame = c.frame_count

    for frame_number, orig in c.get_img(first_frame=config["first_frame"], last_frame=last_frame):
        cv2.resizeWindow("wait_key", 300, 8)
        wait_key = cv2.getTrackbarPos('wait_key', 'wait_key')

        # orig = fix_collision(orig)
        orig = rotate_img(orig, config["angle"])
        orig = cv2.resize(orig, (1280, 720), interpolation=cv2.INTER_AREA)

        hsv = hsv_filter(orig)

        tmp = extract_region_from_img(hsv, SCALE_REGION)
        # gr = tmp
        # gr, count = cals_sizes_blue(tmp, config["th"])
        gr, count = cals_sizes(tmp, config["th"])

        if cv2.countNonZero(gr[:, :config["left_edge"]])>config["left_edge"]//2:
            print_text(orig, '!', coords=(config["left_edge"]//2, SCALE_REGION[1]-10),
                       size=2, color=(0, 0, 255), thikness=2)

        if cv2.countNonZero(gr[:, -config["right_edge"]:])>config["right_edge"]//2:
            print_text(orig, '!',
                       coords=(SCALE_REGION[0] + SCALE_REGION[2] - config["left_edge"]//2, SCALE_REGION[1]-10),
                       size=2, color=(0, 0, 255), thikness=2)


        """
        if int(cnt*coef) > 500:
            print_text(orig, '{} mm'.format(int(cnt*coef)), coords=(25, 40), size=1, color=(0, 255, 0), thikness=2)
        else:
            print_text(orig, '{} mm'.format(0), coords=(25, 40), size=1, color=(0, 255, 0), thikness=2)
        """
        perc = int(count/max_px*100)
        arr.insert(0, perc)
        arr.pop(-1)

        perc_list = int(count / config["max_px"] * 100)
        arr_list.insert(0, perc_list)
        arr_list.pop(-1)

        out_pr = perc if abs(sum(arr, 0)/len(arr) - perc) < 2 else out_pr
        out_pr_list = perc_list if abs(sum(arr_list, 0)/len(arr_list) - perc_list) < 2 else out_pr_list

        # """
        if out_pr_list - old_perc > 5 and old_perc == 0:
            count_long, count_short = count_short_parts(gr, count_long, count_short)
        old_perc = out_pr_list
        # """

        if out_pr_list > 93:
            out_pr_list = 100

        gr = cv2.cvtColor(gr, cv2.COLOR_GRAY2BGR)

        orig = replace_region_from_img(orig, gr, SCALE_REGION)

        # print(frame_number)
        # print(count)
        # print(out_pr_list)
        # print(' ')

        # mm_out_pr = out_pr / 100 * 5900
        # print(mm_out_pr)

        if count_long != 0:
            sh_pr = int(count_short/count_long * 100)
        else:
            sh_pr = 0

        print_text(orig, '{}%'.format(out_pr), coords=(25, 40), size=1,  color=(0, 255, 0), thikness=2)
        print_text(orig, '{}%_list'.format(out_pr_list), coords=(25, 80), size=1, color=(0, 255, 0), thikness=2)
        print_text(orig, '{}%'.format(sh_pr),
                   coords=(25, 120), size=1, color=(255, 0, 0), thikness=2)
        print_text(orig, 'sh = {}'.format(count_short),
                   coords=(25, 160), size=1, color=(255, 0, 0), thikness=2)
        print_text(orig, 'l = {}'.format(count_long),
                   coords=(25, 200), size=1, color=(255, 0, 0), thikness=2)

        cv2.imshow('img', orig)

        if rec:
            out_video.write(orig)

        key = cv2.waitKey(wait_key)
        if key == ord('s'):
            bbox = cv2.selectROI("img", orig, fromCenter=False, showCrosshair=True)
            print(bbox)
        elif key == 27:
            break
        elif key == ord('a'):
            cv2.waitKey(0)

    c.stop()
    if rec:
        out_video.release()
    cv2.destroyAllWindows()
