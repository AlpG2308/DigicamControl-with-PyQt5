# -*- coding: utf-8 -*-
"""
Changed on Tue Mar 17 2020

@author: szilagyi
"""

# importing all necessary modules to generate the GUI (for PyQt5 version)
# PyQt5 and PyQt4 are different! check version on your PC first!
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QComboBox, QWidget, QMenuBar, QStatusBar, QGroupBox, QDoubleSpinBox, QPushButton, QMainWindow, QApplication, QLabel, QRadioButton, QSpinBox, QFrame
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QRect, Qt, QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont

# importing other necessary modules for certain functions
from functools import partial
import sys
import time
import subprocess as sbp
from datetime import datetime

# import module to connect to Attocube controller
from AttoConnect import AttoConnect

# redefine AttoConnect module to shorten commands later on
a = AttoConnect()

# import module to connect to Keithley controller
from KeithleyConnect import KeithleyConnect

# redefine KeithleyConnect module to shorten commands later on
k = KeithleyConnect()

# enable basic settings for Keithley controller
# set output to voltage (DCVOLTS) (default)
k.keithley.write('smua.source.func = smua.OUTPUT_DCVOLTS')
# set range for voltage (v) to autorange
k.keithley.write('smua.source.autorangev = smua.AUTORANGE_ON')
# set range for current (i) to autorange
k.keithley.write('smua.measure.autorangei = smua.AUTORANGE_ON')

# define class for Keithley output readout of current (i) and voltage (v)
class Reader(QObject):

    # send blank value to GUI display after measurement stopped (finished)
    finished = pyqtSignal()
    # send measured output value to GUI display
    output = pyqtSignal(str)
    
    # initialize Reader function
    def __init__(self, parent=None, **kwargs):
        super(Reader, self).__init__(parent, **kwargs)
        # set flag (reading values) to True
        self.reading = True
    
    # current output readout function
    def readcurr(self):
        
        # get current (i) value from Keithley (first value)
        ri = k.keithley.query('print(smua.measure.i(smua.nvbuffer1))')
        # send value as string to pyqtSignal in Reader function
        self.output.emit(str(ri))
        
        # continuous current measurement and output as long as reading is True
        while self.reading:
            
            # needed short timer to read the buffer values without problems
            time.sleep(0.5)
            ri = k.keithley.query('print(smua.measure.i(smua.nvbuffer1))')
            self.output.emit(str(ri))
        
        # when reading flag is set False, while loop stops and output is blank
        ri = ''
        self.output.emit(str(ri))
        # send finished signal to pyqtSignal in Reader function
        self.finished.emit()
    
    # voltage output readout function    
    def readvolt(self):
        
        # get voltage (v) value from Keithley (first value)
        rv = k.keithley.query('print(smua.measure.v(smua.nvbuffer1))')
        # send value as string to pyqtSignal in Reader function
        self.output.emit(str(rv))
        
        # continuous current measurement and output as long as reading is True
        while self.reading:
            
            # needed short timer to read the buffer values without problems
            time.sleep(0.2)
            rv = k.keithley.query('print(smua.measure.v(smua.nvbuffer1))')
            self.output.emit(str(rv))
        
        # when reading flag is set False, while loop stops and output is blank
        rv = ''
        self.output.emit(str(rv))
        # send finished signal to pyqtSignal in Reader function
        self.finished.emit()

class VoltageTracker(QObject):

    finished = pyqtSignal()
    tracked = pyqtSignal(str)

    def __init__(self, parent = None, **kwargs):
        super(VoltageTracker, self).__init__(parent, **kwargs)
        self.tracking = False

    def track(self, t):
        
        s = 0
        self.tracked.emit(str(s))

        while self.tracking:

            if s != t:

                self.tracked.emit(str(s))
                s += 1
                time.sleep(0.3)

            elif s == t:

                self.tracked.emit(str(s))
                time.sleep(0.3)
                break

        self.finished.emit()
#digicam Control Class
class Camera_Control():
    """This class can control a Nikon camera using the CamControlRemote.exe from digicam control. This class and the
     capture fuction is only callable if the digicamcontrol sofware is open and LiveView is started.
     __init__ initializes a session with the desired name, iso and aperture. While the capture function just takes a live view picture.
     The remote exe is only callable via the cmd and therefore subprocess run was used.
     http://digicamcontrol.com/
    """
    def __init__ (self, path_remote, name, count, voltage):
        self.path_remote = path_remote
        self.name = name
        self.count = count
        #self.ampere = ampere
        self.voltage = voltage
        #self.iso= sbp.run(self.path_remote + " /c get iso", capture_output=True, text=True).stdout.split('"')[1]
        #self.aperture = sbp.run(self.path_remote + " /c get aperture", capture_output=True, text=True).stdout.split('"')[1]


        #sbp.run(self.path_remote +
        #        f" /c set session.filenametemplate {str(self.name)}_{str(self.voltage)}eV_{str(self.ampere)}A")
        #sbp.run(self.path_remote +
                #f" /c set session.filenametemplate {str(self.name)}_{str(self.iso)}eV_{str(self.aperture)}A")
        sbp.run(self.path_remote +
               f" /c set session.filenametemplate {str(self.name)}_{str(self.count)}_{self.voltage}")




    def capture(self,path_remote):
        full_path = self.path_remote + " /c do LiveView_Capture"
        sbp.run(full_path)

# define class for the GUI window and all its functions
class Window(QMainWindow):
    
    # initialize window function
    def __init__(self):
        
        super(Window, self).__init__()
        # set basic window geometry (position x and y, size width and height)
        self.setGeometry(100, 100, 1040, 780)
        # set window main title
        self.setWindowTitle("LEEH Control GUI")
#   Camera Control
        self.CameraBox = QGroupBox("Camera Control", self)
        self.CameraBox.setGeometry((QRect(890,15,150,250)))
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.CameraBox.setFont(font)
        self.CameraBox.setObjectName("CameraBox")
        ######

        self.button = QPushButton("Capture", self.CameraBox)
        self.button.setGeometry(955,30,50,40)

        #sample name label
        self.nameLabel = QLabel("Sample",self.CameraBox)
        self.nameLabel.setGeometry(900,20,50,40)
        self.line = QLineEdit(self.CameraBox)
        self.line.setGeometry(950,20,60,40)
        self.button.clicked.connect(self.remote_control)
        self.line.textChanged.connect(self.counter)
        ######
    @pyqtSlot(str)
    def remote_control(self,measured_output):

        path_remote = '"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"'
        cam = Camera_Control(path_remote, self.line.text(), self.count, measured_output)
        cam.capture(path_remote)
        self.count += 1
    # initialize count value 0  everytime input line changed
    def counter(self):
        self.count = 0
