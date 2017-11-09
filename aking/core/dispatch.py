import logging
import redis
import ujson
from core import RS
from tornado import ioloop
from fake_data import init_data

client = redis.Redis(host="localhost", port=6379, db=0)
rs = RS(client=client)


logger = logging.getLogger('simple')

rs.clear() # clean the die-user
rs.flush() # clean the empty-room

ioloop.PeriodicCallback(rs.clear, 4 * 1000).start()
ioloop.PeriodicCallback(rs.flush, 20 * 1000).start()


class BaseMsgManager(object):


	def user_join(self, handler, data):
		logger.debug('data type=%s | data=%s', type(data), data)
		uid = data.get("uid")
		rs.user_join(uid)
		packet = {
			"receivers": rs.my_member(uid),
			"content": {
                    "msg_type":"user_join",
                    "msg_id":"226",
                    "data":{
                        "uid": uid,
                        "phone":"137xxxx"
                    }
                }
            }
		rs.pub_to_all(ujson.dumps(packet))

		ret = {
			"msg_type": "ack_user_join",
			"msg_id": "124",
			"data":{
				}
			}
		ret = init_data		
		return ret 


	def user_leave(self, handler, data):
		logger.debug('data type=%s | data=%s', type(data), data)
		uid = data.get("uid")
		packet = {
			"receivers": rs.my_member(uid),
			"content": {
                    "msg_type":"user_leave",
                    "msg_id":"228",
                    "data":{
                        "uid": uid,
                        "phone":"137xxxx"
                    }
                }
            }
		rs.pub_to_all(ujson.dumps(packet))


class Dispatch(object):
	def __init__(self, MsgManager):
		self.msg_manager = MsgManager()

	def route(self, handler, packet):
		"""
		{
			"msg_type": "user_join",
			"msg_id":"123",
			"data":{
			}
		}
		"""
		try:
			data = ujson.loads(packet)
		except:
			logger.error('data format error')
		else:
			func_name = data.get('msg_type')
			data = data.get("data")
			ret = getattr(self.msg_manager, func_name, self.default_func)(handler, data)
		if not ret : return
		try:	
			handler.write_message(ujson.dumps(ret))
		except:
			logger.error('return message error format ')
	def call(self, handler, func_name, data):
	# Don't care about return value
		getattr(self.msg_manager, func_name, self.default_func)(handler, data)

	def default_func(self, handler, data):
		print 'run default function'
		handler.write_message("default function")
