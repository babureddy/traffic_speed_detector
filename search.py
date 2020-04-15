import sys
import cv2 as cv
import numpy as np
import pytesseract 
import glob
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
sum=0

def main(filename,disp=False):
    # Load an image in color mode
    src = cv.imread(filename, cv.IMREAD_COLOR)
    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        print ('Usage: hough_circle.py [image_name -- default ' + default_file + '] \n')
        return -1    
    gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 5)    
    rows = gray.shape[0]
    minRadius = 20
    maxRadius = 50
    if filename.startswith('GoldStandards'):
        minRadius = 20
        maxRadius = 0
    elif filename.startswith('stress_dataset'):
        minRadius = 10
        maxRadius = 40
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8,
                               param1=100, param2=30,
                               minRadius=minRadius, maxRadius=maxRadius)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv.circle(src, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv.circle(src, center, radius, (255, 0, 255), 3)
            x,y,r = i[0], i[1], i[2]
            rectX = (x - r) 
            # rectY = int((y - r) * 0.9) # reduce height
            rectY = (y - r) 
            crop_img = src[rectY:(rectY+2*r), rectX:(rectX+2*r)]
            crop_img[:,:,2] = 0 # remove red color
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            try:
                crop_img = cv2.filter2D(crop_img, -1, kernel)
            except:
                pass
            # cv.imshow("cropped circle", crop_img)
            config = ("-l eng --oem 1 --psm 9")
            try:
                text = pytesseract.image_to_string(crop_img, config=config)
                filename = filename.lower()
                text = text.replace('-','').replace('(','').replace(')','')
                print(filename,',', text,',',1) 
                if text.isdigit() : 
                    # print(filename,',', text,',',1) 
                    global sum
                    sum += 1
            except :
                pass
    if disp:
        cv.imshow("detected circles", src)
        cv.waitKey(0)
    return 0
if __name__ == "__main__":
    count=0
    # print(len(sys.argv))
    if len(sys.argv) == 1:
        for name in glob.glob('development_dataset/*/*.jpg',recursive=True): 
            count += 1
            main(name)
        for name in glob.glob('GoldStandards/*.jpg',recursive=False): 
            count += 1
            main(name)
        for name in glob.glob('stress_dataset/*.TIF',recursive=False): 
            count += 1
            main(name)        
        accuracy = (sum/count) * 100
        print('Images',count,'Accuracy',accuracy)
    elif len(sys.argv) == 2 and sys.argv[1] == '0':
        for name in glob.glob('development_dataset/*/*.jpg',recursive=True): 
            count += 1
            main(name)
        accuracy = (sum/count) * 100
        print('Images',count,'Accuracy',accuracy)
    elif len(sys.argv) == 2 and sys.argv[1] == '1':
        for name in glob.glob('GoldStandards/*.jpg',recursive=False): 
            count += 1
            main(name)
        accuracy = (sum/count) * 100
        print('Images',count,'Accuracy',accuracy)
    elif len(sys.argv) == 2 and sys.argv[1] == '2':
        for name in glob.glob('stress_dataset/*.TIF',recursive=False): 
            count += 1
            main(name)        
        accuracy = (sum/count) * 100
        print('Images',count,'Accuracy',accuracy)
    elif len(sys.argv) == 2 :
        main(sys.argv[1],True)        
