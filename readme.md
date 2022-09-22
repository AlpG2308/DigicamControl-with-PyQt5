# Automating DigiCamControl Software

In this project we will use the [CameraControlRemote.exe](http://digicamcontrol.com/doc/) to control a Nikon camera with python.
This project will use the python subprocess module to call and control the binary from the commandline.

The basic idea was to be able to take a picture from a python GUI (written with pyQT) with a specific name.
This was necessary for me to later read out sensor data which will be concatenated to the sensor data.

Main aspects to watch out for in this code are the specific code segments to interact with CameraControlRemote.exe

**Specifying a filename**

```python
sbp.run(self.path_remote +
               f" /c set session.filenametemplate {str(self.name)}_{str(self.count)}")
```

**Retrieving iso etc.**

```python
sbp.run(self.path_remote + " /c get iso", capture_output=True, text=True).stdout.split('"')[1]
```

Furthermore a counter was added otherwise the digicam-software will use an default counter, which works in mysterious ways.

The gui2 is just a basic gui with a capture push-button as well as an editing line.
The sensor signals will later be added as a variable to the `Camera_Control` class using pyqt signals.

## Notes about the requirements
The pipfile contains the pandas library which is not necessary for the control of the digicamcontrol software