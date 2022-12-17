import lumix_control
import os

IP = "192.168.54.1" #IP of camera
control = lumix_control.CameraControl(IP)

control.get_pics(os.path.join(os.getenv("HOME"), "Pictures/pana/raw/")) #get pictures from camera and save them to ~/Pictures/pana/raw/
