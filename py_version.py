import numpy as np
import cv2
import time

def callback(value):
    pass

def setup_trackbars():
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
        cv2.createTrackbar("%s_%s" % ("Threshold", i), "Trackbars", v, 255, callback)

def get_trackbar_values():
    values = []

    for i in ["MIN", "MAX"]:
        v = cv2.getTrackbarPos("%s_%s" % ("Threshold", i), "Trackbars")
        values.append(v)

    return values

def main():
    #cap = cv2.VideoCapture('D:\\Research\\Videos\\20-2.avi')
    cap = cv2.VideoCapture('C:\\Users\\Jefferson\\OneDrive - University of Pittsburgh\\Pitt\\2021 Fall\\Research\\m_code\\cell_tracking\\V4.avi')
    #cap.set(cv2.CAP_PROP_POS_FRAMES, 6000)
    if (cap.isOpened()== False):
      print("Error opening video stream or file")

    start_time = time.time()
    width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`

    numframes = 1000
    center = round(width/2)
    #print(center)
    slits_im = np.zeros((int(height),numframes), dtype='uint8')
    #print(np.shape(slits_im))
    for i in range(numframes):
        ret, frame = cap.read()
        fgray = frame[:,:,2]
        slit = fgray[:,center]
        slits_im[:,i] = slit
    
    slit_f = cv2.GaussianBlur(slits_im, (3, 3), 0)
    mean_col = np.mean(slit_f, axis=1)
    #print(slit_f.dtype); print(mean_col.dtype)
    #print(slit_f); print(mean_col)
    col_image = slit_f.copy()
    for i in range(numframes):
        col_image[:,i] = mean_col

    #slit_front = cv2.absdiff(slits_im, col_image)
    slit_front = cv2.subtract(slit_f, col_image)
    #norm_front = (255*(slit_front - np.min(slit_front))/np.ptp(slit_front))
    norm_front = cv2.normalize(slit_front,  None, 0, 255, cv2.NORM_MINMAX)

    T, threshInv = cv2.threshold(norm_front, 0, 255, cv2.THRESH_OTSU)
    cv2.imshow("OTSU", threshInv)
    print("--- %s seconds ---" % (time.time() - start_time))

    #(thresh, im_bw) = cv2.threshold(slit_f, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    #cv2.imshow("Slits_Image", slits_im)
    #cv2.imshow("front", slit_front)
    #print(slit_front)
    #cv2.imshow('FRAME',fgray)
        
    setup_trackbars()

    while True:
        t_min, t_max = get_trackbar_values()

        thresh = cv2.inRange(norm_front, t_min, t_max)
        cv2.imshow("Original", slits_im)
        cv2.imshow("Front", norm_front)
        cv2.imshow("Thresh", thresh)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            print("Chosen threshold: %s" % t_min)
            break

    cv2.destroyAllWindows()

    cap.release()

    #cap = cv2.VideoCapture('D:\\Research\\Videos\\20-2.avi')
    #if (cap.isOpened()== False):
        #print("Error opening video stream or file")


    


if __name__ == '__main__':
    main()