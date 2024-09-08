import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from ultralytics import YOLO
import math
import time

path = 'ImagesAttendance'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'{name},{dtString}\n')
            return True
    return False

encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 480)

model = YOLO("C://Users//hp//Documents//Python//Face Recognition//models//best.pt")
confidence = 0.8

prev_frame_time = 0
new_frame_time = 0

marked_attendance = set()  # Set to keep track of marked attendance

while True:
    new_frame_time = time.time()
    success, img = cap.read()
    results = model(img, stream=True, verbose=False)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bounding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            # Confidence
            conf = math.ceil((box.conf[0] * 100)) / 100
            # Class Name
            cls = int(box.cls[0])

            if conf > confidence:
                # Draw bounding box
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                if classNames[cls] == 'real':
                    # Mark attendance
                    face_img = img[y1:y2, x1:x2]
                    encodeFace = face_recognition.face_encodings(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
                    if encodeFace:
                        matches = face_recognition.compare_faces(encodeListKnown, encodeFace[0])
                        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace[0])
                        matchIndex = np.argmin(faceDis)

                        if matches[matchIndex]:
                            name = classNames[matchIndex].upper()
                            if name not in marked_attendance:
                                marked = markAttendance(name)
                                if marked:
                                    marked_attendance.add(name)
                            cv2.putText(img, 'Attendance Marked', (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                        (0, 0, 255), 1)
                else:
                    cv2.putText(img, 'Fake Face', (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)

    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    print(fps)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
