import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QProcess, QTimer
from PyQt5.QtWidgets import QLineEdit, QPushButton, QApplication, QVBoxLayout, QMainWindow
import subprocess as sbp


class Camera_Control():
    """This class can control a Nikon camera using the CamControlRemote.exe from digicam control. This class and the
     capture fuction is only callable if the digicamcontrol sofware is open and LiveView is started.
     __init__ initializes a session with the desired name, iso and aperture. While the capture function just takes a live view picture.
     The remote exe is only callable via the cmd and therefore subprocess run was used.
     http://digicamcontrol.com/
    """

    def __init__(self, path_remote, name, count):
        self.path_remote = path_remote
        self.name = name
        self.count = count
        # self.ampere = ampere
        # self.voltage = voltage
        # self.iso= sbp.run(self.path_remote + " /c get iso", capture_output=True, text=True).stdout.split('"')[1]
        # self.aperture = sbp.run(self.path_remote + " /c get aperture", capture_output=True, text=True).stdout.split('"')[1]

        # sbp.run(self.path_remote +
        #        f" /c set session.filenametemplate {str(self.name)}_{str(self.voltage)}eV_{str(self.ampere)}A")
        # sbp.run(self.path_remote +
        # f" /c set session.filenametemplate {str(self.name)}_{str(self.iso)}eV_{str(self.aperture)}A")
        sbp.run(self.path_remote +
                f" /c set session.filenametemplate {str(self.name)}_{str(self.count)}")

    def capture(self, path_remote):
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
        self.timer_button = QPushButton("Timer", self)
        self.timer_button.setCheckable(True)
        self.timer_button.move(100, 180)
        self.button.move(100, 150)
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
        #self.line.textChanged.connect(self.counter)
        self.timer = QTimer()


    # create buttom callback

    @pyqtSlot()
    def remote_control(self):
        self.count += 1
        path_remote = '"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"'
        cam = Camera_Control(path_remote, self.line.text(), self.count)
        cam.capture(path_remote)

# # initialize count value 0  everytime input line changed
# @pyqtSlot()
# def counter(self):
#     self.count = 0
    ###############
    @pyqtSlot()
    def start_timer(self):
        if self.timer_button.isChecked():
            self.timer.start(1000)
            self.timer_label.setText(str(timer))
        else:
            self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    im = CaptureImage()
    im.show()
    sys.exit(app.exec())
