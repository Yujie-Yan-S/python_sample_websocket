import logging
import threading
from websocket_server import WebsocketServer
from socket import *

# API https://github.com/Pithikos/python-websocket-server
# 回调

# task queue
tasks = []

sockets = []
sockets[0] = socket(AF_INET, SOCK_STREAM)
sockets[0].connect((IP_Address, 12345))

sockets[1] = socket(AF_INET, SOCK_STREAM)
sockets[1].connect((IP_Address, 12345))

sockets[2] = socket(AF_INET, SOCK_STREAM)
sockets[2].connect((IP_Address, 12345))


def message_received(client, server, message):
    # 接收到了uri
    # 储存到tasks queue里
    tasks.append(message)
    # server.send_message(client,message)
    # 处理返回图片的分类数据


def message_handler():
    available_machine = [True, True, True]
    # 从queue中取出下一个task交给后端
    while True:
        if True in available_machine and len(tasks) != 0:
            index = available_machine.index(True)
            task = tasks.pop(0)
            available_machine[index] = False
            threading.Thread(target=send_task, args=(sockets[index], task)).start()


def send_task(s, message):
    s.send(message.encode())


if __name__ == '__main__':
    # 服务器的ip和端口
    server = WebsocketServer(host='127.0.0.1', port=9001)

    # 拿到ws的message的时候call 回调函数
    server.set_fn_message_received(message_received)
    server_thread = threading.Thread(target=server.run_forever)
    server_thread.start()
    threading.Thread(target=message_handler).start()
    print("ok")
