from cvzone.FaceDetectionModule import FaceDetector
import cv2
import cvzone
from time import time

classID = 0 # 0 is for fake and 1 is for real
outputFolderpath = "DataSets/DataCollect"
save = True
confidence=0.8
offsetPercentageW=10
offsetPercentageH=20
camWidth , camHeight = 640,480
floatingPoint=6
blurThreshold = 35
debug = False

cap = cv2.VideoCapture(2)
cap.set(3,camWidth)
cap.set(4,camHeight)

detector = FaceDetector(minDetectionCon=0.5, modelSelection=0)

while True:
        success, img = cap.read()
        imgOut = img.copy()

        # Detect faces in the image
        # img: Updated image
        # bboxs: List of bounding boxes around detected faces
        img, bboxs = detector.findFaces(img,draw=False)

        listblur=[]
        listInfo = []


        # Check if any face is detected
        if bboxs:
            for bbox in bboxs:
                # bbox contains 'id', 'bbox', 'score', 'center'

                # ---- Get Data  ---- #
                # center = bbox["center"]

                # ---- Adding offset to the face detected

                x, y, w, h = bbox['bbox']
                score = bbox['score'][0]

                if score>confidence:
                    offsetW = (offsetPercentageW/100)*w
                    x=int(x-offsetW)
                    w=int(w+offsetW*2)

                    offsetH = (offsetPercentageH/ 100) * h
                    y = int(y - offsetH*3)
                    h = int(h + offsetH * 3.2)

                    # -- To avoid value below 0

                    if x<0:x=0
                    if y<0:y=0
                    if h<0:h=0
                    if w<0:w=0

                    # ------Finding blurriness

                    imgFace = img[y:y+h,x:x+w]
                    cv2.imshow("Face",imgFace)
                    blurVa1ue= int(cv2.Laplacian(imgFace,cv2.CV_64F).var())
                    if blurVa1ue>blurThreshold:
                        listblur.append(True)
                    else:
                        listblur.append(False)

                    # ---- Normalize Values
                    ih,iw,_ = img.shape
                    xc,yc = x+w/2,y+h/2
                    xcn = round(xc/iw,floatingPoint)
                    ycn = round(yc/ih,floatingPoint)
                    wn = round(w/iw,floatingPoint)
                    hn = round(h/ih,floatingPoint)

                    # -- to avoid values above 1
                    if xcn>1:xcn=1
                    if ycn>1:ycn=1
                    if hn>1:hn=1
                    if wn>1:wn=1

                    # print(xcn,ycn,wn,hn)
                    listInfo.append(f"{classID} {xcn} {ycn} {wn} {hn}\n")
                    # ---- Drawing----

                    cv2.rectangle(imgOut,(x,y,w,h),(255,0,0),3)
                    cvzone.putTextRect(imgOut,f"Score:{int(score*100)}% Blur:{blurVa1ue}",(x,y-20),scale=2,thickness=3 )

                    if debug:
                        cv2.rectangle(img, (x, y, w, h), (255, 0, 0), 3)
                        cvzone.putTextRect(img, f"Score:{int(score * 100)}% Blur:{blurVa1ue}", (x, y - 20), scale=2,thickness=3)

            # ---- TO SAVE
            if save:
                if all(listblur) and listblur!=[]:
                    timeNow=time()
                    timeNow=str(timeNow).split('.')
                    timeNow=timeNow[0]+timeNow[1]
                    cv2.imwrite(f"{outputFolderpath}/{timeNow}.jpg",img)

                    for info in listInfo:
                        f = open(f"{outputFolderpath}/{timeNow}.txt", "a")
                        f.write(info)
                        f.close()
                    # --Save Text Labels


                # print(x,y,w,h)
                # score = int(bb    ox['score'][0] * 100)
                #
                # # ---- Draw Data  ---- #
                # cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
                # cvzone.putTextRect(img, f'{score}%', (x, y - 10))
                # cvzone.cornerRect(img, (x, y, w, h))

        # Display the image in a window named 'Image'
        cv2.imshow("Image", imgOut)
        # Wait for 1 millisecond, and keep the window open
        cv2.waitKey(1)