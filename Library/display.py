import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QScrollArea, QSizePolicy, QTabWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent, QObject
from PyQt5 import QtCore
import sys
import socket
import struct
import pickle

class CaptureVideoFramesWorker1(QThread):
    ImageUpdated1 = pyqtSignal(QImage)
    ImageUpdated2 = pyqtSignal(QImage)

    def __init__(self, host_ip, port) -> None:
        super(CaptureVideoFramesWorker1, self).__init__()
        self.host_ip = host_ip
        self.port = port
        self.__thread_active = True
        self.__thread_pause = False

    def run(self) -> None:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host_ip, self.port))
        print(f"Connected to {self.port}")
        data = b""
        payload_size = struct.calcsize("Q")
        while self.__thread_active:
            for _ in range(2):  # Loop for two frames
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
                if frame is not None:
                    height, width, channels = frame.shape
                    bytes_per_line = width * channels
                    cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    qt_rgb_image_scaled = qt_rgb_image.scaled(1280, 720, Qt.KeepAspectRatio)
                    if _ == 0:
                        self.ImageUpdated1.emit(qt_rgb_image_scaled)
                    else:
                        self.ImageUpdated2.emit(qt_rgb_image_scaled)
        client_socket.close()
        self.quit()



    def stop(self) -> None:
        self.__thread_active = False

    def pause(self) -> None:
        self.__thread_pause = True

    def unpause(self) -> None:
        self.__thread_pause = False


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        self.list_of_cameras_state = {}

        self.label_1 = QLabel("Road 1")
        self.camera_1 = QLabel()
        self.camera_1.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_1.setScaledContents(True)
        self.camera_1.installEventFilter(self)
        self.camera_1.setObjectName("Camera_1")
        self.list_of_cameras_state["Camera_1"] = "Normal"

        
        self.QScrollArea_1 = QScrollArea()
        self.QScrollArea_1.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_1.setWidgetResizable(True)
        self.QScrollArea_1.setWidget(self.camera_1)

        self.label_2 = QLabel("Road 2")
        self.camera_2 = QLabel()
        self.camera_2.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_2.setScaledContents(True)
        self.camera_2.installEventFilter(self)
        self.camera_2.setObjectName("Camera_2")
        self.list_of_cameras_state["Camera_2"] = "Normal"

        self.QScrollArea_2 = QScrollArea()
        self.QScrollArea_2.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_2.setWidgetResizable(True)
        self.QScrollArea_2.setWidget(self.camera_2)

        self.label_3 = QLabel("Road 1")
        self.camera_3 = QLabel()
        self.camera_3.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_3.setScaledContents(True)
        self.camera_3.installEventFilter(self)
        self.camera_3.setObjectName("Camera_3")
        self.list_of_cameras_state["Camera_3"] = "Normal"

        self.QScrollArea_3 = QScrollArea()
        self.QScrollArea_3.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_3.setWidgetResizable(True)
        self.QScrollArea_3.setWidget(self.camera_3)

        self.label_4 = QLabel("Road 2")
        self.camera_4 = QLabel()
        self.camera_4.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_4.setScaledContents(True)
        self.camera_4.installEventFilter(self)
        self.camera_4.setObjectName("Camera_4")
        self.list_of_cameras_state["Camera_4"] = "Normal"

        self.QScrollArea_4 = QScrollArea()
        self.QScrollArea_4.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_4.setWidgetResizable(True)
        self.QScrollArea_4.setWidget(self.camera_4)

        self.__SetupUI()

        self.CaptureVideoFramesWorker_1 = CaptureVideoFramesWorker1('127.0.0.1', 9999)
        self.CaptureVideoFramesWorker_1.ImageUpdated1.connect(lambda image: self.ShowCamera1(image))
        self.CaptureVideoFramesWorker_1.ImageUpdated2.connect(lambda image: self.ShowCamera2(image))

        self.CaptureVideoFramesWorker_2 = CaptureVideoFramesWorker1('127.0.0.1', 4477)
        self.CaptureVideoFramesWorker_2.ImageUpdated1.connect(lambda image: self.ShowCamera3(image))
        self.CaptureVideoFramesWorker_2.ImageUpdated2.connect(lambda image: self.ShowCamera4(image))
    
        self.CaptureVideoFramesWorker_3 = CaptureVideoFramesWorker1('127.0.0.1', 3311)
        self.CaptureVideoFramesWorker_3.ImageUpdated1.connect(lambda image: self.ShowCamera5(image))
        self.CaptureVideoFramesWorker_3.ImageUpdated2.connect(lambda image: self.ShowCamera6(image))


        self.CaptureVideoFramesWorker_1.start()
        self.CaptureVideoFramesWorker_2.start()
        self.CaptureVideoFramesWorker_3.start()

    def __SetupUI(self) -> None:
        self.tab_widget = QTabWidget()

        # Existing tabs
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab1, "Original Video")
        self.tab_widget.addTab(self.tab2, "Vehicle Counter")

        # New tabs
        self.tab3 = QWidget()
        # self.tab4 = QWidget()
        self.tab_widget.addTab(self.tab3, "Ambulance Detection")

        # Layouts for existing tabs
        grid_layout_1 = QGridLayout()
        grid_layout_2 = QGridLayout()

        # Adjusted layout for Tab 1
        grid_layout_1.addWidget(self.label_1, 0, 0) # Label for Camera 1
        grid_layout_1.addWidget(self.QScrollArea_1, 1, 0) # Video widget for Camera 1
        grid_layout_1.addWidget(self.label_2, 0, 1) # Label for Camera 2
        grid_layout_1.addWidget(self.QScrollArea_2, 1, 1) # Video widget for Camera 2

        # Adjusted layout for Tab 2
        grid_layout_2.addWidget(self.label_3, 0, 0) # Label for Camera 3
        grid_layout_2.addWidget(self.QScrollArea_3, 1, 0) # Video widget for Camera 3
        grid_layout_2.addWidget(self.label_4, 0, 1) # Label for Camera 4
        grid_layout_2.addWidget(self.QScrollArea_4, 1, 1) # Video widget for Camera 4

        # Layouts for new tabs
        grid_layout_3 = QGridLayout()

        # Assuming you have video paths for these new cameras
        self.label_5 = QLabel("Road 1")
        self.camera_5 = QLabel()
        self.camera_5.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_5.setScaledContents(True)
        self.camera_5.installEventFilter(self)
        self.camera_5.setObjectName("Camera_5")
        self.list_of_cameras_state["Camera_5"] = "Normal"

        self.QScrollArea_5 = QScrollArea()
        self.QScrollArea_5.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_5.setWidgetResizable(True)
        self.QScrollArea_5.setWidget(self.camera_5)

        self.label_6 = QLabel("Road 2")
        self.camera_6 = QLabel()
        self.camera_6.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_6.setScaledContents(True)
        self.camera_6.installEventFilter(self)
        self.camera_6.setObjectName("Camera_6")
        self.list_of_cameras_state["Camera_6"] = "Normal"

        self.QScrollArea_6 = QScrollArea()
        self.QScrollArea_6.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_6.setWidgetResizable(True)
        self.QScrollArea_6.setWidget(self.camera_6)

        # Adjusted layout for Tab 3
        grid_layout_3.addWidget(self.label_5, 0, 0) # Label for Camera 5
        grid_layout_3.addWidget(self.QScrollArea_5, 1, 0) # Video widget for Camera 5
        grid_layout_3.addWidget(self.label_6, 0, 1) # Label for Camera 6
        grid_layout_3.addWidget(self.QScrollArea_6, 1, 1) # Video widget for Camera 6


        # Set layouts for tabs
        self.tab1.setLayout(grid_layout_1)
        self.tab2.setLayout(grid_layout_2)
        self.tab3.setLayout(grid_layout_3)
        # self.tab4.setLayout(grid_layout_4)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tab_widget)

        self.widget = QWidget(self)
        self.widget.setLayout(vbox)

        self.setCentralWidget(self.widget)
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'black';}")
        self.setWindowIcon(QIcon(QPixmap("camera_2.png")))
        self.setWindowTitle("AN URBAN TRAFFIC MANAGEMENT SYSTEM")



    @QtCore.pyqtSlot()
    def ShowCamera1(self, frame: QImage) -> None:
        self.camera_1.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera2(self, frame: QImage) -> None:
        self.camera_2.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera3(self, frame: QImage) -> None:
        self.camera_3.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera4(self, frame: QImage) -> None:
        self.camera_4.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera5(self, frame: QImage) -> None:
        self.camera_5.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera6(self, frame: QImage) -> None:
        self.camera_6.setPixmap(QPixmap.fromImage(frame))

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            if source.objectName() == 'Camera_1':
                if self.list_of_cameras_state["Camera_1"] == "Normal":
                    self.QScrollArea_2.hide()
                    self.label_2.hide()
                    self.list_of_cameras_state["Camera_1"] = "Maximized"
                else:
                    self.QScrollArea_2.show()
                    self.label_2.show()
                    self.list_of_cameras_state["Camera_1"] = "Normal"
                return True
            elif source.objectName() == 'Camera_2':
                # Similar logic for Camera_2
                if self.list_of_cameras_state["Camera_2"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.label_1.hide()
                    self.list_of_cameras_state["Camera_2"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.label_1.show()
                    self.list_of_cameras_state["Camera_2"] = "Normal"
                return True
            elif source.objectName() == 'Camera_3':
                # Similar logic for Camera_3
                if self.list_of_cameras_state["Camera_3"] == "Normal":
                    self.QScrollArea_4.hide()
                    self.label_4.hide()
                    self.list_of_cameras_state["Camera_3"] = "Maximized"
                else:
                    self.QScrollArea_4.show()
                    self.label_4.show()
                    self.list_of_cameras_state["Camera_3"] = "Normal"
                return True
            elif source.objectName() == 'Camera_4':
                # Similar logic for Camera_4
                if self.list_of_cameras_state["Camera_4"] == "Normal":
                    self.QScrollArea_3.hide()
                    self.label_3.hide()
                    self.list_of_cameras_state["Camera_4"] = "Maximized"
                else:
                    self.QScrollArea_3.show()
                    self.label_3.show()
                    self.list_of_cameras_state["Camera_4"] = "Normal"
                return True
            elif source.objectName() == 'Camera_5':
                # Logic for Camera_5
                if self.list_of_cameras_state["Camera_5"] == "Normal":
                    self.QScrollArea_6.hide()
                    self.label_6.hide()
                    self.list_of_cameras_state["Camera_5"] = "Maximized"
                else:
                    self.QScrollArea_6.show()
                    self.label_6.show()
                    self.list_of_cameras_state["Camera_5"] = "Normal"
                return True
            elif source.objectName() == 'Camera_6':
                # Logic for Camera_6
                if self.list_of_cameras_state["Camera_6"] == "Normal":
                    self.QScrollArea_5.hide()
                    self.label_5.hide()
                    self.list_of_cameras_state["Camera_6"] = "Maximized"
                else:
                    self.QScrollArea_5.show()
                    self.label_5.show()
                    self.list_of_cameras_state["Camera_6"] = "Normal"
                return True
        return super().eventFilter(source, event)

   


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
