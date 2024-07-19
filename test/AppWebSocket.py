
from flask import Flask
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

app = Flask(__name__)
sockets = Sockets(app)

@sockets.route('/humanchat')
def chat_socket(ws):
    # 获取WebSocket对象
    #ws = request.environ.get('wsgi.websocket')
    # 如果没有获取到，返回错误信息
    if not ws:
        print('未建立连接！')
        return 'Please use WebSocket'
    # 否则，循环接收和发送消息
    else:
        print('建立连接！')
        while True:
            message = ws.receive()
            if len(message)==0:
                ws.send('输入信息为空')
            else:
                ws.send(f'received: {message}')

if __name__ == '__main__':
    print('start websocket server')
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()
    
    