import lumix_control
from PIL import Image, ImageTk
import io
import time
import socket
from tkinter import Tk, Label
from threading import Thread

#This gets more and more out of sync.

IP = "192.168.54.1" #IP of camera
control = lumix_control.CameraControl(IP)
my_ip = "0.0.0.0"
my_stream_port = 12345

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((my_ip, my_stream_port))
    s.settimeout(10)
    return s

control.start_stream(my_stream_port)

root = Tk()

label = Label()
label.pack()

def daemon():
    stream_socket = connect()
    t = time.time()
    while 1:
        try:
            data = stream_socket.recv(1024 * 512 * 1) # 0.5MB
            data = data[data.find(b'\xff\xd8'):]
        except socket.timeout:
            control.start_stream(my_stream_port)
            continue
        if not data:
            control.start_stream(my_stream_port)
            continue
        if time.time() - t > 5:
            control.get_state()
            t = time.time()
        if data[-2:] != b'\xff\xd9':
            print('no end of jpeg found from stream')
            continue
        img = Image.open(io.BytesIO(data))
        try:
            img_widget = ImageTk.PhotoImage(img)
        except (RuntimeError, AttributeError):
            print("Window closed, exiting.")
            exit(0)
        label.configure(image=img_widget)
        label.image = img_widget


t = Thread(target=daemon)
t.start()

root.mainloop()

t.join()
