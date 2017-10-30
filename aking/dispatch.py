import redis
import ujson
from core import RS

client = redis.Redis(host="localhost", port=6379, db=0)
rs = RS(client=client)


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
			print 'data format error'
		else:
			func_name = data.get('msg_type')
			data = data.get("data")
			getattr(self.msg_manager, func_name, self.default_func)(handler, data)

	def default_func(self, handler, data):
		print 'run default function'
		handler.write_message("default function")