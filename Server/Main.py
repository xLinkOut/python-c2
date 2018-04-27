#-*- coding:utf-8 -*-

import tornado.web,tornado.options
import os
import Server
import APIs

tornado.options.define("port",type=int,default=6969,help="Run the WebServer on the given port.")
tornado.options.define("html",type=str,default="html",help="Set the directory that contain the html files.")

class Application(tornado.web.Application):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        settings = {
            "cookie_secret": "9x68q0UYqclOhTp4PBnQTNDpVdL49ELbA0I9YBckVjy3n2MgIEMzClFLsico",
            "login_url": "/login",
            "autoreload": True,
            "compiled_template_cache": False
        }
        tornado.web.Application.__init__(self,[
            # Server route
            tornado.web.url(r"/",Server.RootHandler,name="RootHandler"),
            tornado.web.url(r"/login",Server.LoginHandler,name="LoginHandler"),
            tornado.web.url(r"/logout",Server.LogoutHandler,name="LogoutHandler"),
            tornado.web.url(r"/signup",Server.SignupHandler,name="SignupHandler"),
            tornado.web.url(r"/recover",Server.RecoverHandler,name="RecoverHandler"),
            tornado.web.url(r"/token",Server.TokenHandler,name="TokenHandler"),
            tornado.web.url(r"/massive",Server.MassiveHandler,name="MassiveHandler"),            
            tornado.web.url(r"/client/[0-9a-z]+",Server.ClientHandler,name="ClientHandler"),

            # Server APIs
            tornado.web.url(r"/client/api/sysinfo",Server.SysinfoHandler,name="SysinfoHandler"),
            
            # Client APIs
            tornado.web.url(r"/api/init",APIs.InitHandler,name="InitHandler"),
            tornado.web.url(r"/api/getUpdates",APIs.GetUpdatesHandler,name="GetUpdatesHandler"),

        ], **settings)

def main():
    tornado.options.parse_command_line()
    Application().listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()