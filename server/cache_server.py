import socket, cv2, pickle, struct
import imutils # pip install imutils
import threading
import cv2
import os





server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '127.0.0.1'
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)
server_socket.bind(socket_address)
server_socket.listen()
print("Listening at",socket_address)

global frame
frame = [None, None]

def start_video_stream():
    global frame
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = '127.0.0.1'
    port = 7766
    client_socket.connect((host_ip,port))
    data = b""
    payload_size = struct.calcsize("Q")
    try:
        while True:
            for i in range(2):  # Loop for two frames
                while len(data) < payload_size:
                    packet = client_socket.recv(4*1024) 
                    if not packet: break
                    data+=packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]

                msg_size = struct.unpack("Q",packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4*1024)
                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame[i] = pickle.loads(frame_data)
                # try:
                #     cv2.imshow(f"TRANSMITTING TO CACHE SERVER - FRAME {i+1}", frame[i])
                # except:
                #     pass
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        client_socket.close()
        print("Client socket closed.")


thread = threading.Thread(target=start_video_stream, args=())
thread.start()

def serve_client(addr,client_socket):
    global frame
    try:
        print('CLIENT {} CONNECTED!'.format(addr))
        if client_socket:
            while True:
                for i in range(2):  # Loop for two frames
                    a = pickle.dumps(frame[i])
                    message = struct.pack("Q",len(a))+a
                    client_socket.sendall(message)
    except Exception as e:
        print(f"CLINET {addr} DISCONNECTED")
        pass

while True:
    client_socket,addr = server_socket.accept()
    print(addr)
    thread = threading.Thread(target=serve_client, args=(addr,client_socket))
    thread.start()
    print("TOTAL CLIENTS ",threading.active_count() - 2) # edited here because one thread is already started before
