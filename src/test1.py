import logging
import threading
from websocket_server import WebsocketServer
from socket import *

# API https://github.com/Pithikos/python-websocket-server
# 回调

# task queue
tasks = []

ips = ["192.122.236.104", "164.67.126.43", "143.215.216.194"]

clients = [None] * 3
available_machine = [True, True, True]
dict = {}


def message_received(client, server, message):
    clientID = client["id"]

    # 接收到了uri

    if clientID in dict: #如果client之前有发过来message, 就把这个message加到client 之前message的末端。client 里面应该有几个field，不知道能不能直接用client来当key.
        dict[clientID][1] += message
        if (message.endswith("\n")):#如果这个message是\n结尾，那就说明这个uri传完了，我们有一个完整的uri
            print("get full message:")
            print(message)
            tasks.append((dict[clientID][0], dict[clientID][1]))#把这个client和他完整的uri放到tasks里面
            dict.pop(clientID) #把这个client和他的message从dictionary移除，避免之后这个client发过来，我们把他新的uri和旧的uri连在一起
    else: #这个uri是新的，之前没有储存过这个client这个uri的数据
        if(message.endswith("\n")):#如果这个message直接以\n结尾，那我们就是一次把整个完整的uri拿到了，就直接放进去tasks
            tasks.append((client, message)) #放进去tasks
        else: #这个uri只是其中一部分，还不完整，我们就把这个uri和对应的client放到dict里面
            dict[clientID] = [client, message] #放到dict里面


    # 储存到tasks queue里
    #tasks.append((client, message))


def load_balance():
    # 从queue中取出下一个task交给后端一台available machine上
    while True:
        if True in available_machine and len(tasks) != 0:
            index = available_machine.index(True)
            available_machine[index] = False  # 锁死
            task = tasks.pop(0)
            print(task)
            client = task[0]  # 获取client
            message = task[1] + "\n"  # 获取url
            clients[index] = client  # 储存client信息
            threading.Thread(target=task_handler, args=(index, message)).start()  # 起线程处理信息


def task_handler(index, message):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((ips[index], 12345))
    s.send(message.encode())  # 发送url
    res = s.recv(4096)  # 接受结果
    client = clients[index]
    clients[index] = None
    available_machine[index] = True  # 解锁
    server.send_message(client, res.decode())  # 向前端返回结果
    s.close()


if __name__ == '__main__':
    # 服务器的ip和端口
    server = WebsocketServer(host='192.41.233.54', port=12345)  # GENI IP: 172.17.4.2
    lb_thread = threading.Thread(target=load_balance)
    server.set_fn_message_received(message_received)
    lb_thread.start()
    server.run_forever()
    print("ok")

                                                                                                                                                                        76,0-1        Bot

