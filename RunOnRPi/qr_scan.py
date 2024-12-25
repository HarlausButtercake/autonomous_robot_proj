import time

import cv2
import numpy as np

# set up camera object
cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()
cv2.namedWindow('Window', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Window', 500, 500)
cv2.setWindowProperty('Window', cv2.WND_PROP_FULLSCREEN, 0)
start_time = time.time()
data = None
while time.time() - start_time < 30:
    # get the image
    _, img = cap.read()
    # get bounding box coords and data
    data, bbox, _ = detector.detectAndDecode(img)

    # if there is a bounding box, draw one, along with the data
    if bbox is not None:
        bbox = bbox.reshape((4, 2))
        bbox = np.int32(bbox)

        for i in range(len(bbox)):
            try:
                cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i + 1) % len(bbox)][0]), color=(255,
                                                                                             0, 255), thickness=2)
                cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
            except Exception as e:
                # print(e)
                pass
        # if data:
        #     print("FOUND: ", data)
            # if


    cv2.moveWindow('Window', 0, 0)
    cv2.imshow("Window", img)
    if (cv2.waitKey(1) == ord("q")) or data:
        print(data)
        break
if not data:
    print("NO_QR_SCANNED")
cap.release()
cv2.destroyAllWindows()