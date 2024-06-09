import socket,cv2, pickle,struct
import threading 
import time
import random
from queue import Queue
from collections import deque

global vehicle_count_1
global vehicle_count_2
global ambulance_detect
global counter_a,counter_b
global my_socket
global delay_in_seconds
global delay
delay="5000"
delay_in_seconds = int(delay) / 1000
counter_a=counter_b=0
vehicle_count_1=deque()
vehicle_count_2=deque()
ambulance_detect=Queue()




def vehicle():
    global vehicle_count_1
    global vehicle_count_2
    
    # create socket
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = '127.0.0.1' # Here Require vehicle_counter
    port = 1431 #This port is only used for getting vehicle count from Vehicle_counter
    try:
        client_socket.connect((host_ip,port)) # a tuple
    except:
        pass
    if client_socket:
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            for i in range(1, 3):  # Loop for two frames
                while len(data) < payload_size:
                    packet = client_socket.recv(4*1024) # 4K
                    if not packet: break
                    data+=packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                if len(packed_msg_size) < 8:  # Ensure we have received enough data
                    print("Error: Not enough data received")
                else:
                    msg_size = struct.unpack("Q",packed_msg_size)[0]
                    # msg_size = struct.unpack("Q",packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4*1024)
                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame = pickle.loads(frame_data)
                # cv2.imshow(f"RECEIVING VIDEO FROM CACHE SERVER - FRAME {i}", frame)
                if i==1:
                    vehicle_count_1.append(frame)
                elif i==2:
                    vehicle_count_2.append(frame)
                # print(f"object count of {i}= {frame}")

            key = cv2.waitKey(1) & 0xFF
            if key  == ord('q'):
                break
        client_socket.close()


def ambulance_connection():
    global ambulance_detect
    ambulance_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = '127.0.0.1'
    print('HOST IP:',host_ip)
    port = 7777
    ambulance_socket.connect((host_ip,port))
    data1 = b""
    payload_size1 = struct.calcsize("Q")
    try:
        while True:
            while len(data1) < payload_size1:
                packet1 = ambulance_socket.recv(4*1024)
                if not packet1: break
                data1+=packet1
            packed_msg_size1 = data1[:payload_size1]
            data1 = data1[payload_size1:]
            if len(packed_msg_size1) < 8:
                print("Error: Not enough data received")
                break
            else:
                msg_size1 = struct.unpack("Q",packed_msg_size1)[0]

            while len(data1) < msg_size1:
                data1 += ambulance_socket.recv(4*1024)
            frame_data1 = data1[:msg_size1]
            data1  = data1[msg_size1:]
            frame1 = pickle.loads(frame_data1)
            ambulance_detect.put(frame1)
            # print(frame1)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        ambulance_socket.close()
        print("ambulance socket closed.")

def sender(msg):
    global my_socket
    global delay_in_seconds
    global delay
    try:
        my_socket.send(msg.encode())
        recv_msg = (my_socket.recv(1024).decode())
        button_msg = (my_socket.recv(1024).decode())
        print()
        print(recv_msg)
        print(button_msg)
        print()
        time.sleep(delay_in_seconds)
        if button_msg =="Button Pressed from Nodemcu":
            msg="5 "+delay
            sender(msg)

    except BrokenPipeError:
        print("Connection lost. Please check the server.")

def nodemcu():
    global my_socket
    global vehicle_count_1
    global vehicle_count_2
    global ambulance_detect
    global counter_a,counter_b
    global delay_in_seconds
    global delay
    my_socket = socket.socket()

    port = 80
    ip = "172.16.34.203"


    try:
        my_socket.connect((ip,port))
        # time.sleep(8)
    except ConnectionRefusedError:
        print("Connection refused. Please check if the server is running and accessible.")
    while True:
    
        a=vehicle_count_1[-1]
        b=vehicle_count_2[-1]
        status,ambulance=ambulance_detect.get()
        # status=0
        # ambulance=0
        if status==1:
            if ambulance==1:
                msg="1 "+delay
                print("Ambulance detected from logic")
                sender(msg)
            else:
                msg="2 "+delay
                sender(msg)
        else:
            l =[0,1,2,3,4,5,6,7,8,9]
            a=random.choice(l)
            b=random.choice(l)

            print(f"Road1 Count={a} and Road2 Count={b}")
            if a==0 and b==0:
                msg="3 " + delay
                sender(msg)
                counter_a=counter_b=0
            elif a==b:
                msg="1 "+delay
                sender(msg)

                msg="2 "+delay
                sender(msg)
                counter_a=counter_b=0
            elif a>b:
                counter_a+=1
                counter_b=0
                if(counter_a==3):
                    print()
                    print(f" a={a} , b={b} a>b occured 3 times")
                    print()
                    if(b>0):
                        msg="2 "+delay
                        sender(msg)

                    else:
                        msg="1 "+delay
                        sender(msg)
                    counter_a=0
                else:
                    msg="1 "+delay
                    sender(msg)

            elif a<b:
                counter_b+=1
                counter_a=0
                if(counter_b==3):
                    print()
                    print(f" a={a} , b={b} a<b occured 3 times")
                    print()
                    if(a>0):
                        msg="1 "+delay
                        sender(msg)
                    else:
                        msg="2 "+delay
                        sender(msg)
                    counter_a=0
                else:
                    msg="2 "+delay
                    sender(msg)



thread1=threading.Thread(target=vehicle)
thread2=threading.Thread(target=ambulance_connection)
thread3=threading.Thread(target=nodemcu)
thread1.start()
thread2.start()
# thread3.start()
