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


#  listening from logic script
logic_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '127.0.0.1'
print('HOST IP:',host_ip)
port = 1431 #This port is only used for sending vehicle count to logic
logic_address = (host_ip,port)
logic_socket.bind(logic_address)
logic_socket.listen()
print("Listening at",logic_address)


#load Model
model = YOLO("/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Models/yolov8n.pt")

# current_object_count = queue.Queue()
global current_object_count
current_object_count = [None,None] 
global frame1
frame1 = [queue.Queue(), queue.Queue()]

def vehicle_count():
    global current_object_count
    print("Vehicle count logic is running")
    # global frame1
    # create socket
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

    # Define normalized polygon coordinates
    ZONE_POLYGON = np.array([
        # [0.29, 0.55],[0.72, 0.55],[0.6, 0.19],[0.31, 0.2]
        [0.12, 0.5],[0.84, 0.48],[0.61, 0.17],[0.4, 0.18]
    ])

    # if source != "0":
    zone_polygon_pixels = (ZONE_POLYGON * np.array([3840, 2160])).astype(int)
    # else:
    #     zone_polygon_pixels = ZONE_POLYGON  # No scaling for webcam
    # Convert the polygon points to integer type
    zone_polygon_pixels = (ZONE_POLYGON * 1080).astype(int)

    zone = sv.PolygonZone(polygon=zone_polygon_pixels, frame_resolution_wh=(3840,2160))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone,
        color=sv.Color.RED, # Updated to use the updated color constant
        thickness=2,
        text_thickness=4,
        text_scale=2
    )
    while True:
        for i in range(2):  # Loop for two frames
            try:
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
                # frame1[i].put(frame)
                
            except:
                pass

            #Vehicle Counting logic
            result = model(frame, agnostic_nms=True)[0]
            detections = sv.Detections.from_ultralytics(result)

            s_class=[1,2,3,5,7]
            detections=detections[np.isin(detections.class_id,s_class)]

            frame = box_annotator.annotate(
                scene=frame,
                detections=detections,
            )
            frame = label_annotator.annotate(
                scene=frame,
                detections=detections,
            )
            zone.trigger(detections=detections)
            # current_object_count.put(zone.current_count)
            current_object_count[i] = zone.current_count
            frame = zone_annotator.annotate(scene=frame)
            frame1[i].put(frame)

            # print(frame)
            # cv2.imshow(f"RECEIVING VIDEO FROM CACHE SERVER - FRAME {i}", frame)
            print(f"The object of {i}th frame is {current_object_count[i]}")

        key = cv2.waitKey(1) & 0xFF
        if key  == ord('q'):
            break
    client_socket.close()


thread2 = threading.Thread(target=vehicle_count,args=())
thread2.start()


def Display():
    global frame1
    #  listening from logic script
    display_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = '127.0.0.1'
    print('HOST IP:',host_ip)
    port3 = 4477 #This port is only used for sending vehicle count to logic
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




def serve_client(addr,client_socket):
    global current_object_count
    try:
        print('CLIENT {} CONNECTED!'.format(addr))
        if client_socket:
            while True:
                for i in range(2):  # Loop for two frames
                    a = pickle.dumps(current_object_count[i])
                    message = struct.pack("Q",len(a))+a
                    client_socket.sendall(message)
    except Exception as e:
        print(f"CLINET {addr} DISCONNECTED")
        pass

thread3 = threading.Thread(target=Display,args=())
thread3.start()

while True:
    lo_socket,lo_addr = logic_socket.accept()
    if lo_socket:
        print(lo_addr)
        thread = threading.Thread(target=serve_client, args=(lo_addr,lo_socket))
        thread.start()

