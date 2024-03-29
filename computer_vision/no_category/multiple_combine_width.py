import cv2
import numpy as np
import imageio
import imutils
import time

def detectAndDescribe(image, method=None):
    """
    Compute key points and feature descriptors using an specific method
    """
    assert method is not None, "You need to define a feature detection method. Values are: 'sift', 'surf'"
    
    # detect and extract features from the image
    if method == 'sift':
        descriptor = cv2.xfeatures2d.SIFT_create()
    elif method == 'surf':
        descriptor = cv2.xfeatures2d.SURF_create()
    elif method == 'brisk':
        descriptor = cv2.BRISK_create()
    elif method == 'orb':
        descriptor = cv2.ORB_create()
        
    # get keypoints and descriptors
    (kps, features) = descriptor.detectAndCompute(image, None)
    #print((kps, features))
    
    return (kps, features)


def createMatcher(method,crossCheck):
    "Create and return a Matcher Object"
    
    if method == 'sift' or method == 'surf':
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=crossCheck)
    elif method == 'orb' or method == 'brisk':
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=crossCheck)
    return bf


def matchKeyPointsBF(featuresA, featuresB, method):
    bf = createMatcher(method, crossCheck=True)
        
    # Match descriptors.
    best_matches = bf.match(featuresA,featuresB)
    
    # Sort the features in order of distance.
    # The points with small distance (more similarity) are ordered first in the vector
    rawMatches = sorted(best_matches, key = lambda x:x.distance)
    print("Raw matches (Brute force):", len(rawMatches))
    return rawMatches


def matchKeyPointsKNN(featuresA, featuresB, ratio, method):
    bf = createMatcher(method, crossCheck=False)
    # compute the raw matches and initialize the list of actual matches
    #print(featuresA, featuresB)
    #print(' ')
    if featuresA is None or featuresB is None:
        return None
    else:
        rawMatches = bf.knnMatch(featuresA, featuresB, 2)
        print("Raw matches (knn):", len(rawMatches))
        matches = []

        # loop over the raw matches
        for m,n in rawMatches:
            # ensure the distance is within a certain ratio of each
            # other (i.e. Lowe's ratio test)
            if m.distance < n.distance * ratio:
                matches.append(m)
        return matches


def getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh):
    # convert the keypoints to numpy arrays
    kpsA = np.float32([kp.pt for kp in kpsA])
    kpsB = np.float32([kp.pt for kp in kpsB])

    if len(matches) > 4:

        # construct the two sets of points
        ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
        ptsB = np.float32([kpsB[m.trainIdx] for m in matches])

        # estimate the homography between the sets of points
        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
            reprojThresh)

        return (matches, H, status)
    else:
        return None


def combine(img1, img2, out, pos, rewrite = False, exp_step = 150, feature_extractor = 'orb', feature_matching = 'knn'):
    trainImg = img1
    trainImg_gray = cv2.cvtColor(trainImg, cv2.COLOR_RGB2GRAY)
    queryImg = img2
    queryImg_gray = cv2.cvtColor(queryImg, cv2.COLOR_RGB2GRAY)

    kpsA, featuresA = detectAndDescribe(trainImg_gray, method=feature_extractor)
    kpsB, featuresB = detectAndDescribe(queryImg_gray, method=feature_extractor)

    if feature_matching == 'bf':
        matches = matchKeyPointsBF(featuresA, featuresB, method=feature_extractor)
    elif feature_matching == 'knn':
        matches = matchKeyPointsKNN(featuresA, featuresB, ratio=0.8, method=feature_extractor)


    if matches is None:
        return out, pos

    kpsA = np.float32([kp.pt for kp in kpsA])
    kpsB = np.float32([kp.pt for kp in kpsB])
    
    disp_x = 0
    counter = 0
    if len(matches) > 4:
        ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
        ptsB = np.float32([kpsB[m.trainIdx] for m in matches])

        # max_d = 0
        for m in matches:
            if m.queryIdx == m.trainIdx:
                if kpsA[m.queryIdx][0] != kpsB[m.trainIdx][0]:
                    x1, x2 = kpsA[m.queryIdx][0], kpsB[m.trainIdx][0]
                    # y1, y2 = kpsA[m.queryIdx][1], kpsB[m.trainIdx][1]
                    disp_x = disp_x + abs(x2-x1)
                    # disp_x = abs(x2-x1)
                    # disp_y = y1-y2 # abs(y2-y1)
                    counter += 1
        if counter > 0:
            disp_y = disp_y // counter


    if pos + disp_x + queryImg.shape[1] > out.shape[1]:
        if rewrite:
            out = out * 0
            pos = 0
            disp_x = 0
        else:
            new_out = np.zeros((out.shape[0], out.shape[1] + exp_step, 3), np.uint8)
            new_out[:,:out.shape[1]] = out
            out = new_out

    # print(int(pos + disp_x), int(pos + disp_x + queryImg.shape[1]), out.shape[1])
    # print(int(disp_y))

    '''
    if disp_y >= 0: 
        out[int(disp_y):, int(pos + disp_x):int(pos + disp_x + queryImg.shape[1])] = queryImg[:queryImg.shape[0]-int(disp_y),:]
    else:
        out[:int(disp_y), int(pos + disp_x):int(pos + disp_x + queryImg.shape[1])] = queryImg[-int(disp_y):,:]
    # '''
    
    out[:, int(pos + disp_x):int(pos + disp_x + queryImg.shape[1])] = queryImg[:,:]
    # out[:, int(pos + disp_x):int(pos + disp_x + queryImg.shape[1]-4)] = queryImg[:,2:-2]
    pos += disp_x

    return out, pos
    

if __name__ == '__main__':

    def rotate_img(img, angle):
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h))

    def getCoordinatesOfRectangle(x, y, height, width):
        first = x
        second = y
        third = x + width
        fourth = y + height
        return first, second, third, fourth

    feature_extractor = 'orb' 
    feature_matching = 'knn'

    video_name = 'D:/КАНДИДАТСКАЯ ДИССЕРТАЦИЯ/Helpfull Demos/341/TestData/VID_20220305_140251_cropped.mp4'
    cap = cv2.VideoCapture(video_name)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  

    first, second, third, fourth = getCoordinatesOfRectangle(150, 100, 500, 500)
    result = np.zeros((fourth - second, third - first+500, 3), np.uint8)
    boundingBox_old = None
    pos = 0
    start_combine = None

    while cap.isOpened():
        ret, img = cap.read()
        # img = rotate_img(img, 180)
        boundingBox = img[second:fourth, first:third]

        if start_combine is None:
            result[:,:boundingBox.shape[1]] = boundingBox
            boundingBox_old = boundingBox
            start_combine = 1
        else:
            tmp, pos = combine(boundingBox_old, boundingBox, result, pos, exp_step = 150)
            if not (tmp is None):
                result = tmp.copy()

        cv2.imshow('', result)

        boundingBox_old = boundingBox

        key = cv2.waitKey(100)
        if key & 0xFF == ord('q') or key & 0xFF == 27:
            break
        elif key ==ord('s'):
            bbox = cv2.selectROI('img', img, fromCenter=False, showCrosshair=True)
            print(bbox)
        elif key ==ord('a'):
            cv2.waitKey(0)

    cv2.destroyAllWindows()
