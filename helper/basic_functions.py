

database = dict()

database['convert color'] = {
'Description':
'',
'Example 1' :
'image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)',
'Example 2' :
'image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)',
'Example 3' :
'image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)'}

database['clip clamp interval'] = {
'Description':
'',
'Example 1' :
'x = np.clip(y, min, max)'}

database['empty image create'] = {
'Description':
'',
'Example 1' :
'image = np.zeros((1920, 1080, 3), np.uint8)'}

database['rotate image'] = {
'Description':
'',
'Example 1' :
'image = imutils.rotate(image, 15)'}

database['flip image'] = {
'Description':
'',
'Example 1' :
'image = cv2.flip(image, 0)'}

database['erode erosion'] = {
'Description':
'',
'Example 1' :
'image = cv2.erode(image, np.ones((5, 5), np.uint8), iterations=3)'}

database['dilate dilation'] = {
'Description':
'',
'Example 1' :
'image = cv2.dilate(image, np.ones((5, 5), np.uint8), iterations=6)'}

database['medianBlur'] = {
'Description':
'',
'Example 1' :
'image = cv2.medianBlur(image, 15)'}

database['contour find'] = {
'Description':
'',
'Example 1' :
'''
contours, h = cv2.findContours(image,
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
            
cnts = imutils.grab_contours((contours, h))

(x, y, w, h) = cv2.boundingRect(cnts[contour_ind])
'''}

database['contour draw'] = {
'Description':
'',
'Example 1' :
'''
cv2.drawContours(image=image,
                 contours=contours,
                 contourIdx=contour_ind,
                 color=(255, 255, 255),
                 thickness=-1,
                 lineType=cv2.LINE_AA)
'''}

database['resize'] = {
'Description':
'',
'Example 1' :
'image = cv2.resize(image, (1920, 1080), interpolation = cv2.INTER_AREA)'}

database['resize'] = {
'Description':
'',
'Example 1' :
'ret, mask = cv2.threshold(image, 230, 255, cv2.THRESH_BINARY_INV)'}

database['combine images stack'] = {
'Description':
'',
'Example [vertical]' :
'result = np.vstack([image1, image2])',
'Example [horizontal]' :
'result = np.hstack([image1, image2])',
'Example [depth]' :
'result = np.dstack([image1, image2])'}



database['makedirs'] = {
'Description':
'',
'Example 1' :
'''
if not os.path.exists(path):
    os.makedirs(path)'''}

database['rename file'] = {
'Description':
'',
'Example 1' :
'os.rename(name_from, name_to)'}
