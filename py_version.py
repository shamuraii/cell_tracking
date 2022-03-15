from imutils.video import FileVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import cv2
import imutils
import time

# Parameters
SAFE_THRESH = 60
MIN_THRESH = 25
FRAMES_PER_SLIT = 1000

# Globals
FRAMES_PER_SEC = 0
WIDTH, HEIGHT = 0, 0
SLIT_POS = 0
FRAME_COUNT = 0

def filterFrame(frame):
    fgray = frame[:,:,2]
    slit = fgray[:,SLIT_POS]
    return slit

# speed up data reading
# https://github.com/PyImageSearch/imutils/blob/master/demos/read_frames_fast.py
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to input video file")
args = vars(ap.parse_args())

print("Gathering Video Information...")
cap = cv2.VideoCapture(args["video"])
if (cap.isOpened()== False):
    print("Error opening video stream or file")
    quit()

# Gather Video Details / Constants
WIDTH  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
FRAMES_PER_SEC = cap.get(cv2.CAP_PROP_FPS)
SLIT_POS = round(WIDTH/2)
FRAME_COUNT = cap.get(cv2.CAP_PROP_FRAME_COUNT)
duration = (FRAME_COUNT / FRAMES_PER_SEC) / 60
print("Width: %d\nHeight: %d\nFPS: %s\nSlit Pos: %d\nFrame Count: %d\nDuration: %0.2f min" % (WIDTH,HEIGHT,FRAMES_PER_SEC,SLIT_POS,FRAME_COUNT,duration))
cap.release()

# Open Video Stream
print("[INFO] starting video file thread...")
fvs = FileVideoStream(args["video"], transform=filterFrame).start()
time.sleep(1.0) # Let buffer fill up

# start the FPS timer
fps = FPS().start()
slits_im = np.zeros((int(HEIGHT),FRAMES_PER_SLIT), dtype='uint8')
i = 0
while fvs.running():
    slit = fvs.read()
    slits_im[:,i] = slit
    fps.update()
    i += 1
    if (i == FRAMES_PER_SLIT):
        # Denoise / Remove Background
        slit_f = cv2.fastNlMeansDenoising(slits_im,None,3,7,21)
        mean_col = np.mean(slit_f, axis=1)
        col_image = slit_f.copy()
        for i in range(FRAMES_PER_SLIT):
            col_image[:,i] = mean_col
        # Subtract Background + Normalize from 0-255
        slit_front = cv2.subtract(slit_f, col_image)
        norm_front = cv2.normalize(slit_front,  None, 0, 255, cv2.NORM_MINMAX)
        # Get OTSU Threshold
        T, otsu_f = cv2.threshold(norm_front, 0, 255, cv2.THRESH_OTSU)
        print("[INFO] Thresh = %s" % T)
        # Increase Threshold if below minimum
        if (T < MIN_THRESH): T = SAFE_THRESH
        thresh_f = cv2.inRange(norm_front, T, 255)

        # Morphological Open
        kernel = np.ones((2,2),np.uint8)
        open_f = cv2.morphologyEx(thresh_f, cv2.MORPH_OPEN, kernel)

        og_copy = slit_f.copy()
        # Get Countours from opened image
        cnts = cv2.findContours(open_f, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0]
        for c in cnts:
            # calculate moments for each contour
            M = cv2.moments(c)

            # calculate x,y coordinate of center
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(og_copy, (cX, cY), 3, (255, 255, 255), -1)
            else:
                cX, cY = 0, 0

        cv2.imshow("Original", og_copy)
        cv2.imshow("Front", norm_front)
        cv2.imshow("open_f", open_f)

        # Reset variables for next batch
        slits_im.fill(0)
        i = 0
        break


# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.waitKey(0)
cv2.destroyAllWindows()
fvs.stop()
quit()