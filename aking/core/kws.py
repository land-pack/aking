import logging
import ujson
from tornado import web
from tornado import ioloop
from tornado import websocket
from pubsub import PubSub
from player import Player, PlayerList, PlayerManager
from dispatch import BaseMsgManager, Dispatch

logger = logging.getLogger('simple')

pb = PubSub()
dispatch_obj = Dispatch(MsgManager=BaseMsgManager)

ws_handler = []
player_lst = []
# player_manager = PlayerManager()

# Player connect success and then generate a player object!
player_id_to_object = {}


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


@pb.sub("PlayerJoinRoom")
def player_join_room(channel, body):
    data = ujson.loads(body)
    uid =  str(data.get("uid"))
    rs_id = data.get("rs_id")
    logger.info("user id=%s | room id=%s", uid, rs_id)
    player_list = PlayerManager.get(rs_id)
    player = player_id_to_object[uid]
    player_list.add(player)
    logger.warning("player manager -->%s", PlayerManager.usage())



class EchoWebSocket(websocket.WebSocketHandler):
    def prepare(self):
        d = {k:v[0] for k, v in self.request.arguments.iteritems()}
        self.arg = d
        logger.info('websocket arguments:%s', d)

    def check_origin(self, origin):
        return True


    def open(self):
        logger.info("WebSocket opened")
        # global ws_handler
        # ws_handler.append(self)
        uid = self.arg.get("uid", 0)
        logger.debug("open websocket with uid=%s", uid)
        player_id_to_object[uid] =  Player(self, uid)

        # self.write_message(u"connected")

    def on_message(self, message):
        logger.info("WebSocket message")
        dispatch_obj.route(self, message)

    def on_close(self):
        # ws_handler.remove(self)
        uid = self.arg.get("uid", 0)
        del player_id_to_object[uid]
        logger.info("WebSocket closed")



