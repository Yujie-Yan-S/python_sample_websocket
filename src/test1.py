import logging
import threading
from websocket_server import WebsocketServer
from socket import *

# API https://github.com/Pithikos/python-websocket-server
# Note that list structure is thread-safe in python. Deadlock is not possible in this program

# task queue
tasks = []

# backend machine IP addresses
ips = ["192.122.236.104", "164.67.126.43", "143.215.216.194"]

clients = [None] * 3
available_machine = [True, True,
                     True]  # list to lock backend machines and block potential data transferring to the working machines
dict = {}  # dictionary to store pending messages


def message_received(client, server, message):
    clientID = client["id"]

    # Received URI

    if clientID in dict:  # If the client hasn't finished receiving messages, append the continued message to the dictionary
        dict[clientID][1] += message
        if (message.endswith("\n")):  # URI ends with '\n'
            print("get full message:")
            print(message)
            tasks.append((dict[clientID][0], dict[clientID][1]))  # append a tuple of client and its completed message
            dict.pop(clientID)  # remove the finished client from the dictionary
    else:  # situation when the message is new
        if (message.endswith("\n")):  # if ends with '\n', it means end of a complete message
            tasks.append((client, message))  # add to tasks
        else:  # otherwise add this new client-message pair to the dictionary
            dict[clientID] = [client, message]


def load_balance():
    # This function is executed by a thread. Take out a task and send to appropriate backend machines
    while True:
        if True in available_machine and len(tasks) != 0:
            index = available_machine.index(True)
            available_machine[index] = False  # lock the machine
            task = tasks.pop(0)
            print(task)
            client = task[0]  # get client
            message = task[1] + "\n"  # get URI
            clients[index] = client  # store the client info
            threading.Thread(target=task_handler,
                             args=(index, message)).start()  # start a thread to handle the task in a backend machine


def task_handler(index, message):
    s = socket(AF_INET, SOCK_STREAM)  # Establish TCP connection with the backend
    s.connect((ips[index], 12345))
    s.send(message.encode())  # send URI to backend
    res = s.recv(4096)  # accept
    client = clients[index]
    clients[index] = None
    available_machine[index] = True  # unlock the machine
    server.send_message(client, res.decode())  # send result to the frontend
    s.close()  # close socket


if __name__ == '__main__':
    server = WebsocketServer(host='192.41.233.54', port=12345)  # create websocket
    lb_thread = threading.Thread(target=load_balance)  # start load_balance
    server.set_fn_message_received(message_received)
    lb_thread.start()
    server.run_forever()  # Run websocket server
    print("ok")
