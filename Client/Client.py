#-*- coding:utf-8 -*-
import sys
sys.path.append("modules")

import requests,json
from time import sleep
from uuid import getnode as generateID

SERVER_URL = "http://localhost/api/"
MY_ID = generateID()

def Init():
    r = requests.post(SERVER_URL + "init",data={"id": MY_ID})
    # :todo: aggiungere controlli sull'avvenuta connessione

def Polling():
    response = requests.get(SERVER_URL + "getUpdates?id={}".format(MY_ID))
    data = json.loads(response.text)
    if not data["idle"]:
        return data["command"]
    return False

def main():
    Init()
    while(True):
        command = Polling()
        if command:
            print(command)
        else:
            sleep(5)

if __name__ == "__main__":
    main()