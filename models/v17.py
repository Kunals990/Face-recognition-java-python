import math
import os
import socket
import time
from datetime import datetime

import cv2
import cvzone
import face_recognition
import numpy as np
from ultralytics import YOLO

path = 'ImagesAttendance'
name = None
name_in_attend=[]
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    print(classNames)

print(classNames)
print(classNames)

if "Kunal" in classNames:
    print("YESSS")


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
            name_in_attend.append(name)
            f.writelines(f'{name},{dtString}\n')
            return True
    return False


encodeListKnown = findEncodings(images)
print('Encoding Complete')

webcam_thread = None
command_queue = None


def start_loop():

        cap = cv2.VideoCapture(0)  # For Webcam
        cap.set(3, 480)
        cap.set(4, 480)

        model_path = os.path.join(".", "models", "best.pt")
        model = YOLO(model_path)
        confidence = 0.8
        yolo_classNames = ["fake", "real"]  # Separate list for YOLO class names

        prev_frame_time = 0
        new_frame_time = 0

        marked_attendance = set()  # Set to keep track of marked attendance
        n=0
        # time.sleep(7)
        while (n<14):
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
                    print(conf)
                    # Class Name
                    cls = int(box.cls[0])
                    print(cls)
                    print(yolo_classNames[cls])
                    if conf > confidence:
                        if yolo_classNames[cls] == 'real':
                            color = (0, 255, 0)
                            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                            facesCurFrame = face_recognition.face_locations(imgS)
                            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

                            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                                matchIndex = np.argmin(faceDis)

                                if matches[matchIndex] :
                                    global name
                                    name = classNames[matchIndex].upper()
                                    if name not in marked_attendance:
                                        marked = markAttendance(name)
                                        if marked:
                                            marked_attendance.add(name)

                                    y1, x2, y2, x1 = faceLoc
                                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255),2)
                                    cv2.putText(img, 'Attendance Marked', (x1 + 6, y1 - 30), cv2.FONT_HERSHEY_COMPLEX,
                                                1, (255, 0, 0), 2)  # Change color to blue
                                    print(name)

                        else:
                            color = (0, 0, 255)
                        print(name_in_attend)


                        cvzone.cornerRect(img, (x1, y1, w, h), colorC=color, colorR=color)
                        cvzone.putTextRect(img, f'{yolo_classNames[cls].upper()} {int(conf*100)}%', (max(0, x1), max(35, y1)), scale=2, thickness=4, colorR=color, colorB=color)
            n = n + 1
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            print(fps)


            cv2.imshow("Image", img)
            cv2.waitKey(1)

        cap.release()
        cv2.destroyAllWindows()


SERVER_PORT = 12345
SERVER_IP = "127.0.0.1"

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)

print("Waiting for connection...")

# Accept connection
client_socket, addr = server_socket.accept()
print(f"Connection from {addr} has been established.")

while True:
    # Receive command from client
    command_bytes = client_socket.recv(1024)

    command = command_bytes.decode('utf-8').strip()

    # Perform action based on command
    if command.lower() == "1":
        print("Starting webcam...")
        start_loop()
    # elif (command=="2" ):
    #     print("Stopping webcam...")
    #     stop_webcam()
    else:
        print("Invalid command")

# Close the connection
client_socket.close()