import sqlite3
import socket

class data:
    def __init__(self,db):
        # Connect/Create to database and create table if not existed
        self.db = db
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS clients(ip VARCHAR(100),name VARCHAR(100),nickname VARCHAR(100),uuid VARCHAR(100) PRIMARY KEY)''')
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
            hostname = item[1]
            nickname = item[2]
            uuid = item[3]
            info = {'hostname':hostname,'nickname':nickname,'uuid':uuid}
            cli.append(info)
            clients.append(cli)
        return clients

    def update(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        ip = client[1][0]
        name = client[2]['hostname']
        c.execute('''SELECT nickname FROM clients WHERE uuid=?''',(client[2]['uuid'],))
        results = c.fetchall()
        nickname = results[0][0]
        c.execute('''UPDATE clients SET ip = ?, name = ? WHERE uuid=?''',(ip,name,client[2]['uuid'],))
        conn.commit()
        return nickname
        
    def setnick(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        nickname = client[2]['nickname']
        c.execute('''UPDATE clients SET nickname = ? WHERE uuid=?''',(nickname,client[2]['uuid'],))
        conn.commit()

    def new(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        ip = client[1][0]
        name = client[2]['hostname']
        nickname = client[2]['nickname']
        uuid = client[2]['uuid']
        c.execute('''INSERT INTO clients VALUES(?,?,?,?)''',(ip,name,nickname,uuid))
        conn.commit()

    def remove(self,client):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''DELETE FROM clients WHERE uuid=?''',(client[2]['uuid'],))
        conn.commit()