#   Keithley control



        # generate Keithley function box containing its widgets
        self.KeithleyBox = QGroupBox("Keithley Control", self)
        # set box geometry (position x and y, size width and height)
        self.KeithleyBox.setGeometry(QRect(20, 15, 650, 120))
        # define font: type, size, bold, weight, ...
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)#
        font.setWeight(75)
        # set font in box
        self.KeithleyBox.setFont(font)
        # set box name (also for references)
        self.KeithleyBox.setObjectName("KeithleyBox")

        # define ON/OFF button and its text
        self.OnOffButton = QPushButton("Turn\n""Output\n""ON", self.KeithleyBox)
        # set button geometry (position x and y, size width and height)
        self.OnOffButton.setGeometry(QRect(20, 30, 71, 71))
        # set fill and color of button (changes depending on mode ON or OFF)
        self.OnOffButton.setAutoFillBackground(False)
        # default button color is set to green
        self.OnOffButton.setStyleSheet("background-color: green")
        # define font: type, size, bold, weight, ...
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        #set font in button
        self.OnOffButton.setFont(font)
        # set button name (also for references)
        self.OnOffButton.setObjectName("OnOffButton")
        # give button checkable functionality (ON or OFF mode)
        self.OnOffButton.setCheckable(True)
        # connect button click to OnOff function (checking mode)
        self.OnOffButton.clicked[bool].connect(self.OnOff)
        
        # define label for Control Mode
        self.ModeLabel = QLabel("Control Mode:", self.KeithleyBox)
        # set label geometry (position x and y, size width and height)
        self.ModeLabel.setGeometry(QRect(120, 30, 121, 16))
        # define font
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        # set label font
        self.ModeLabel.setFont(font)
        # set label name
        self.ModeLabel.setObjectName("ModeLabel")
        
        # define voltage control mode selection
        self.VoltageControl = QRadioButton("Voltage Control", self.KeithleyBox)
        # set voltage control mode geometry
        self.VoltageControl.setGeometry(QRect(120, 48, 131, 31))
        # define voltage control mode font
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        # set font for voltage control mode
        self.VoltageControl.setFont(font)
        # set default value to checked (GUI starts using voltage control mode)
        self.VoltageControl.setChecked(True)
        # set voltage control mode name (also for references)
        self.VoltageControl.setObjectName("VoltageControl")
        # connect selection toggle to VoltageControl function
        self.VoltageControl.toggled.connect(lambda:self.SetControl(self.VoltageControl))
        
        # define current control mode selection
        self.CurrentControl = QRadioButton("Current Control", self.KeithleyBox)
        # set current control mode geometry
        self.CurrentControl.setGeometry(QRect(120, 74, 131, 31))
        # define current control mode font
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        # set font for current control mode
        self.CurrentControl.setFont(font)
        # set default value to unchecked (GUI starts using voltage control mode)
        self.CurrentControl.setChecked(False)
        # set current control mode name (also for references)
        self.CurrentControl.setObjectName("CurrentControl")
        # connect selection toggle to CurrentControl function
        self.CurrentControl.toggled.connect(lambda:self.SetControl(self.CurrentControl))
        
        # define enter voltage/current value box
        self.SetVoltsAmps = QSpinBox(self.KeithleyBox)
        # set box geometry (position x and y, size width and height)
        self.SetVoltsAmps.setGeometry(QRect(260, 50, 121, 51))
        # define font for set value
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        # set value font
        self.SetVoltsAmps.setFont(font)
        # align value within box
        self.SetVoltsAmps.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        # set border values (min and max)
        self.SetVoltsAmps.setMinimum(-1000)
        self.SetVoltsAmps.setMaximum(0)
        # set step size for value box
        self.SetVoltsAmps.setSingleStep(1)
        # set default value
        self.SetVoltsAmps.setProperty("value", 0)
        # set value box name (also for references)
        self.SetVoltsAmps.setObjectName("SetVoltsAmps")
        # connect set/changed value information to setVoltAmps function
        self.SetVoltsAmps.valueChanged.connect(self.setVoltsAmps)
        
        # define label for set value box
        self.SetLabel = QLabel("Set Voltage in V:", self.KeithleyBox)
        # set label geometry
        self.SetLabel.setGeometry(QRect(260, 30, 121, 16))
        # define font for label
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        # set label font
        self.SetLabel.setFont(font)
        # set label name
        self.SetLabel.setObjectName("SetLabel")
        
        # define readout voltage/current value box (default value is blank)
        self.ReadVoltsAmps = QLabel("", self.KeithleyBox)
        # set box geometry (position x and y, size width and height)
        self.ReadVoltsAmps.setGeometry(QRect(410, 50, 221, 51))
        # define font for readout value
        font = QFont()
        font.setPointSize(17)
        font.setBold(True)
        font.setWeight(75)
        # set readout value font
        self.ReadVoltsAmps.setFont(font)
        # set box frame properties
        self.ReadVoltsAmps.setFrameShape(QFrame.WinPanel)
        self.ReadVoltsAmps.setFrameShadow(QFrame.Sunken)
        self.ReadVoltsAmps.setLineWidth(1)
        # set readout box name (also for references)
        self.ReadVoltsAmps.setObjectName("ReadVoltsAmps")
        
        # define label for readout box
        self.ReadLabel = QLabel("Measured Current in A:", self.KeithleyBox)
        # set label geometry
        self.ReadLabel.setGeometry(QRect(410, 30, 171, 16))
        # define font for label
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        # set label font
        self.ReadLabel.setFont(font)
        # set label name
        self.ReadLabel.setObjectName("ReadLabel")
        
        # set thread and reader to None (default) to empty all buffers
        self.thread = None
        self.reader = None

