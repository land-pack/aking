from tornado import web
from tornado import ioloop
from tornado import websocket
from pubsub import PubSub
from player import Player, PlayerList 


pb = PubSub()

ws_handler = []
player_lst = []


@pb.sub("my_sub")
def my_sub(channel, body):
    print 'channel -->', channel, 'body', body
    global ws_handler
    for handler in ws_handler:
        handler.write_message(body)

@pb.sub("VGuessEventMessage")
def my_sub(channel, body):
    print 'channel -->', channel, 'body', body
    global ws_handler
    for handler in ws_handler:
        handler.write_message(body)

class EchoWebSocket(websocket.WebSocketHandler):
    def prepare(self):
        d = {k:v[0] for k, v in self.request.arguments.iteritems()}
        self.arg = d
        logger.info('websocket arguments:%s', d)

    def check_origin(self, origin):
        return True


    def open(self):
        global ws_handler
        ws_handler.append(self)
        uid = self.arg.get("uid", 0)
        player = Player(self, uid)
        player_lst.append(player)

        print("WebSocket opened")
        self.write_message(u"connected")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        ws_handler.remove(self)
        player_lst.remove(self.arg.uid)
        print("WebSocket closed")



