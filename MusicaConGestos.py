from concurrent.futures import thread
import math
import cv2
import time
import os
import mediapipe as mp
from pydub.generators import Sine
from pydub.playback import play
import keyboard
import threading
import ffmpeg
 
class HandDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
 
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
 
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
 
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
 
    def findPosition(self, img, handNo=0, draw=True):
 
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
 
        return lmList
 

wCam, hCam = 650, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = HandDetector(detectionCon=1)

def thread_task(array):
    print("empieza task", array)
    t = threading.Thread(target = make_tone, args = (array,))
    t.start()

def thread_record():
    
    t = threading.Thread(target=record)
    t.start()

def make_tone(array):
    print("Tono ",array)
    if(array == [1,0,0,0,0]):
        freq = 261.63
    elif(array == [0,1,0,0,0]):        
        freq = 329.63
    elif(array == [0,0,1,0,0]):        
        freq = 392.00
    elif(array == [0,0,0,1,0]):        
        freq = 493.88
    elif(array == [0,0,0,0,1]):        
        freq = 578.33
    else:
        freq= 698.45

    tone = (Sine(freq).to_audio_segment(volume=-20.0))
    play(tone)

def record():

    previousTime = 0
    run = True
    tipIds = [4,8,12,16,20]

    while run:
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            run = False

        success,img = cap.read()
        img = detector.findHands(img, draw=True )
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            fingers = []

            # if(math.dist(lmList[4], lmList[tipIds[1]]) < 30):


            # print("Distancia Pulgar - Indice  : ", math.dist(lmList[4], lmList[tipIds[1]]))
            # print("Distancia Pulgar - Anular : ", math.dist(lmList[4], lmList[tipIds[2]]))
            # print("Distancia Pulgar - Corazon : ", math.dist(lmList[4], lmList[tipIds[3]]))
            # print("Distancia Pulgar - Meñique : ", math.dist(lmList[4], lmList[tipIds[4]]))
            
    
            if(lmList[tipIds[0]][1] < lmList[17][1]):
                print("Reverse Hand")

            # Thumb
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
    
            # 4 Fingers
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            print(fingers)
            if(fingers != [0,0,0,0,0]):
                 thread_task(fingers)
    

        currentTime = time.time()
        fps = 1/(currentTime - previousTime)    
        previousTime = currentTime
        cv2.putText(img, f'FPS: {int(fps)}', (0,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255),2)    
        cv2.imshow("Image",img)
        cv2.waitKey(1)



if __name__ == "__main__":

    print ("Executed when invoked directly")
    thread_record()