#   Attocube control
   
        #   X axis
        
        # generate Attocube function box for x axis containing its widgets
        self.XBox = QGroupBox("X Axis Control", self)
        # set box geometry (position x and y, size width and height)
        self.XBox.setGeometry(QRect(20, 150, 271, 611))
        # define font: type, size, bold, weight, ...
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        # set font in box
        self.XBox.setFont(font)
        # set box name (also for references)
        self.XBox.setObjectName("XBox")
        
        # generate filter function box for x axis containing its widgets
        self.XFilter = QGroupBox("Filter Mode", self.XBox)
        # set box geometry (position x and y, size width and height)
        self.XFilter.setGeometry(QRect(20, 30, 231, 71))
        # define font: type, size, bold, weight, ...
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        # set font in box
        self.XFilter.setFont(font)
        # set box name (also for references)
        self.XFilter.setObjectName("XFilter")
        
        # define frequency filter mode selection
        self.XFilterOff = QRadioButton("OFF", self.XFilter)
        # set frequency filter mode geometry
        self.XFilterOff.setGeometry(QRect(10, 30, 61, 20))
        # set default value to checked (GUI starts using filter mode set Off)
        self.XFilterOff.setChecked(True)
        # set frequency filter mode name (also for references)
        self.XFilterOff.setObjectName("XFilterOff")
        # connect selection toggle to XFilterOff function
        self.XFilterOff.toggled.connect(lambda:self.SetFilterX(self.XFilterOff))
        
        # code description as for frequency filter mode 'Off' (see above code)
        self.XFilter16 = QRadioButton("16 Hz", self.XFilter)
        self.XFilter16.setGeometry(QRect(80, 30, 61, 20))
        self.XFilter16.setObjectName("XFilter16")
        # connect selection toggle to XFilter16 function
        self.XFilter16.toggled.connect(lambda:self.SetFilterX(self.XFilter16))
        
        # code description as for frequency filter mode 'Off' (see above code)
        self.XFilter160 = QRadioButton("160 Hz", self.XFilter)
        self.XFilter160.setGeometry(QRect(150, 30, 71, 20))
        self.XFilter160.setObjectName("XFilter160")
        # connect selection toggle to XFilter160 function
        self.XFilter160.toggled.connect(lambda:self.SetFilterX(self.XFilter160))
        
        # generate mode selection box for x axis containing its widgets
        self.XMode = QGroupBox("Mode Control", self.XBox)
        # set box geometry (position x and y, size width and height)
        self.XMode.setGeometry(QRect(20, 120, 231, 111))
        # define font in box
        font = QFont()
        font.setPointSize(8)
        # set font in box
        self.XMode.setFont(font)
        # set box name (also for references)
        self.XMode.setObjectName("XMode")
        
        # define stepping mode selection
        self.XModeGnd = QRadioButton("GND mode", self.XMode)
        # set stepping mode geometry
        self.XModeGnd.setGeometry(QRect(10, 30, 101, 20))
        # set default value to checked (GUI starts using GND mode)
        self.XModeGnd.setChecked(True)
        # set stepping mode name (also for references)
        self.XModeGnd.setObjectName("XModeGnd")
        # connect selection toggle to XModeGnd function
        self.XModeGnd.toggled.connect(lambda:self.SetModeX(self.XModeGnd))
        
        # code description as for stepping mode 'GND' (see above code)
        self.XModeOff = QRadioButton("Offset mode", self.XMode)
        self.XModeOff.setGeometry(QRect(120, 30, 101, 20))
        self.XModeOff.setObjectName("XModeOff")
        # connect selection toggle to XModeOff function
        self.XModeOff.toggled.connect(lambda:self.SetModeX(self.XModeOff))
        
        # code description as for stepping mode 'GND' (see above code)
        self.XModeStp = QRadioButton("STP mode", self.XMode)
        self.XModeStp.setGeometry(QRect(10, 70, 101, 20))
        self.XModeStp.setObjectName("XModeStp")
        # connect selection toggle to XModeStp function
        self.XModeStp.toggled.connect(lambda:self.SetModeX(self.XModeStp))
        
        # code description as for stepping mode 'GND' (see above code)
        self.XModeStpOff = QRadioButton("STP+ mode", self.XMode)
        self.XModeStpOff.setGeometry(QRect(120, 70, 101, 20))
        # define font for this mode
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        # set font for this mode
        self.XModeStpOff.setFont(font)
        self.XModeStpOff.setObjectName("XModeStpOff")
        # connect selection toggle to XModeStpOff function
        self.XModeStpOff.toggled.connect(lambda:self.SetModeX(self.XModeStpOff))
        
        # generate continuous steps mode box for x axis containing its widgets
        self.XConStep = QGroupBox("Continuous Stepping", self.XBox)
        # set box geometry (position x and y, size width and height)
        self.XConStep.setGeometry(QRect(20, 250, 231, 101))
        # define font in box
        font = QFont()
        font.setPointSize(8)
        # set font in box
        self.XConStep.setFont(font)
        # set box name (also for references)
        self.XConStep.setObjectName("XConStep")
        
        # define enter frequency value box
        self.XFreqChange = QSpinBox(self.XConStep)
        # set box geometry (position x and y, size width and height)
        self.XFreqChange.setGeometry(QRect(75, 50, 81, 31))
        # define font for set value
        font = QFont()
        font.setPointSize(10)
        # set value font
        self.XFreqChange.setFont(font)
        # align value within box
        self.XFreqChange.setAlignment(Qt.AlignCenter)
        # set border values (default min = 0 and max)
        self.XFreqChange.setMaximum(1000)
        # set step size for value box
        self.XFreqChange.setSingleStep(10)
        # set default value
        self.XFreqChange.setProperty("value", 200)
        # set value box name (also for references)
        self.XFreqChange.setObjectName("XFreqChange")
        # connect set/changed value information to setFreqX function
        self.XFreqChange.valueChanged.connect(self.SetFreqX)
        
        # define frequency value box label
        self.XFreqLabel = QLabel(" Frequency (Hz)", self.XConStep)
        # set label geometry
        self.XFreqLabel.setGeometry(QRect(65, 30, 101, 20))
        # align label
        self.XFreqLabel.setAlignment(Qt.AlignCenter)
        # set label name
        self.XFreqLabel.setObjectName("XFreqLabel")
        
        # define piezo move button and its text
        self.XConUp = QPushButton("X+", self.XConStep)
        # set button geometry (position x and y, size width and height)
        self.XConUp.setGeometry(QRect(180, 30, 41, 51))
        # define font for button
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        # set button font
        self.XConUp.setFont(font)
        # set button name (also for references)
        self.XConUp.setObjectName("XConUp")
        # connect button pressing action to ConUpX function
        self.XConUp.pressed.connect(self.ConUpX)
        # connect button releasing action to StopX function
        self.XConUp.released.connect(self.StopX)
        
        # see description of button code above
        self.XConDown = QPushButton("X-", self.XConStep)
        self.XConDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.XConDown.setFont(font)
        self.XConDown.setObjectName("XConDown")
        # connect button pressing action to ConDownX function
        self.XConDown.pressed.connect(self.ConDownX)
        # connect button releasing action to StopX function
        self.XConDown.released.connect(self.StopX)
        
        # generate single steps mode box for x axis containing its widgets
        self.XSinStep = QGroupBox("Single Stepping", self.XBox)
        # set box geometry (position x and y, size width and height)
        self.XSinStep.setGeometry(QRect(20, 370, 231, 101))
        # define font in box
        font = QFont()
        font.setPointSize(8)
        # set font in box
        self.XSinStep.setFont(font)
        # set box name (also for references)
        self.XSinStep.setObjectName("XSinStep")
        
        # same code description as for previous value box 
        self.XAmpChange = QDoubleSpinBox(self.XSinStep)
        self.XAmpChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.XAmpChange.setFont(font)
        self.XAmpChange.setAlignment(Qt.AlignCenter)
        self.XAmpChange.setDecimals(1)
        self.XAmpChange.setMaximum(60.0)
        self.XAmpChange.setSingleStep(1.0)
        self.XAmpChange.setProperty("value", 30.0)
        self.XAmpChange.setObjectName("XAmpChange")
        # connect set/changed value information to setAmpX function
        self.XAmpChange.valueChanged.connect(self.SetAmpX)
        
        # same code description as for previous label
        self.XAmpLabel = QLabel("Amplitude (V)", self.XSinStep)
        self.XAmpLabel.setGeometry(QRect(70, 30, 91, 20))
        self.XAmpLabel.setAlignment(Qt.AlignCenter)
        self.XAmpLabel.setObjectName("XAmpLabel")
        
        # same code description as for previous buttons
        self.XSinDown = QPushButton("X-", self.XSinStep)
        self.XSinDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.XSinDown.setFont(font)
        self.XSinDown.setObjectName("XSinDown")
        # connect button clicking action to SinDownX function
        self.XSinDown.clicked.connect(self.SinDownX)
        
        # same code description as for previous buttons
        self.XSinUp = QPushButton("X+", self.XSinStep)
        self.XSinUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.XSinUp.setFont(font)
        self.XSinUp.setObjectName("XSinUp")
        # connect button clicking action to SinUpX function
        self.XSinUp.clicked.connect(self.SinUpX)
        
        # generate extension mode box for x axis containing its widgets
        self.XExtOff = QGroupBox("Extension via Offset", self.XBox)
        # set box geometry (position x and y, size width and height)
        self.XExtOff.setGeometry(QRect(20, 490, 231, 101))
        # define font in box
        font = QFont()
        font.setPointSize(8)
        # set font in box
        self.XExtOff.setFont(font)
        # set box name (also for references)
        self.XExtOff.setObjectName("XExtOff")
        
        # same code description as for previous value box 
        self.XOffChange = QDoubleSpinBox(self.XExtOff)
        self.XOffChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.XOffChange.setFont(font)
        self.XOffChange.setAlignment(Qt.AlignCenter)
        self.XOffChange.setDecimals(1)
        self.XOffChange.setMaximum(99.9)
        self.XOffChange.setSingleStep(0.1)
        self.XOffChange.setProperty("value", 0.0)
        # connect set/changed value information to XOffChange function
        self.XOffChange.setObjectName("XOffChange")
        
        # same code description as for previous label
        self.XOffLabel = QLabel("Voltage(V)", self.XExtOff)
        self.XOffLabel.setGeometry(QRect(70, 30, 91, 20))
        self.XOffLabel.setAlignment(Qt.AlignCenter)
        self.XOffLabel.setObjectName("XOffLabel")
        
        # same code description as for previous buttons
        self.XExtDown = QPushButton("X-", self.XExtOff)
        self.XExtDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.XExtDown.setFont(font)
        self.XExtDown.setObjectName("XExtDown")
        # connect set/changed value information to ExtDownX function
        self.XExtDown.clicked.connect(self.ExtDownX)
        
        # same code description as for previous buttons
        self.XExtUp = QPushButton("X+", self.XExtOff)
        self.XExtUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.XExtUp.setFont(font)
        self.XExtUp.setObjectName("XExtUp")
        # connect set/changed value information to ExtUpX function
        self.XExtUp.clicked.connect(self.ExtUpX)
        
        #   Y axis
        
        # code explanation same as for X axis (check above code)
        self.YBox = QGroupBox("Y Axis Control", self)
        self.YBox.setGeometry(QRect(310, 150, 271, 611))
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.YBox.setFont(font)
        self.YBox.setObjectName("YBox")
        
        self.YFilter = QGroupBox("Filter Mode", self.YBox)
        self.YFilter.setGeometry(QRect(20, 30, 231, 71))
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.YFilter.setFont(font)
        self.YFilter.setObjectName("YFilter")
        
        self.YFilterOff = QRadioButton("OFF", self.YFilter)
        self.YFilterOff.setGeometry(QRect(10, 30, 61, 20))
        self.YFilterOff.setChecked(True)
        self.YFilterOff.setObjectName("YFilterOff")
        self.YFilterOff.toggled.connect(lambda:self.SetFilterY(self.YFilterOff))
        
        self.YFilter16 = QRadioButton("16 Hz", self.YFilter)
        self.YFilter16.setGeometry(QRect(80, 30, 61, 20))
        self.YFilter16.setObjectName("YFilter16")
        self.YFilter16.toggled.connect(lambda:self.SetFilterY(self.YFilter16))
        
        self.YFilter160 = QRadioButton("160 Hz", self.YFilter)
        self.YFilter160.setGeometry(QRect(150, 30, 71, 20))
        self.YFilter160.setObjectName("YFilter160")
        self.YFilter160.toggled.connect(lambda:self.SetFilterY(self.YFilter160))
        
        self.YMode = QGroupBox("Mode Control", self.YBox)
        self.YMode.setGeometry(QRect(20, 120, 231, 111))
        font = QFont()
        font.setPointSize(8)
        self.YMode.setFont(font)
        self.YMode.setObjectName("YMode")
        
        self.YModeGnd = QRadioButton("GND mode", self.YMode)
        self.YModeGnd.setGeometry(QRect(10, 30, 101, 20))
        self.YModeGnd.setChecked(True)
        self.YModeGnd.setObjectName("YModeGnd")
        self.YModeGnd.toggled.connect(lambda:self.SetModeY(self.YModeGnd))
        
        self.YModeOff = QRadioButton("Offset mode", self.YMode)
        self.YModeOff.setGeometry(QRect(120, 30, 101, 20))
        self.YModeOff.setObjectName("YModeOff")
        self.YModeOff.toggled.connect(lambda:self.SetModeY(self.YModeOff))
        
        self.YModeStp = QRadioButton("STP mode", self.YMode)
        self.YModeStp.setGeometry(QRect(10, 70, 101, 20))
        self.YModeStp.setObjectName("YModeStp")
        self.YModeStp.toggled.connect(lambda:self.SetModeY(self.YModeStp))
        
        self.YModeStpOff = QRadioButton("STP+ mode", self.YMode)
        self.YModeStpOff.setGeometry(QRect(120, 70, 101, 20))
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.YModeStpOff.setFont(font)
        self.YModeStpOff.setObjectName("YModeStpOff")
        self.YModeStpOff.toggled.connect(lambda:self.SetModeY(self.YModeStpOff))
        
        self.YConStep = QGroupBox("Continuous Stepping", self.YBox)
        self.YConStep.setGeometry(QRect(20, 250, 231, 101))
        font = QFont()
        font.setPointSize(8)
        self.YConStep.setFont(font)
        self.YConStep.setObjectName("YConStep")
        
        self.YFreqChange = QSpinBox(self.YConStep)
        self.YFreqChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.YFreqChange.setFont(font)
        self.YFreqChange.setAlignment(Qt.AlignCenter)
        self.YFreqChange.setMaximum(1000)
        self.YFreqChange.setSingleStep(10)
        self.YFreqChange.setProperty("value", 200)
        self.YFreqChange.setObjectName("YFreqChange")
        self.YFreqChange.valueChanged.connect(self.SetFreqY)
        
        self.YFreqLabel = QLabel(" Frequency (Hz)", self.YConStep)
        self.YFreqLabel.setGeometry(QRect(65, 30, 101, 20))
        self.YFreqLabel.setAlignment(Qt.AlignCenter)
        self.YFreqLabel.setObjectName("YFreqLabel")
        
        self.YConUp = QPushButton("Y+", self.YConStep)
        self.YConUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.YConUp.setFont(font)
        self.YConUp.setObjectName("YConUp")
        self.YConUp.pressed.connect(self.ConUpY)
        self.YConUp.released.connect(self.StopY)
        
        self.YConDown = QPushButton("Y-", self.YConStep)
        self.YConDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.YConDown.setFont(font)
        self.YConDown.setObjectName("YConDown")
        self.YConDown.pressed.connect(self.ConDownY)
        self.YConDown.released.connect(self.StopY)
        
        self.YSinStep = QGroupBox("Single Stepping", self.YBox)
        self.YSinStep.setGeometry(QRect(20, 370, 231, 101))
        font = QFont()
        font.setPointSize(8)
        self.YSinStep.setFont(font)
        self.YSinStep.setObjectName("YSinStep")
        
        self.YAmpChange = QDoubleSpinBox(self.YSinStep)
        self.YAmpChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.YAmpChange.setFont(font)
        self.YAmpChange.setAlignment(Qt.AlignCenter)
        self.YAmpChange.setDecimals(1)
        self.YAmpChange.setMaximum(60.0)
        self.YAmpChange.setSingleStep(1.0)
        self.YAmpChange.setProperty("value", 30.0)
        self.YAmpChange.setObjectName("YAmpChange")
        self.YAmpChange.valueChanged.connect(self.SetAmpY)
        
        self.YAmpLabel = QLabel("Amplitude (V)", self.YSinStep)
        self.YAmpLabel.setGeometry(QRect(70, 30, 91, 20))
        self.YAmpLabel.setAlignment(Qt.AlignCenter)
        self.YAmpLabel.setObjectName("YAmpLabel")
        
        self.YSinDown = QPushButton("Y-", self.YSinStep)
        self.YSinDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.YSinDown.setFont(font)
        self.YSinDown.setObjectName("YSinDown")
        self.YSinDown.clicked.connect(self.SinDownY)
        
        self.YSinUp = QPushButton("Y+", self.YSinStep)
        self.YSinUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.YSinUp.setFont(font)
        self.YSinUp.setObjectName("YSinUp")
        self.YSinUp.clicked.connect(self.SinUpY)
        
        self.YExtOff = QGroupBox("Extension via Offset", self.YBox)
        self.YExtOff.setGeometry(QRect(20, 490, 231, 101))
        font = QFont()
        font.setPointSize(8)
        self.YExtOff.setFont(font)
        self.YExtOff.setObjectName("YExtOff")
        
        self.YOffChange = QDoubleSpinBox(self.YExtOff)
        self.YOffChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.YOffChange.setFont(font)
        self.YOffChange.setAlignment(Qt.AlignCenter)
        self.YOffChange.setDecimals(1)
        self.YOffChange.setMaximum(99.9)
        self.YOffChange.setSingleStep(0.1)
        self.YOffChange.setProperty("value", 0.0)
        self.YOffChange.setObjectName("YOffChange")
        
        self.YOffLabel = QLabel("Voltage (V)", self.YExtOff)
        self.YOffLabel.setGeometry(QRect(70, 30, 91, 20))
        self.YOffLabel.setAlignment(Qt.AlignCenter)
        self.YOffLabel.setObjectName("YOffLabel")
        
        self.YExtDown = QPushButton("Y-", self.YExtOff)
        self.YExtDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.YExtDown.setFont(font)
        self.YExtDown.setObjectName("YExtDown")
        self.YExtDown.clicked.connect(self.ExtDownY)
        
        self.YExtUp = QPushButton("Y+", self.YExtOff)
        self.YExtUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.YExtUp.setFont(font)
        self.YExtUp.setObjectName("YExtUp")
        self.YExtUp.clicked.connect(self.ExtUpY)

        #   Z axis
        
        # code explanation same as for X axis (check above code)
        self.ZBox = QGroupBox("Z Axis Control", self)
        self.ZBox.setGeometry(QRect(600, 150, 271, 611))
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ZBox.setFont(font)
        self.ZBox.setObjectName("ZBox")
        
        self.ZFilter = QGroupBox("Filter Mode", self.ZBox)
        self.ZFilter.setGeometry(QRect(20, 30, 231, 71))
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.ZFilter.setFont(font)
        self.ZFilter.setObjectName("ZFilter")
        
        self.ZFilterOff = QRadioButton("OFF", self.ZFilter)
        self.ZFilterOff.setGeometry(QRect(10, 30, 61, 20))
        self.ZFilterOff.setChecked(True)
        self.ZFilterOff.setObjectName("ZFilterOff")
        self.ZFilterOff.toggled.connect(lambda:self.SetFilterZ(self.ZFilterOff))
        
        self.ZFilter16 = QRadioButton("16 Hz", self.ZFilter)
        self.ZFilter16.setGeometry(QRect(80, 30, 61, 20))
        self.ZFilter16.setObjectName("ZFilter16")
        self.ZFilter16.toggled.connect(lambda:self.SetFilterZ(self.ZFilter16))
        
        self.ZFilter160 = QRadioButton("160 Hz", self.ZFilter)
        self.ZFilter160.setGeometry(QRect(150, 30, 71, 20))
        self.ZFilter160.setObjectName("ZFilter160")
        self.ZFilter160.toggled.connect(lambda:self.SetFilterZ(self.ZFilter160))
        
        self.ZMode = QGroupBox("Mode Control", self.ZBox)
        self.ZMode.setGeometry(QRect(20, 120, 231, 111))
        font = QFont()
        font.setPointSize(8)
        self.ZMode.setFont(font)
        self.ZMode.setObjectName("ZMode")
        
        self.ZModeGnd = QRadioButton("GND mode", self.ZMode)
        self.ZModeGnd.setGeometry(QRect(10, 30, 101, 20))
        self.ZModeGnd.setChecked(True)
        self.ZModeGnd.setObjectName("ZModeGnd")
        self.ZModeGnd.toggled.connect(lambda:self.SetModeZ(self.ZModeGnd))

        self.ZModeOff = QRadioButton("Offset mode", self.ZMode)
        self.ZModeOff.setGeometry(QRect(120, 30, 101, 20))
        self.ZModeOff.setObjectName("ZModeOff")
        self.ZModeOff.toggled.connect(lambda:self.SetModeZ(self.ZModeOff))
        
        self.ZModeStp = QRadioButton("STP mode", self.ZMode)
        self.ZModeStp.setGeometry(QRect(10, 70, 101, 20))
        self.ZModeStp.setObjectName("ZModeStp")
        self.ZModeStp.toggled.connect(lambda:self.SetModeZ(self.ZModeStp))
        
        self.ZModeStpOff = QRadioButton("STP+ mode", self.ZMode)
        self.ZModeStpOff.setGeometry(QRect(120, 70, 101, 20))
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ZModeStpOff.setFont(font)
        self.ZModeStpOff.setObjectName("ZModeStpOff")
        self.ZModeStpOff.toggled.connect(lambda:self.SetModeZ(self.ZModeStpOff))
        
        self.ZConStep = QGroupBox("Continuous Stepping", self.ZBox)
        self.ZConStep.setGeometry(QRect(20, 250, 231, 101))
        font = QFont()
        font.setPointSize(8)
        self.ZConStep.setFont(font)
        self.ZConStep.setObjectName("ZConStep")
        
        self.ZFreqChange = QSpinBox(self.ZConStep)
        self.ZFreqChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.ZFreqChange.setFont(font)
        self.ZFreqChange.setAlignment(Qt.AlignCenter)
        self.ZFreqChange.setMaximum(1000)
        self.ZFreqChange.setSingleStep(10)
        self.ZFreqChange.setProperty("value", 200)
        self.ZFreqChange.setObjectName("ZFreqChange")
        self.ZFreqChange.valueChanged.connect(self.SetFreqZ)
        
        self.ZFreqLabel = QLabel(" Frequency (Hz)", self.ZConStep)
        self.ZFreqLabel.setGeometry(QRect(65, 30, 101, 20))
        self.ZFreqLabel.setAlignment(Qt.AlignCenter)
        self.ZFreqLabel.setObjectName("ZFreqLabel")
        
        self.ZConUp = QPushButton("Z+", self.ZConStep)
        self.ZConUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.ZConUp.setFont(font)
        self.ZConUp.setObjectName("ZConUp")
        self.ZConUp.pressed.connect(self.ConUpZ)
        self.ZConUp.released.connect(self.StopZ)
        
        self.ZConDown = QPushButton("Z-", self.ZConStep)
        self.ZConDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.ZConDown.setFont(font)
        self.ZConDown.setObjectName("ZConDown")
        self.ZConDown.pressed.connect(self.ConDownZ)
        self.ZConDown.released.connect(self.StopZ)
        
        self.ZSinStep = QGroupBox("Single Stepping", self.ZBox)
        self.ZSinStep.setGeometry(QRect(20, 370, 231, 101))
        font = QFont()
        font.setPointSize(8)
        self.ZSinStep.setFont(font)
        self.ZSinStep.setObjectName("ZSinStep")
        
        self.ZAmpChange = QDoubleSpinBox(self.ZSinStep)
        self.ZAmpChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.ZAmpChange.setFont(font)
        self.ZAmpChange.setAlignment(Qt.AlignCenter)
        self.ZAmpChange.setDecimals(1)
        self.ZAmpChange.setMaximum(60.0)
        self.ZAmpChange.setSingleStep(1.0)
        self.ZAmpChange.setProperty("value", 30.0)
        self.ZAmpChange.setObjectName("ZAmpChange")
        self.ZAmpChange.valueChanged.connect(self.SetAmpZ)
        
        self.ZAmpLabel = QLabel("Amplitude (V)", self.ZSinStep)
        self.ZAmpLabel.setGeometry(QRect(70, 30, 91, 20))
        self.ZAmpLabel.setAlignment(Qt.AlignCenter)
        self.ZAmpLabel.setObjectName("ZAmpLabel")
        
        self.ZSinDown = QPushButton("Z-", self.ZSinStep)
        self.ZSinDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.ZSinDown.setFont(font)
        self.ZSinDown.setObjectName("ZSinDown")
        self.ZSinDown.clicked.connect(self.SinDownZ)
        
        self.ZSinUp = QPushButton("Z+", self.ZSinStep)
        self.ZSinUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.ZSinUp.setFont(font)
        self.ZSinUp.setObjectName("ZSinUp")
        self.ZSinUp.clicked.connect(self.SinUpZ)
        
        self.ZExtOff = QGroupBox("Extension via Offset", self.ZBox)
        self.ZExtOff.setGeometry(QRect(20, 490, 231, 101))
        font = QFont()
        font.setPointSize(8)
        self.ZExtOff.setFont(font)
        self.ZExtOff.setObjectName("ZExtOff")
        
        self.ZOffChange = QDoubleSpinBox(self.ZExtOff)
        self.ZOffChange.setGeometry(QRect(75, 50, 81, 31))
        font = QFont()
        font.setPointSize(10)
        self.ZOffChange.setFont(font)
        self.ZOffChange.setAlignment(Qt.AlignCenter)
        self.ZOffChange.setDecimals(1)
        self.ZOffChange.setMaximum(99.9)
        self.ZOffChange.setSingleStep(0.1)
        self.ZOffChange.setProperty("value", 0.0)
        self.ZOffChange.setObjectName("ZOffChange")
        
        self.ZOffLabel = QLabel("Voltage (V)", self.ZExtOff)
        self.ZOffLabel.setGeometry(QRect(70, 30, 91, 20))
        self.ZOffLabel.setAlignment(Qt.AlignCenter)
        self.ZOffLabel.setObjectName("ZOffLabel")
        
        self.ZExtDown = QPushButton("Z-", self.ZExtOff)
        self.ZExtDown.setGeometry(QRect(10, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.ZExtDown.setFont(font)
        self.ZExtDown.setObjectName("ZExtDown")
        self.ZExtDown.clicked.connect(self.ExtDownZ)
        
        self.ZExtUp = QPushButton("Z+", self.ZExtOff)
        self.ZExtUp.setGeometry(QRect(180, 30, 41, 51))
        font = QFont()
        font.setPointSize(10)
        self.ZExtUp.setFont(font)
        self.ZExtUp.setObjectName("ZExtUp")
        self.ZExtUp.clicked.connect(self.ExtUpZ)

        #   Data Reader

        self.DataBox = QGroupBox("Data Reader", self)
        self.DataBox.setGeometry(QRect(680, 15, 200, 120))
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.DataBox.setFont(font)
        self.DataBox.setObjectName("DataBox")

        self.Startbtn = QPushButton("Start", self.DataBox)
        self.Startbtn.setGeometry(QRect(10, 18, 80, 40))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Startbtn.setFont(font)
        self.Startbtn.setObjectName("Startbtn")

        self.Stopbtn = QPushButton("Stop", self.DataBox)
        self.Stopbtn.setGeometry(QRect(110, 18, 80, 40))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Stopbtn.setFont(font)
        self.Stopbtn.setObjectName("Stopbtn")
        self.Stopbtn.setEnabled(False)

        self.Selection = QComboBox(self.DataBox)
        self.Selection.move(20, 62)
        self.Selection.addItem("200")
        self.Selection.addItem("400")
        self.Selection.addItem("1000")

        self.Location = QPushButton("DATA PATH", self.DataBox)
        self.Location.setGeometry(QRect(110, 62, 80, 25))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Location.setFont(font)
        self.Location.setObjectName("Location")
        self.Location.clicked.connect(self.OpenPath)

        self.Path = QLineEdit("D:\CMN PC Data\VoltageStability", self.DataBox)
        self.Path.setGeometry(QRect(10, 90, 180, 25))
        self.Path.setObjectName("Path")

        self.threadt = None
        self.tracker = None

        self.Startbtn.clicked.connect(self.start_track)

    def OpenPath(self):
        
        pathname = QFileDialog.getExistingDirectory()
        path = str(pathname)
        self.Path.setText(path)

    def start_track(self):

        self.Startbtn.setEnabled(False)
        self.Stopbtn.setEnabled(True)
        self.Location.setEnabled(False)
        number = str(self.Selection.currentText())

        timestr = time.strftime("%Y%m%d-%H%M%S")
        with open(str(self.Path.text())+'\\Voltage_tracker_'+str(timestr)+'.txt','w') as writer:
            writer.write('Time (s), Voltage (V)\n')
            self.timestr = timestr

        self.threadt = QThread()
        self.tracker = VoltageTracker(tracked = self.add_tracked_values)
        self.tracker.moveToThread(self.threadt)

        self.tracker.tracking = True
        self.threadt.started.connect(partial(self.tracker.track, t=int(number)))
        self.Stopbtn.clicked.connect(self.stop_track)
        self.tracker.finished.connect(self.track_finished)
        self.tracker.finished.connect(self.threadt.quit)
        self.tracker.finished.connect(self.tracker.deleteLater)
        self.threadt.finished.connect(self.threadt.deleteLater)

        self.threadt.start()

    def stop_track(self):

        self.tracker.tracking = False
        self.Stopbtn.setEnabled(False)
        self.Startbtn.setEnabled(True)
        self.Location.setEnabled(True)

    @pyqtSlot(str)
    def add_tracked_values(self, trackV):

        with open(str(self.Path.text())+'\\Voltage_tracker_'+str(self.timestr)+'.txt','a') as appender:

            times = round(float(trackV)*0.3,2)
            appender.write(str(times)+', '+str(self.ReadVoltsAmps.text()))
            appender.write('\n')

    def track_finished(self):

        self.tracker.tracking = False
        self.Stopbtn.setEnabled(False)
        self.Startbtn.setEnabled(True)
        self.Location.setEnabled(True)
        
#   Keithley functions
        
    # thread functions for PyQt signals to be sent and got back from Reader class
    # start thread for current readout (only for voltage control mode)
    def start_readcurr(self):
        
        # start showing/getting output as soon as OnOFF button is in ON mode
        k.keithley.write('smua.source.output = smua.OUTPUT_ON')
        # define thread as QThread (gain its python functionality)
        self.thread = QThread()
        # define Reader class connection and connect its output to display_output function
        self.reader = Reader(output = self.display_output)
        # put Reader class in thread, so it can run simulatenously to GUI
        self.reader.moveToThread(self.thread)
        # when thread is started connect it to readcurr function
        self.thread.started.connect(self.reader.readcurr)
        # when thread is finished/stopped connect it to quit function
        self.reader.finished.connect(self.thread.quit)
        # empty previous reader function buffer
        self.reader.finished.connect(self.reader.deleteLater)
        # empty previous thread buffer
        self.thread.finished.connect(self.thread.deleteLater)
        # start the readout of current measurement
        self.thread.start()
    
    # start thread for voltage readout (only for current control mode)        
    def start_readvolt(self):
        
        # same description as for current reader function only for voltage in current control mode 
        k.keithley.write('smua.source.output = smua.OUTPUT_ON')
        self.thread = QThread()
        self.reader = Reader(output = self.display_output)
        self.reader.moveToThread(self.thread)
        self.thread.started.connect(self.reader.readvolt)
        self.reader.finished.connect(self.thread.quit)
        self.reader.finished.connect(self.reader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()        

    # control mode selection function passing mode information to OnOff button
    def SetControl(self, c):
        
        # checking if voltage control mode is toggled
        if c.text() == 'Voltage Control' and c.isChecked() == True:
            
            # reset OnOff button style and text
            self.OnOffButton.setStyleSheet('color: black; background-color: green')
            self.OnOffButton.setText("Turn\n""Output\n""ON")
            # turn output off on Keithley (in case it's not already done)
            k.keithley.write('smua.source.output = smua.OUTPUT_OFF')
            # reset starting value to 0
            self.SetVoltsAmps.setValue(0)
            v0 = self.SetVoltsAmps.value()
            # send value as command to Keithley
            k.keithley.write('smua.source.levelv = '+str(v0))
            # reset (blank) readout box
            self.ReadVoltsAmps.setText('')
            # adapt set label to voltage control mode
            self.SetLabel.setText("Set Voltage in V:")
            # adapt read label to voltage control mode
            self.ReadLabel.setText("Measured Current in A:")
            # (re)set min value for voltage control mode
            self.SetVoltsAmps.setMinimum(-1000)
            # reset output and readout parameters for Keithley
            k.keithley.write('smua.source.func = smua.OUTPUT_DCVOLTS')
            k.keithley.write('smua.source.autorangev = smua.AUTORANGE_ON')
            k.keithley.write('smua.measure.autorangei = smua.AUTORANGE_ON')
        
        # checking if current control mode is toggled
        # same description as for voltage control mode, but for current control mode
        elif c.text() == 'Current Control' and c.isChecked() == True:
        
            self.OnOffButton.setStyleSheet('color: black; background-color: green')
            self.OnOffButton.setText("Turn\n""Output\n""ON")
            k.keithley.write('smua.source.output = smua.OUTPUT_OFF')
            
            self.SetVoltsAmps.setValue(0)
            a0 = self.SetVoltsAmps.value()
            k.keithley.write('smua.source.leveli = '+str(a0))
            
            self.ReadVoltsAmps.setText('')
            self.SetLabel.setText("Set Current in nA:")
            self.ReadLabel.setText("Measured Voltage in V:")
            
            self.SetVoltsAmps.setMinimum(-1000)
            k.keithley.write('smua.source.func = smua.OUTPUT_DCAMPS')
            k.keithley.write('smua.source.limitv = 1200')
            k.keithley.write('smua.source.autorangei = smua.AUTORANGE_ON')
            k.keithley.write('smua.measure.autorangev = smua.AUTORANGE_ON')  
        
        # in case no mode is toggled (should not be possible) function is passed
        else:
            
            pass

    # function for OnOff button, default mode is inactive
    def OnOff(self, active):
        
        # after setting button to output on state in voltage control mode
        if active and self.VoltageControl.isChecked() == True:
            # set button appearence to ON mode
            self.OnOffButton.setStyleSheet('color: black; background-color: red')
            self.OnOffButton.setText("Turn\n""Voltage\n""OFF")
            # start reading current function
            self.start_readcurr()       

        # after setting button to output on state in current control mode
        elif active and self.CurrentControl.isChecked() == True:
            # set button appearence to ON mode
            self.OnOffButton.setStyleSheet('color: black; background-color: red')
            self.OnOffButton.setText("Turn\n""Current\n""OFF")
            # start reading voltage function
            self.start_readvolt()
        
        # after setting button to output off state
        else:
            # start stop_read function to stop measuring voltage and current readout
            self.stop_read()
            # reset button appearence to OFF mode
            self.OnOffButton.setStyleSheet('color: black; background-color: green')
            self.OnOffButton.setText("Turn\n""Output\n""ON")
    
    # send current and voltage control set values to Keithley
    def setVoltsAmps(self):
        
        # for voltage control mode
        if self.VoltageControl.isChecked() == True:
            # get value from box
            v = self.SetVoltsAmps.value()
            # send command to Keithley
            k.keithley.write('smua.source.levelv = '+str(v))
        
        # for current control mode
        elif self.CurrentControl.isChecked() == True:
            # get value from box
            a = self.SetVoltsAmps.value()
            # set to nano amps
            na = a*10**(-9)
            # send command to Keithley
            k.keithley.write('smua.source.leveli = '+str(na))
        
        # if no mode chosen/toggled function is passed
        else:
            
            pass
    
    # take measured output values from Reader class sent via pyqtSignal  
    @pyqtSlot(str)
    # while output turned ON show measured output values in box
    def display_output(self, measured_output):
        
        self.ReadVoltsAmps.setText(measured_output)
    
    # when output is turned OFF stop thread    
    def stop_read(self):
        # set reading flag to False to stop while loop in thread
        self.reader.reading = False
        # send output off command to Keithley
        k.keithley.write('smua.source.output = smua.OUTPUT_OFF')
        # set box value to blank
        self.ReadVoltsAmps.setText('')

#   Attocube functions
       
    #   Filter
    # same for x, y and z axis
    # function sending respective filter mode selection to AttoCube controller
    def SetFilterX(self, fx):
        
        # get checked mode
        if fx.text() == 'OFF' and fx.isChecked() == True:
            # send mode to controller
            a.atto.write('setfil 3 off')
            
        if fx.text() == '16 Hz' and fx.isChecked() == True:
            a.atto.write('setfil 3 16')
            
        if fx.text() == '160 Hz' and fx.isChecked() == True:
            a.atto.write('setfil 3 160')
            
    def SetFilterY(self, fy):
        
        if fy.text() == 'OFF' and fy.isChecked() == True:
            a.atto.write('setfil 2 off')
            
        if fy.text() == '16 Hz' and fy.isChecked() == True:
            a.atto.write('setfil 2 16')
            
        if fy.text() == '160 Hz' and fy.isChecked() == True:
            a.atto.write('setfil 2 160')
            
    def SetFilterZ(self, fz):
        
        if fz.text() == 'OFF' and fz.isChecked() == True:
            a.atto.write('setfil 4 off')
            
        if fz.text() == '16 Hz' and fz.isChecked() == True:
            a.atto.write('setfil 4 16')
            
        if fz.text() == '160 Hz' and fz.isChecked() == True:
            a.atto.write('setfil 4 160')
            
    #   Mode
    # same for x, y and z axis     
    # function sending respective stepping mode selection to AttoCube controller
    def SetModeX(self, mx):
        
        # get checked mode
        if mx.text() == 'GND mode' and mx.isChecked() == True:
            # send mode to controller
            a.atto.write('setm 3 gnd')
            # set offset values to default (0)
            self.XOffChange.setValue(0.0)
           
        if mx.text() == 'Offset mode' and mx.isChecked() == True:
            a.atto.write('setm 3 off')
           
        if mx.text() == 'STP mode' and mx.isChecked() == True:
            a.atto.write('setm 3 stp')
           
        if mx.text() == 'STP+ mode' and mx.isChecked() == True:
            a.atto.write('setm 3 stp+')

    def SetModeY(self, my):
        
        if my.text() == 'GND mode' and my.isChecked() == True:
            a.atto.write('setm 2 gnd')
            self.YOffChange.setValue(0.0)
           
        if my.text() == 'Offset mode' and my.isChecked() == True:
            a.atto.write('setm 2 off')
           
        if my.text() == 'STP mode' and my.isChecked() == True:
            a.atto.write('setm 2 stp')
           
        if my.text() == 'STP+ mode' and my.isChecked() == True:
            a.atto.write('setm 2 stp+')
            
    def SetModeZ(self, mz):
        
        if mz.text() == 'GND mode' and mz.isChecked() == True:
            a.atto.write('setm 4 gnd')
            self.ZOffChange.setValue(0.0)
           
        if mz.text() == 'Offset mode' and mz.isChecked() == True:
            a.atto.write('setm 4 off')
           
        if mz.text() == 'STP mode' and mz.isChecked() == True:
            a.atto.write('setm 4 stp')
           
        if mz.text() == 'STP+ mode' and mz.isChecked() == True:
            a.atto.write('setm 4 stp+')
        
    #   Frequency
    # same for x, y and z axis
    # function sending respective set frequency value to AttoCube controller    
    def SetFreqX(self):
        
        # get set frequency value
        frx = self.XFreqChange.value()
        # send frequency value to controller
        a.atto.write('setf 3 '+str(frx))
        
    def SetFreqY(self):
        
        fry = self.YFreqChange.value()
        a.atto.write('setf 2 '+str(fry))
        
    def SetFreqZ(self):
        
        frz = self.ZFreqChange.value()
        a.atto.write('setf 4 '+str(frz))
        
    #   Amplitude
    # same for x, y and z axis
    # function sending respective set amplitude value to AttoCube controller
    def SetAmpX(self):
        
        # get set amplitude value
        ax = self.XAmpChange.value()
        # send amplitude value to controller
        a.atto.write('setv 3 '+str(ax))
        
    def SetAmpY(self):
        
        ay = self.YAmpChange.value()
        a.atto.write('setv 2 '+str(ay))
        
    def SetAmpZ(self):
        
        az = self.ZAmpChange.value()
        a.atto.write('setv 4 '+str(az))
        
    #   Continuous Stepping
    # same for x, y and z axis
    # function sending continuous stepping signal to AttoCube controller
    # set frequency and amplitude values will affect the step speed and size
    def ConUpX(self):
        
        # set button color to red while pressing it
        self.XConUp.setStyleSheet('color: black; background-color: red')
        # send continuous stepping command to controller
        a.atto.write('stepu 3 0')
        
    def ConDownX(self):
        
        self.XConDown.setStyleSheet('color: black; background-color: red')
        a.atto.write('stepd 3 0')
    
    # function sending stopping signal to AttoCube controller        
    def StopX(self):
        
        # send stop command to controller
        a.atto.write('stop 3')
        # reset button colors to default
        self.XConUp.setStyleSheet('color: black; background-color: None')
        self.XConDown.setStyleSheet('color: black; background-color: None')
    
    def ConUpY(self):
        
        self.YConUp.setStyleSheet('color: black; background-color: red')
        a.atto.write('stepd 2 0')
        
    def ConDownY(self):
        
        self.YConDown.setStyleSheet('color: black; background-color: red')
        a.atto.write('stepu 2 0')
            
    def StopY(self):
        
        a.atto.write('stop 2')
        self.YConUp.setStyleSheet('color: black; background-color: None')
        self.YConDown.setStyleSheet('color: black; background-color: None')
        
    def ConUpZ(self):
        
        self.ZConUp.setStyleSheet('color: black; background-color: red')
        a.atto.write('stepu 4 0')
        
    def ConDownZ(self):
        
        self.ZConDown.setStyleSheet('color: black; background-color: red')
        a.atto.write('stepd 4 0')
            
    def StopZ(self):
        
        a.atto.write('stop 4')
        self.ZConUp.setStyleSheet('color: black; background-color: None')
        self.ZConDown.setStyleSheet('color: black; background-color: None')
        
    #   Single Steps
    # same for x, y and z axis
    # function sending single step signal to AttoCube controller 
    # set amplitude values will affect the step size
    def SinUpX(self):
        
        # send single step for respective axis and direction to controller
        a.atto.write('stepu 3 1')
        
    def SinDownX(self):
        
        a.atto.write('stepd 3 1')
        
    def SinUpY(self):
        
        a.atto.write('stepd 2 1')
        
    def SinDownY(self):
        
        a.atto.write('stepu 2 1')
        
    def SinUpZ(self):
        
        a.atto.write('stepu 4 1')
        
    def SinDownZ(self):
        
        a.atto.write('stepd 4 1')
        
    #   Offset
    # same for x, y and z axis
    # set offset values will affect the expansion    
    def ExtDownX(self):
        
        # get set or changed value from box
        edx = self.XOffChange.value()
        # take offset expansion value and change it in respective direction
        if edx > 0.0:    
            medx = edx - 0.1
            # set/show new value in box
            self.XOffChange.setValue(medx)
            # send new value to controller
            a.atto.write('seta 3 '+str(medx))  
        # if min (default) value reached (0), send min value only 
        else:
            medx = 0
            self.XOffChange.setValue(medx)
            a.atto.write('seta 3 '+str(medx))
    
    # set value can only be increased until set max in box (max = 20.0 by default)    
    def ExtUpX(self):
        
        eux = self.XOffChange.value()
        peux = eux + 0.1
        self.XOffChange.setValue(peux)
        a.atto.write('seta 3 '+str(peux))
        
    def ExtUpY(self):
        
        edy = self.YOffChange.value()
        if edy > 0.0:    
            medy = edy - 0.1
            self.YOffChange.setValue(medy)
            a.atto.write('seta 2 '+str(medy))    
        else:
            medy = 0
            self.YOffChange.setValue(medy)
            a.atto.write('seta 2 '+str(medy))
        
    def ExtDownY(self):
        
        euy = self.YOffChange.value()
        peuy = euy + 0.1
        self.YOffChange.setValue(peuy)
        a.atto.write('seta 2 '+str(peuy))
        
    def ExtDownZ(self):
        
        edz = self.ZOffChange.value()
        if edz > 0.0:    
            medz = edz - 0.1
            self.ZOffChange.setValue(medz)
            a.atto.write('seta 4 '+str(medz))    
        else:
            medz = 0
            self.ZOffChange.setValue(medz)
            a.atto.write('seta 4 '+str(medz))
        
    def ExtUpZ(self):
        
        euz = self.ZOffChange.value()
        peuz = euz + 0.1
        self.ZOffChange.setValue(peuz)
        a.atto.write('seta 4 '+str(peuz))
        
#   Run GUI        

# main script run in application       
if __name__ == '__main__':
    
    # define run function, which can be terminated without failing
    def run():
        
        # define the GUI as QApplication to get all properties for it
        app = QApplication(sys.argv)
        # rename the GUI window to be able to assign functions to it
        gui = Window()
        # show the GUI window
        gui.show()
        # start the whole application
        app.exec_()
        
    # run the GUI code (whole script)
    run()
