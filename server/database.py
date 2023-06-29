import sqlite3
import socket

#same order as table columns (not including ip, gets added from socket)
elements = ('hostname','nickname','uuid')

class data:
    def __init__(self,db):
        # Connect/Create to database and create table if not existed
        self.db = db
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS clients(ip VARCHAR(100),hostname VARCHAR(100),nickname VARCHAR(100),uuid VARCHAR(100) PRIMARY KEY)''')
        except:
            pass

    def populate(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''SELECT * FROM clients''')
        results = c.fetchall()
        clients = []
        for item in results:
            cli = []
            cli.append((socket.socket()))
            cli.append((item[0],0))
            info = {}
            for i in range(1,len(item)):
                info.update({elements[i-1]:item[i]})
            cli.append(info)
            clients.append(cli)
        return clients

    def update(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        #values to update
        ip = client[1][0]
        hostname = client[2]['hostname']
        c.execute('''UPDATE clients SET ip = ?, hostname = ? WHERE uuid=?''',(ip,hostname,client[2]['uuid']))
        conn.commit()

    def new(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        info = [client[1][0]]
        for i in client[2]:
            info.append(client[2][i])
        c.execute('''INSERT INTO clients VALUES(?,?,?,?)''',info)
        conn.commit()

    def remove(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''DELETE FROM clients WHERE uuid=?''',(client[2]['uuid'],))
        conn.commit()

    def setnick(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        nickname = client[2]['nickname']
        c.execute('''UPDATE clients SET nickname = ? WHERE uuid=?''',(nickname,client[2]['uuid'],))
        conn.commit()