import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QLineEdit, QPushButton, QApplication, QVBoxLayout, QMainWindow
import subprocess as sbp
import cgitb
cgitb.enable(format = "text")

class Camera_Control():
    """This class can control a Nikon camera using the CamControlRemote.exe from digicam control. This class and the
     capture fuction is only callable if the digicamcontrol sofware is open and LiveView is started.
     __init__ initializes a session with the desired name, iso and aperture. While the capture function just takes a live view picture.
     The remote exe is only callable via the cmd and therefore subprocess run was used.
     http://digicamcontrol.com/
    """

    def __init__(self, path_remote, name, minTime):
        self.path_remote = path_remote
        self.name = name
        self.minTime = minTime
        sbp.run(self.path_remote +
                f" /c set session.filenametemplate {str(self.name)}_{str(self.minTime)}min")

    def capture(self):
        full_path = self.path_remote + " /c do LiveView_Capture"
        sbp.run(full_path)


# create main window
class CaptureImage(QMainWindow):
    def __init__(self):
        super(CaptureImage, self).__init__()
        self.initUI()

    # initialize Main Window
    def initUI(self):
        self.setWindowTitle("You shall be captured")
        self.setGeometry(200, 200, 300, 300)
        self.button = QPushButton("Capture", self)
        self.button.move(100, 150)
        self.timer_button = QPushButton("Timer", self)
        self.timer_button.setCheckable(True)
        self.timer_button.move(100, 180)
        self.intervalButton = QPushButton("Interval Capture", self)
        self.intervalButton.move(100,210)
        self.intervalButton.setCheckable(True)
        # sample name label
        self.timer_label = QtWidgets.QLabel("Timer",self)
        self.timer_label.move(50,80)
        self.nameLabel = QtWidgets.QLabel(self)
        self.nameLabel.setText("Sample:")
        self.nameLabel.move(50, 110)
        self.line = QLineEdit(self)
        self.line.move(100, 110)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.nameLabel)
        self.button.clicked.connect(self.remote_control)
        self.timer_button.clicked.connect(self.start_timer)
        self.intervalButton.clicked.connect(self.intervalCapture)
        self.timer_label.setText("--:--")
        self.timer = QTimer() #initalize timer object
        self.timer.timeout.connect(self.displayTime) #call function remote control every 5 min


    # create buttom callback

    @pyqtSlot()
    def remote_control(self):
        '''
        Calls the Camera_Control Class, which in turn calls the CameraControlRemoteCmd.exe
        '''
        path_remote = '"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"'
        cam = Camera_Control(path_remote, self.line.text(), self.min)
        cam.capture()

    @pyqtSlot()
    def start_timer(self):
        '''This function is called by the timer_button,
         when clicked a timer will start and the self.count variable will be set to 0'''

        self.timer_count = 0
        if self.timer_button.isChecked() or self.intervalButton.isChecked():
            self.timer.start(1000)
        else:
            self.timer.stop()
            self.timer_label.setText("--:--")
    @pyqtSlot()
    def displayTime(self):
        '''This methods calculates the minutes and seconds
         from a counter which increments by 1 every second
         and displays set the timer_label.text() to minutes:seconds formatting.
         The second part of this function if self.intervalButton.isChecked() and self.count/60 % interval ==0:
         denotes a 2 conditional interval function call.
         '''
        self.timer_count += 1
        self.min = int(self.timer_count/60)
        sec = int(self.timer_count - self.min*60)
        self.timer_label.setText(f"{str(self.min)} min : {str(sec)} sec")
        interval = 0.5
        if self.intervalButton.isChecked() and self.timer_count/60 % interval ==0:
            print(f"The current min is: {str(self.min)}\n.. Every 2 min Timer successful")
            #self.remote_control()
    @pyqtSlot()
    def intervalCapture (self):
        '''This method calls the remote_control Function every 5 mins.
        If the min modulus of 5 is == 0 the function will be called'''
        if self.intervalButton.isChecked():
            self.timer_button.setEnabled(False)
            self.start_timer()
            self.displayTime()

        else:
            self.timer.stop()
            self.timer_label.setText("--:--")
            self.timer_button.setEnabled(True)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    im = CaptureImage()
    im.show()
    sys.exit(app.exec())
