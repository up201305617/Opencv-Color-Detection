import numpy as np
import cv2.cv2 as cv

top_left_pt = (-1,-1)
bottom_right_pt = (-1,-1)
mouse_position = (-1,-1)

def nothing(x):
  pass

# reset points of the ROI rectangle
def resetPoints():
    global top_left_pt, bottom_right_pt
    top_left_pt = (-1,-1)
    bottom_right_pt = (-1,-1)

# select a ROI with mouse
def selectROI(event,x,y,flags,param):

    global top_left_pt, bottom_right_pt
    global x_initial, y_initial
    global mouse_position
    selecting = False 

    if event == cv.EVENT_LBUTTONDOWN:
        x_initial = x
        y_initial = y
        selecting = True
    elif event == cv.EVENT_MOUSEMOVE:
        mouse_position = (x,y)
        if selecting:
            top_left_pt = (min(x_initial, x), min(y_initial, y))
            bottom_right_pt = (max(x_initial, x), max(y_initial, y))
    elif event == cv.EVENT_LBUTTONUP:
        selecting = False
        top_left_pt = (min(x_initial, x), min(y_initial, y))
        bottom_right_pt = (max(x_initial, x), max(y_initial, y))

# return a string with the color name based on HSV values
def getColor(h,s,v):
    
    if(v < 0.1):
         return "Preto"
    elif (s < 0.15 and v > 0.65):
        return "Branco"
    elif (s< 0.15 and (0.1<v and v<0.65)):
        return "Cinzento"
    elif ((h<11 or h>351) and s > 0.7 and v>0.3):
        return "Vermelho"
    elif (310 < h and h<351 and s>0.5 and v>0.5):
        return "Rosa"
    elif ((h<11 or h>351) and s<0.7 and v >0.2):
        return "Rosa"
    elif (11<h and h<45 and s >0.25 and v >0.8):
        return "Laranja"
    elif (11<h and h<45 and s >0.25 and 0.1<v and v<0.75):
        return "Castanho"
    elif (45<h and h<64 and s >0.2 and v >0.2):
        return "Amarelo"
    elif (64<h and h<150 and s>0.20 and v>0.2):
        return "Verde"
    elif (150<h and h<180 and s>0.2 and v >0.2):
        return "Azul Esverdeado"
    elif (180 < h and h<255 and s>0.2 and v >0.2):
        return "Azul"
    elif (255 <h and h<310 and s >0.5 and v>0.2):
        return "Roxo"
    elif (255 < h and h < 310 and 0.15 < s and s < 0.5 and v > 0.2):
        return "Roxo Claro"
    else:
        return "Desconhecida"

# calculate the RGB average of a given frame
def frameAverage(frame):
    
    height,width,_ = frame.shape
    avg_R=0
    avg_G=0
    avg_B=0
    count = 0

    for i in range(height):
        for j in range(width):
            avg_R += frame[i][j][2]
            avg_G += frame[i][j][1]
            avg_B += frame[i][j][0]
            count += 1
    
    if(count !=0):
        avg_R = avg_R / count
        avg_G = avg_G / count
        avg_B = avg_B / count
    else:
        resetPoints()
    
    return avg_R, avg_G, avg_B

# convert RGB to HSV
def rgb2hsv(r,g,b):

    r, g, b = r/255.0, g/255.0, b/255.0
    cmax = max(r,g,b)
    cmin = min(r,g,b)
    delta = cmax-cmin
    
    if cmax == cmin:
        h = 0
    elif cmax == r:
        h = (60 * ((g-b)/delta) + 360) % 360
    elif cmax == g:
        h = (60 * ((b-r)/delta) + 120) % 360
    elif cmax == b:
        h = (60 * ((r-g)/delta) + 240) % 360

    if cmax == 0:
        s = 0
    else:
        s = delta/cmax
    
    v = cmax

    return h, s, v

# calcute the color of a given ROI
def calculateColor(roi):

    r,g,b = frameAverage(roi)
    h,s,v = rgb2hsv(r,g,b)
    color = getColor(h,s,v)
    
    return color

# main function
def main():

    window_name = "Webcam"
    trackbar_name = "Size"

    cap = cv.VideoCapture(0)

    cv.namedWindow(window_name) 

    cv.setMouseCallback(window_name,selectROI)

    cv.createTrackbar(trackbar_name,window_name,10,50,nothing)

    window_top_left_pt = (0,0)
    window_bottom_right_pt = (0,0)

    while(True):
        
        ret, frame = cap.read()

        if ret == False:
            break

        output = frame
    
        size = cv.getTrackbarPos(trackbar_name,window_name)
        mouse_rectangle_dimension = size
        
        if top_left_pt[0] != -1 or bottom_right_pt[0] != -1:
            cv.rectangle(output,(top_left_pt[0]-1,top_left_pt[1]-1),(bottom_right_pt[0]+1,bottom_right_pt[1]+1),(0,0,255),1)
            mouseROI = frame[top_left_pt[1]:bottom_right_pt[1],top_left_pt[0]:bottom_right_pt[0]]
            m_color = calculateColor(mouseROI)
            cv.putText(output,m_color,(top_left_pt[0],top_left_pt[1]-5),cv.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
        else:
            cv.rectangle(output,top_left_pt,bottom_right_pt,(0,0,255),0)

        window_top_left_pt = (mouse_position[0]-mouse_rectangle_dimension,mouse_position[1]+mouse_rectangle_dimension)
        window_bottom_right_pt = (mouse_position[0]+mouse_rectangle_dimension,mouse_position[1]-mouse_rectangle_dimension)
        
        cursorROI = output[window_bottom_right_pt[1]:window_top_left_pt[1],window_top_left_pt[0]:window_bottom_right_pt[0]]
        
        height,width,_ = cursorROI.shape
        if height > 0 and width > 0:
            cv.imshow("Cursor ROI",cursorROI)
        
        cv.rectangle(output,window_top_left_pt,window_bottom_right_pt,(0,0,255),1)
        
        window_color = calculateColor(cursorROI)
        cv.putText(output,window_color,(window_top_left_pt[0],window_top_left_pt[1]+25),cv.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
        
        cv.imshow(window_name, output)

        k = cv.waitKey(1) & 0xFF

        if k == ord('q'):
            break

        if k == ord('c'):
            resetPoints()

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()