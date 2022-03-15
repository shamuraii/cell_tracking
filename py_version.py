import numpy as np
import cv2
import time

def callback(value):
    pass

def setup_trackbars():
    cv2.namedWindow("Trackbars", 0)
    cv2.createTrackbar("Threshold", "Trackbars", 0, 255, callback)
    cv2.createTrackbar("Kernel_Size", "Trackbars", 0, 25, callback)

def get_trackbar_values():
    values = []

    for i in ["Threshold", "Kernel_Size"]:
        v = cv2.getTrackbarPos(i, "Trackbars")
        values.append(v)

    return values

def main():
    #cap = cv2.VideoCapture('D:\\Research\\Videos\\20-2.avi')
    cap = cv2.VideoCapture('C:\\Users\\Jefferson\\OneDrive - University of Pittsburgh\\Pitt\\2021 Fall\\Research\\m_code\\cell_tracking\\V4.avi')
    #cap.set(cv2.CAP_PROP_POS_FRAMES, 6000)
    if (cap.isOpened()== False):
      print("Error opening video stream or file")
      quit()

    start_time = time.time()
    width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`

    numframes = 1000
    center = round(width/2)
    slits_im = np.zeros((int(height),numframes), dtype='uint8')
    for i in range(numframes):
        ret, frame = cap.read()
        fgray = frame[:,:,2]
        slit = fgray[:,center]
        slits_im[:,i] = slit
    
    #slit_f = cv2.GaussianBlur(slits_im, (5,5), 0)
    slit_f = cv2.fastNlMeansDenoising(slits_im,None,3,7,21)
    mean_col = np.mean(slit_f, axis=1)
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
        t_min, k_size = get_trackbar_values()

        thresh = cv2.inRange(norm_front, t_min, 255)
        kernel = np.ones((k_size,k_size),np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        og_copy = slit_f.copy()
        cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0]
        for c in cnts:
            # calculate moments for each contour
            M = cv2.moments(c)

            # calculate x,y coordinate of center
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            cv2.circle(og_copy, (cX, cY), 3, (255, 255, 255), -1)

        cv2.imshow("Original", og_copy)
        cv2.imshow("Front", norm_front)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Opening", opening)

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