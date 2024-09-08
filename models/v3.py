import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from ultralytics import YOLO
import cvzone
import math
import time

# Load YOLO model for face detection
model = YOLO("C://Users//hp//Documents//Python//Face Recognition//models//best.pt")
confidence_threshold = 0.8

# Load face recognition images and names
path = 'ImagesAttendance'
images = []
classNames = []
myList = os.listdir(path)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

# Encode known faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print('Encoding Complete')

# Set up webcam
cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 480)

# Set to keep track of marked attendance
marked_attendance = set()

while True:
    # Capture frame-by-frame
    success, img = cap.read()

    # Detect faces using YOLO
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

            # Check confidence threshold
            if conf > confidence_threshold:
                if cls == 1:  # Real face
                    # Mark attendance if face recognized
                    face_img = img[y1:y2, x1:x2]
                    encodeFace = face_recognition.face_encodings(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
                    if encodeFace:
                        matches = face_recognition.compare_faces(encodeListKnown, encodeFace[0])
                        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace[0])
                        matchIndex = np.argmin(faceDis)

                        if matches[matchIndex]:
                            name = classNames[matchIndex].upper()
                            if name not in marked_attendance:
                                # Mark attendance
                                with open('Attendance.csv', 'r+') as f:
                                    myDataList = f.readlines()
                                    nameList = [entry.split(',')[0] for entry in myDataList]
                                    if name not in nameList:
                                        now = datetime.now()
                                        dtString = now.strftime('%H:%M:%S')
                                        f.writelines(f'{name},{dtString}\n')
                                        marked_attendance.add(name)
                else:
                    # Fake face
                    cv2.putText(img, 'Fake Face', (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)

    # Display the resulting frame
    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
