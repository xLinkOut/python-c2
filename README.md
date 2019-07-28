# Python C²
Python Command-n-Control botnet with Tornado WebServer.

# How it works
There is a **Server** that control all the **clients/bots**. It is a webserver and work over http protocol: clients talk with the server via HTTP API, GET and POST request to retrive commands and to send data. On the other side, the admin have a dashboard to control every single client. I'm not a web designer so there is just the essential HTML code without a beautiful UI, you can customize all the admin panel as you want. 

Repository now include "venv" virtual environment so its ready to use: `source src/venv/bin/activate`

# Example
Basically:
1. Client start -> Send to the server an init request
2. The admin select the client, and add a command in queue
3. The client every xx second try to get new command from the server
4. If found a command, execute it and then, if necessary, send some data back to the server
5. Goto 1;

# Install
+ Install dependecies (pip requirements soon)
+ Start the server on a machine
+ Start as many client as you want on other machine
