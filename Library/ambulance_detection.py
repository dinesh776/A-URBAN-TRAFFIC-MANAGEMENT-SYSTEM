import socket,cv2, pickle,struct
import numpy as np
import supervision as sv
import cv2
from ultralytics import YOLO
import time
import socket
import pickle
import threading
import queue



#load Model
model = YOLO("/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Models/Siren.pt")
global frame1
frame1 = [queue.Queue(), queue.Queue()]

def ambulance(queue):
    global frame1
    print("Ambulance Detection logic started")
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = '127.0.0.1' # Here Require CACHE Server IP
    port = 9999
    client_socket.connect((host_ip,port)) # a tuple
    data = b""
    payload_size = struct.calcsize("Q")
    box_annotator = sv.BoundingBoxAnnotator(
            thickness=1,
    )
    label_annotator = sv.LabelAnnotator(
        text_scale=1,
    )
    while True:
        for i in range(2):  # Loop for two frames
            while len(data) < payload_size:
                packet = client_socket.recv(4*1024) # 4K
                if not packet: break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q",packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4*1024)
            frame_data = data[:msg_size]
            data  = data[msg_size:]
            frame = pickle.loads(frame_data)

            #Vehicle Counting logic
            result = model(frame, agnostic_nms=True)[0]
            detections = sv.Detections.from_ultralytics(result)
            # print(detections)
            detections=detections[detections.class_id==0]

            if detections:
                queue.put((1,i+1))
            else:
                queue.put((0,0))

            frame = box_annotator.annotate(
                scene=frame,
                detections=detections,
            )
            frame = label_annotator.annotate(
                scene=frame,
                detections=detections,
            )
            frame1[i].put(frame)
            # cv2.imshow(f'Ambulance Frame {i+1}',frame)
            key = cv2.waitKey(1) & 0xFF
        if key  == ord('q'):
            break
    client_socket.close()



def logic(queue):
    ambulance_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = '127.0.0.1'
    print('HOST IP:',host_ip)
    port = 7777
    ambulance_address = (host_ip,port)
    ambulance_socket.bind(ambulance_address)
    ambulance_socket.listen()
    print("Listening at",ambulance_address)
    ambulance_detection=[]
    while True:
        like_socket,likeaddr = ambulance_socket.accept()
        if like_socket:
            print("ambulance is connected to logic")
            while True:
                detected,road=queue.get()
                # detected,road = [0,0]
                # if detected>0:
                try:
                    ambulance_detection.extend([detected,road])
                    a = pickle.dumps(ambulance_detection)
                    message = struct.pack("Q",len(a))+a
                    like_socket.sendall(message)
                    ambulance_detection=[]
                except Exception as e:
                    print(f"Error occurred: {e}")
                    like_socket.close()
                    break


def Display():
    global frame1
    #  listening from logic script
    display_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = '127.0.0.1'
    print('HOST IP:',host_ip)
    port3 = 3311 #This port is only used for sending vehicle count to logic
    display_address = (host_ip,port3)
    display_socket.bind(display_address)
    display_socket.listen()
    print("Listening at",display_address)
    while True:
        d_socket,d_addr = display_socket.accept()
        if display_socket:
            try:
                print('CLIENT {} CONNECTED!'.format(d_addr))
                while True:
                    for i in range(2):  # Loop for two frames
                        a = pickle.dumps(frame1[i].get())
                        message = struct.pack("Q",len(a))+a
                        d_socket.sendall(message)
            except Exception as e:
                print(f"CLINET {d_addr} DISCONNECTED")
                pass


ambulance_detected=queue.Queue()
thread=threading.Thread(target=logic,args=(ambulance_detected,))
thread1=threading.Thread(target=ambulance,args=(ambulance_detected,))
thread3=threading.Thread(target=Display,args=())
thread1.start()
thread.start()
thread3.start()
