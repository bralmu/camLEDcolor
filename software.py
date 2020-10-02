import cv2, os, time, operator
import RPi.GPIO as GPIO

FREQUENCY = 4
CAPTURE_X = 640
CAPTURE_Y = 480
RESIZED_X = 32
RESIZED_Y = 24
redPin = 11 #GPIO 17
greenPin = 13 #GPIO 27
bluePin = 15 #GPIO 22
redPWM = None
greenPWM = None
bluePWM = None
COLOR_PWM_VALUES = {"red": [100, 0, 0],
                    "green": [0, 100, 0],
                    "blue": [0, 0, 100],
                    "white": [30, 100, 50],
                    "black": [0, 0, 0]}

def initializeOutput():
    """Configures Raspberry Pi pins as outputs with PWM signal and sets them to 0V initially."""
    global redPWM, greenPWM, bluePWM
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(redPin, GPIO.OUT)
    GPIO.setup(greenPin, GPIO.OUT)
    GPIO.setup(bluePin, GPIO.OUT)
    redPWM = GPIO.PWM(redPin, 1000)
    greenPWM = GPIO.PWM(greenPin, 1000)
    bluePWM = GPIO.PWM(bluePin, 1000)
    redPWM.start(0)
    greenPWM.start(0)
    bluePWM.start(0)
    
def setOutputColor(color):
    """Changes the output of pins to show the color on the LED."""
    redPWM.ChangeDutyCycle(COLOR_PWM_VALUES[color][0])
    greenPWM.ChangeDutyCycle(COLOR_PWM_VALUES[color][1])
    bluePWM.ChangeDutyCycle(COLOR_PWM_VALUES[color][2])

def getMyWebcamIdx():
    """Returns device index for the specific webcam that we want to use (e.g. ID_MODEL_ID=4095). 
       Because several webcams could be connected to the Raspberry Pi."""
    webcamfound = False
    for i in range (0, 5):
        msg = os.popen('udevadm info --query=all /dev/video' + str(i) + ' | grep \'MODEL_ID\'').read()
        if  'ID_MODEL_ID=4095' in msg:
            webcamfound = True
            break
    if  webcamfound:
        return i
    else:
        return -1
        
def getMostPopularColor(colorCountDictionary):
    return max(colorCountDictionary.items(), key=operator.itemgetter(1))[0]

def main():
    cam = cv2.VideoCapture(getMyWebcamIdx())
    cam.set(3, CAPTURE_X)
    cam.set(4, CAPTURE_Y)
    initializeOutput()
    while True:
        color_count = {'white':0, 'black':0, 'red':0, 'green':0, 'blue':0}
        ret_val, img = cam.read()
        img = cv2.resize(img, (RESIZED_X, RESIZED_Y), interpolation=cv2.INTER_LANCZOS4)
        for x in range (0, RESIZED_X-1):
            for y in range (0, RESIZED_Y-1):
                if (float(img[y,x,0]) + float(img[y,x,1]) + float(img[y,x,2])) < 127.0:
                    img[y,x,0] = 0
                    img[y,x,1] = 0
                    img[y,x,2] = 0
                    color_count['black'] += 1
                elif img[y,x,0] > (float(img[y,x,1]) + float(img[y,x,2])):
                    img[y,x,0] = 255
                    img[y,x,1] = 0
                    img[y,x,2] = 0
                    color_count['blue'] += 1
                elif img[y,x,1] > (float(img[y,x,0]) + float(img[y,x,2])):
                    img[y,x,0] = 0
                    img[y,x,1] = 255
                    img[y,x,2] = 0
                    color_count['green'] += 1
                elif img[y,x,2] > (float(img[y,x,0]) + float(img[y,x,1])):
                    img[y,x,0] = 0
                    img[y,x,1] = 0
                    img[y,x,2] = 255
                    color_count['red'] += 1
                elif img[y,x,0] > 127 and img[y,x,1] > 127 and img[y,x,2] > 127:
                    img[y,x,0] = 255
                    img[y,x,1] = 255
                    img[y,x,2] = 255
                    color_count['white'] += 1
                else:
                    img[y,x,0] = 127
                    img[y,x,1] = 127
                    img[y,x,2] = 127
        mostPopularColor = getMostPopularColor(color_count)
        setOutputColor(mostPopularColor)
        print(mostPopularColor)
        cv2.imshow('windows title', img)
        if  cv2.waitKey(1) == 27: 
            break  # esc to quit
        time.sleep(1 / FREQUENCY)
    redPWM.stop()
    greenPWM.stop()
    bluePWM.stop()
    GPIO.cleanup()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
