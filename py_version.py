from imutils.video import FileVideoStream
from imutils.video import FPS
from pathlib import Path
import numpy as np
import argparse
import cv2
import imutils
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import time

# Parameters
SAFE_THRESH = 60
MIN_THRESH = 25
FRAMES_PER_SLIT = 4000

# Globals
FRAMES_PER_SEC = 0
WIDTH, HEIGHT = 0, 0
SLIT_POS = 0
FRAME_COUNT = 0

def filterFrame(frame):
    try:
        fgray = frame[:,:,2]
        slit = fgray[:,SLIT_POS]
    except TypeError:
        print("[INFO] End of file reached...")
        return None
    return slit

# Get video file path from commandline args
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to input video file")
ap.add_argument("-d", "--debug", required=False, help="enable debug windows", default=False, type=bool)
#ap.add_argument("-o", "--output", required=False, help="Output file name as CSV (Ex: \"data_out.csv\"")
args = vars(ap.parse_args())
DEBUG_MODE = args["debug"]

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

# output array
raw_data = np.zeros((int(FRAME_COUNT),2), np.uint16)

# Open Video Stream
print("[INFO] starting video file thread...")
fvs = FileVideoStream(args["video"], transform=filterFrame).start()
time.sleep(1.0) # Let buffer fill up

# start the FPS timer
fps = FPS().start()
slits_im = np.zeros((int(HEIGHT),FRAMES_PER_SLIT), dtype='uint8')
i = 0
loop_count = 0
while fvs.running():
    slit = fvs.read()
    if slit is None:
        fvs.stop()
        break
    fps.update()
    slits_im[:,i] = slit
    fnum = loop_count * FRAMES_PER_SLIT + i
    raw_data[fnum][0] = fnum
    i += 1

    slit_length = 0
    run_flag = 0
    if (fnum == FRAME_COUNT - 1):
        true_count = int(FRAME_COUNT % FRAMES_PER_SLIT)
        slits_im = np.delete(slits_im, slice(int(true_count),int(FRAMES_PER_SLIT-1)), 1)
        slit_length = true_count
        run_flag = 2
    if (i == FRAMES_PER_SLIT):
        slit_length = FRAMES_PER_SLIT
        run_flag = 1
    
    if (run_flag != 0):
        #plt.hist(slits_im.ravel(),256,[0,256])
        #plt.show()
        #cv2.waitKey(0)

        # Denoise / Remove Background
        slit_f = cv2.GaussianBlur(slits_im, (5,5), 0)
        mean_col = np.mean(slit_f, axis=1)
        col_image = slit_f.copy()
        for i in range(int(slit_length)):
            col_image[:,i] = mean_col
        # Subtract Background + Normalize from 0-255
        slit_front = cv2.subtract(slit_f, col_image)
        norm_front = cv2.normalize(slit_front,  None, 255, 0, cv2.NORM_MINMAX)
        norm_front_f = cv2.GaussianBlur(norm_front, (5,5), 0)
        # Get OTSU Threshold
        T, otsu_f = cv2.threshold(norm_front_f, 0, 255, cv2.THRESH_OTSU)
        print("[INFO] Loop Count: %d\tThresh = %d\tFrame Num: %d" % (loop_count,T,fnum))
        # Increase Threshold if below minimum
        if (T < MIN_THRESH): T = SAFE_THRESH
        thresh_f = cv2.inRange(norm_front_f, T, 255)

        # Morphological Open
        kernel = np.ones((3,3),np.uint8)
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
                raw_data[loop_count * FRAMES_PER_SLIT + cX][1] += 1
            else:
                cX, cY = 0, 0

        if (DEBUG_MODE):
            cv2.imshow("Original", og_copy)
            cv2.imshow("Front", norm_front)
            cv2.imshow("open_f", open_f)
            cv2.waitKey(0)

        # Reset variables for next batch
        slits_im.fill(0)
        i = 0
        loop_count += 1

        if (run_flag == 2):
            fvs.stop()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# Get Sec and Total data
total_cells = 0
total_sec = math.ceil(FRAME_COUNT / FRAMES_PER_SEC)
sec_data = np.zeros((int(total_sec),2), np.uint16)
tot_data = np.zeros((int(total_sec),2), np.uint16)
for row in raw_data:
    sec_data[math.floor(row[0] / FRAMES_PER_SEC)][1] += row[1]
    total_cells += row[1]
for i in range(int(total_sec)):
    sec_data[i][0] = i
    tot_data[i][0] = i
    if (i == 0):
        tot_data[i][1] = sec_data[i][1]
    else:
        tot_data[i][1] = sec_data[i][1] + tot_data[i-1][1]
print("[INFO] Total cells: %d" % total_cells)

# Save Raw data and Sec data to csv files
Path("./output").mkdir(exist_ok=True)

out_raw = "./output/" + Path(args["video"]).stem + "_raw"
out_sec = "./output/" + Path(args["video"]).stem + "_sec"
out_tot = "./output/" + Path(args["video"]).stem + "_tot"
np.savetxt(out_raw + ".csv", raw_data, delimiter=",", fmt="%d")
np.savetxt(out_sec + ".csv", sec_data, delimiter=",", fmt="%d")
np.savetxt(out_tot + ".csv", tot_data, delimiter=",", fmt="%d")
print("[INFO] Raw data saved to: %s" % (out_raw + ".csv"))
print("[INFO] Per Second data saved to: %s" % (out_sec + ".csv"))
print("[INFO] Cumulative Totals saved to: %s" % (out_tot + ".csv"))

# Save graph outputs of raw data and sec data
x,y = raw_data.T
plt.plot(x,y)
plt.title("Cells per Frame")
plt.xlabel("Frame Number")
plt.ylabel("Cells Counted")
plt.savefig((out_raw + ".png"), bbox_inches='tight')

plt.close()
x,y = sec_data.T
plt.plot(x,y)
plt.title("Cells per Second")
plt.xlabel("Time (t)")
plt.ylabel("Cells Counted")
plt.savefig((out_sec + ".png"), bbox_inches='tight')

plt.close()
x,y = tot_data.T
plt.plot(x,y)
plt.title("Cumulative Cells per Second")
plt.xlabel("Time (t)")
plt.ylabel("Total Cells Counted")
plt.savefig((out_tot + ".png"), bbox_inches='tight')

if (DEBUG_MODE):
    cv2.waitKey(0)
cv2.destroyAllWindows()
fvs.stop()
quit()