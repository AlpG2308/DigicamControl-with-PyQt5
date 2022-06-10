import pandas as pd
import subprocess as sbp

file = "./datatest.csv"
path_remote = "C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"

def read_data (file):
    data = pd.read_csv(file)
    return data
value_df = read_data (file)
value = value_df.Voltage[0]
def run_liveview (path_remote):
    #sbp.run(path_remote + " /c do LiveViewWnd_Hide")
    #sleep(0.5)
    full_path = path_remote + " /c do LiveViewWnd_Show"
    sbp.run(full_path)
def hide_liveview(path_remote):
    sbp.run(path_remote + " /c do LiveViewWnd_Hide")

class Camera_Control():
    """This class can control a Nikon camera using the CamControlRemote.exe from digicam control. This class and the
     capture fuction is only callable if the digicamcontrol sofware is open and LiveView is started.
     __init__ initializes a session with the desired name, iso and aperture. While the capture function just takes a live view picture.
     The remote exe is only callable via the cmd and therefore subprocess run was used.
     http://digicamcontrol.com/
    """
    def __init__ (self, path_remote, name):
        self.path_remote = path_remote
        self.name = name
        #self.ampere = ampere
        #self.voltage = voltage
        self.iso= sbp.run(self.path_remote + " /c get iso", capture_output=True, text=True).stdout.split('"')[1]
        self.aperture = sbp.run(self.path_remote + " /c get aperture", capture_output=True, text=True).stdout.split('"')[1]


        #sbp.run(self.path_remote +
        #        f" /c set session.filenametemplate {str(self.name)}_{str(self.voltage)}eV_{str(self.ampere)}A")
        sbp.run(self.path_remote +
                f" /c set session.filenametemplate {str(self.name)}_{str(self.iso)}eV_{str(self.aperture)}A")


    def capture(self,path_remote):
        full_path = self.path_remote + " /c do LiveView_Capture"
        sbp.run(full_path)

if __name__ == "__main__":
    image = Camera_Control(path_remote, "test")
    image.capture(path_remote)