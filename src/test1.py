import logging
from websocket_server import WebsocketServer

# API https://github.com/Pithikos/python-websocket-server
# 回调
def message_received(client, server, message):
    print(message)
    # 接收到了uri
    #分发给后端拿到结果 储存在message里面
    message = 'fake reesult'
    server.send_message(client,message)
    # 处理返回图片的分类数据

# 服务器的ip和端口
server = WebsocketServer(host='127.0.0.1', port=9001, loglevel=logging.INFO)

# 拿到ws的message的时候call 回调函数
server.set_fn_message_received(message_received)
server.run_forever()