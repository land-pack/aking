import traceback
import logging
import ujson
from tornado import web
from tornado import ioloop
from tornado import websocket
from pubsub import PubSub
from dispatch import BaseMsgManager, Dispatch

logger = logging.getLogger('simple')

pb = PubSub()
dispatch_obj = Dispatch(MsgManager=BaseMsgManager)

ws_handler = []
player_lst = []
uid_to_handler = {}

# Player connect success and then generate a player object!
player_id_to_object = {}


@pb.sub("my_sub")
def my_sub(channel, body):
    pb.pub("rs:MessageToPlayerOnTheAllRoom", body)
    logger.debug("publish to all")

@pb.sub("VGuessEventMessage")
def vguess_event_message(channel, body):
    print 'channel -->', channel, 'body', body
    global ws_handler
    for handler in ws_handler:
        handler.write_message(body)

@pb.sub("rs:MessageToPlayerOnTheAllRoom")
def message_to_player_on_the_all_room(channel, body):
    logger.debug('channel -->%s | body=%s', channel, body)
    data = ujson.loads(body)
    uids =  uid_to_handler.keys()
    content = data.get("content")
    for uid in uids:
        try:
            handler = uid_to_handler.get(str(uid))
            handler.write_message(content)
            logger.info("Send Message to uid=%s | data=%s", uid, content)
        except:
            logger.error(traceback.format_exc())

@pb.sub("rs:MessageToPlayerOnTheSameRoom")
def message_to_player_on_the_same_room(channel, body):
    logger.debug('channel -->%s | body=%s', channel, body)
    data = ujson.loads(body)
    uids =  data.get("receivers")
    content = data.get("content")
    for uid in uids:
        try:
            handler = uid_to_handler.get(str(uid))
            handler.write_message(content)
            logger.info("Send Message to uid=%s | data=%s", uid, content)
        except:
            logger.error(traceback.format_exc())

@pb.sub("rs:UserTTLHasExpire")
def user_ttl_has_expire(channel, body):
    data = ujson.loads(body)
    uid = data.get("uid")
    logger.debug("publish to player who has expire ttl ~%s", uid)

    try:
        print '...........1111'
        handler = uid_to_handler.get(str(uid))
        handler.close()
        print '...........2222'
    except:
        logger.error(traceback.format_exc())
    else:
        logger.info("Close handler uid=%s | reason : ttl has expire~", uid)



class EchoWebSocket(websocket.WebSocketHandler):
    def prepare(self):
        d = {k:v[0] for k, v in self.request.arguments.iteritems()}
        self.arg = d
        logger.info('websocket arguments:%s', d)


    def check_origin(self, origin):
        return True


    def open(self):
        logger.info("WebSocket opened")
        uid = self.arg.get("uid", 0)
        logger.debug("open websocket with uid=%s", uid)
        uid_to_handler[uid] =  self


    def on_message(self, message):
        logger.info("WebSocket message")
        dispatch_obj.route(self, message)


    def on_close(self):
        print '...........3333'
        uid = self.arg.get("uid", 0)
        del uid_to_handler[uid]
        print '...........4444'
        logger.info("WebSocket closed")
        dispatch_obj.call(self, "user_leave",data={"uid":uid})




