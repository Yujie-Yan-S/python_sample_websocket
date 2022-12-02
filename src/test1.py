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


def message_received(client, message):
    # 接收到了uri
    # 储存到tasks queue里
    tasks.append((client, message))


def load_balance():
    # 从queue中取出下一个task交给后端一台available machine上
    while True:
        if True in available_machine and len(tasks) != 0:
            index = available_machine.index(True)
            available_machine[index] = False  # 锁死
            task = tasks.pop(0)
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
    server.send_message(client, res)  # 向前端返回结果
    s.close()


if __name__ == '__main__':
    # 服务器的ip和端口
    server = WebsocketServer(host='127.0.0.1', port=9001)  # GENI IP: 172.17.4.2
    server.set_fn_message_received(message_received)
    server_thread = threading.Thread(target=server.run_forever)
    lb_thread = threading.Thread(target=load_balance)

    server_thread.start()
    lb_thread.start()
    print("ok")
