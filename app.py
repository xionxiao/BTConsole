import sys
import eel
import serial
import platform
import threading
from serial.tools import list_ports

eel.init('web-ui')

comm = None
running = True
thread = None


@eel.expose('list_ports')
def list_serial_ports():
    port_list = list(list_ports.comports())
    return [str(p.device) for p in port_list]


@eel.expose
def connect(port):
    global comm
    global thread
    comm = serial.Serial(port, 115200, timeout=1)
    print('connected', comm)
    thread = start_thread()


@eel.expose
def disconnect():
    global running
    running = False


@eel.expose
def send(msg):
    msg = msg + '\r\n'
    if comm:
        comm.write(msg.encode('ascii'))
        print('send', msg)


def capture():
    global comm
    global running
    if not comm:
        return
    while running:
        msg = comm.readline()
        if msg:
            try:
                msg = msg.decode('utf-8').rstrip()
                print(msg)
                eel.receive(msg + '\n')
            except:
                continue
    comm.close()
    print('comm closed')


def start_thread():
    global running
    running = True
    thread = threading.Thread(target=capture)
    thread.start()
    return thread


def exit_app(*args, **kwargs):
    global running
    global thread
    running = False
    if thread:
        thread.join()
    sys.exit()


if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
    mode = 'edge'
else:
    mode = 'chrome'

eel.start('index.html',
          size=(600, 600),
          mode=mode,
          port=0,
          close_callback=exit_app)
