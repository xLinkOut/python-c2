#-*- coding:utf-8 -*-

import tornado.web
import Utility

class GetUpdatesHandler(tornado.web.RequestHandler):
    def get(self):
        client_id = self.get_argument("id")
        command = Utility.DB.selectQuery("SELECT COMMAND_ID,COMMAND FROM QUEUE WHERE CLIENT_ID=?",[client_id])
        if command == None:
            self.write({"ok":True,"idle":True})
        else:
            self.write({"ok":True,"idle":False,"command":{"id": command[0],"command": command[1]}})

class InitHandler(tornado.web.RequestHandler):
    def get(self):
        client_id = self.get_argument("id")
        exists = Utility.DB.selectQuery("SELECT * FROM CLIENTS WHERE ID=?",[client_id])
        if exists:
            # Client già registrato nel database
            self.write("Il client è registrato")
        else:
            self.write("Il client non è registrato")

    def post(self):
        client_id = self.get_body_argument("id")
        exists = Utility.DB.selectQuery("SELECT * FROM CLIENTS WHERE ID=?",[client_id])
        if exists:
            # Client già registrato nel database
            self.write({"ok":True,"status":"already exists"})
        else:
            # Nuovo client
            Utility.DB.executeQuery("INSERT INTO CLIENTS(ID) VALUES(?)",[client_id])
            self.write({"ok":True,"status":"client registered"})