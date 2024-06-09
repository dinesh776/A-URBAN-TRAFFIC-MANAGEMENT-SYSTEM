import socket, cv2, pickle, struct
import imutils
import cv2
import threading
import sys
import cv2,threading
import numpy as np
import supervision as sv
from ultralytics import YOLO
import os
from sort.sort import *
from util import get_car, read_license_plate
import uuid
from datetime import datetime,timedelta
import json
import dateutil
import random,pickle,socket,struct
from queue import Queue

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '127.0.0.1' 
print('HOST IP:',host_ip)
port = 7766
socket_address = (host_ip,port)
server_socket.bind(socket_address)
server_socket.listen()
print("Listening at",socket_address)

global client_socket
client_socket=None
global main_frames_for_license
global frames_for_display
global license_plate_frames_for_display
main_frames_for_license=[Queue(),Queue()]
license_plate_frames_for_display = [Queue(),Queue()]
frames_for_display = [Queue(),Queue()]

# easyocr
global lock
lock=0

def start_video_stream():
        global client_socket
        global main_frames_for_license
        global lock
        global frames_for_display
        client_socket,addr = server_socket.accept()
        camera = False
        if camera == True:
            vid = [cv2.VideoCapture(0),cv2.VideoCapture('/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Media/sample.mp4')]
        else:
            vid = [cv2.VideoCapture('/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Media/sample.mp4'), cv2.VideoCapture('/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Media/Ambulance.mp4')]
        try:
            print('CLIENT {} CONNECTED!'.format(addr))
            if client_socket:
                lock=1
                while True:
                    for i in range(2):  # Loop for two frames
                        if vid[i].isOpened():
                            img, frame = vid[i].read()
                            main_frames_for_license[i].put(frame)
                            frames_for_display[i].put(frame)
                            if img:  # If the frame is read correctly img will be True
                                frame  = imutils.resize(frame,width=1080)
                                # frame = cv2.resize(frame, (720, 720))
                                a = pickle.dumps(frame)
                                message = struct.pack("Q",len(a))+a
                                try:
                                    client_socket.sendall(message)
                                except:
                                    pass
                                # try:
                                #     cv2.imshow(f"TRANSMITTING TO CACHE SERVER - FRAME {i+1}", frame)
                                # except:
                                #     pass
                            else:
                                vid[i].release()  # If the video is finished, release the VideoCapture object
                    key = cv2.waitKey(1) & 0xFF
                    if key ==ord('q'):
                        client_socket.close()
                        break

        except Exception as e:
            print(f"CACHE SERVER {addr} DISCONNECTED")
            pass
        finally:
            for i in range(2):  # Release all the VideoCapture objects
                if vid[i].isOpened():
                    vid[i].release()
            client_socket.close()
            cv2.destroyAllWindows()  # Destroy all the windows


#license Plate Detector
def License_Plate_Detection():
    global lock
    global main_frames_for_license
    global license_plate_frames_for_display
    print()
    print("License is started")
    print()
    coco_model = YOLO('/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Models/yolov8n.pt')
    license_plate_detector = YOLO('/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Models/license_plate.pt')

    mot_tracker = Sort()
    vehicles = [2, 3, 5, 7]

    base_path = 'Results'
    json_paths=[]
    main_folder_paths=[]
    image_folder_paths=[]
    
    
    while True:
        if lock==1:
            for i in range(1, 3):
                folder_name = 'Road' + str(i)
                json_name = 'Result' + str(i) + '.json'
                folder_path = os.path.join(base_path, folder_name)
                images_path = os.path.join(folder_path,'images')
                json_path = os.path.join(folder_path,json_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    os.makedirs(images_path)
                main_folder_paths.append(folder_path)
                image_folder_paths.append(images_path)
                json_paths.append(json_path)
                    # print(f'Created folder: {folder_path}\nCreated Images folder: {images_path}')
                
            # Define the line coordinates
            START = sv.Point(756, 1642)
            END = sv.Point(2992, 1654)

            ret = True

            location=['NAD JUNCTION','Kurmanapalem','Madilapalem','Gajuwaka','Boyapalem','Anandapuram','Gurudwar']

            # ret, frame = queue.get()
            for i in range(2):
                crossed_objects = {}
                frame = main_frames_for_license[i].get()

                if os.path.exists(json_paths[i]):
                    with open(json_paths[i], 'r') as json_file:
                        data = json.load(json_file)
                else:
                    data = {}
                    with open(json_paths[i], 'w') as json_file:
                        json.dump(data, json_file)
                if ret:
                    detections = coco_model(frame)[0]
                    detections_ = []
                    for detection in detections.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = detection
                        if int(class_id) in vehicles:
                            detections_.append([x1, y1, x2, y2, score])

                    if detections_: # Check if detections_ is not empty
                        track_ids = mot_tracker.update(np.asarray(detections_))
                    else:
                        print("No detections made. Skipping tracking update.")

                    # track_ids = mot_tracker.update(np.asarray(detections_))
                    license_plates = license_plate_detector(frame)[0]


                    for license_plate in license_plates.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = license_plate
                        xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

                        if car_id != -1:
                            license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]
                            license_plate_text = read_license_plate(license_plate_crop)
                            # print()
                            # print(license_plate_text)
                            # print()
                            # license_plate_text = read_license_plate(license_plate_crop)

                            if license_plate_text is not None:
                                # Check if the license plate text is already in the JSON file
                                current_date = datetime.now().strftime('%Y-%m-%d')
                                current_time = datetime.now().strftime('%H:%M:%S')
                                # Adjusted logic for detecting if the car crosses the line
                                # This assumes the line is horizontal and cars cross it horizontally
                                if START.x < xcar1 < END.x or START.x < xcar2 < END.x and abs(ycar1 - START.y) or abs(ycar2 - START.y)< 5: # Adjust tolerance as needed
                                    crossed_objects[license_plate_text] = {True:[current_date,current_time]}
                                else:
                                    crossed_objects[license_plate_text] = {False:[current_date,current_time]}

                                if license_plate_text in data:
                                    # If the license plate text exists, append the current time to the list of times for the current date
                                    if current_date in data[license_plate_text]['Date&Time']:
                                        if current_time not in data[license_plate_text]['Date&Time'][current_date]:
                                            last_time = dateutil.parser.parse(data[license_plate_text]['Date&Time'][current_date][-1])
                                            current_time_dt = dateutil.parser.parse(current_time)
                                            if (current_time_dt - last_time) > timedelta(minutes=1):
                                                data[license_plate_text]['Date&Time'][current_date].append(current_time)
                                            # data[license_plate_text]['Date&Time'][current_date].append(current_time)
                                    else:
                                        data[license_plate_text]['Date&Time'][current_date] = [current_time]
                                else:
                                    # If it's not, crop the car image and save it
                                    car_crop = frame[int(ycar1):int(ycar2), int(xcar1):int(xcar2), :]
                                    car_file_name = f"car_{uuid.uuid4().hex}.png"
                                    car_file_path = os.path.join(image_folder_paths[i], car_file_name)
                                    cv2.imwrite(car_file_path, car_crop)
                                    
                                    # Add the license plate text to the JSON file
                                    data[license_plate_text] = {'Date&Time': {current_date: [current_time]}, 'image_path': car_file_path, 'location': random.choice(location), 'Red_line_crossed': crossed_objects[license_plate_text]}
                
                    with open(json_paths[i], 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                    


thread2=threading.Thread(target=License_Plate_Detection)
thread2.start()

while True:
	try:
		start_video_stream()
	except KeyboardInterrupt:
		print("Server stopped.")
		client_socket.close()
		break





