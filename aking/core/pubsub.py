import traceback
import redis
import tornadoredis
from tornado import gen
from tornado import web
from tornado import ioloop
from tornado import websocket

class PubSub(object):


	def __init__(self):
		self.subscribe_channel_set = []
		self.callback_for_channel = {}
		self.subscribe_handler = None

	@gen.engine
	def listen(self):
		yield gen.Task(self.subscribe_handler.subscribe, self.subscribe_channel_set)
		self.subscribe_handler.listen(self.subscribe_callback)

	def run(self, io_loop, r_host='127.0.0.1', r_port=6379, r_db=1):
		self.subscribe_handler = tornadoredis.Client(
				host=r_host,
				port=r_port,
				selected_db=r_db,
				io_loop=io_loop
			)
		self.redis_handler = redis.Redis(
				host=r_host,
				port=r_port,
				db=r_db,)
		self.subscribe_handler.connect()
		self.listen()

	def pub(self, channel, data):
		self.redis_handler.publish(channel, data) 

	def subscribe_callback(self, msg):
		if msg.kind != 'message':
			print 'msg is no kind of message, is ', msg
			return 
		try:
			self.callback_for_channel[msg.channel](msg.channel, msg.body)
		except:
			print 'Error >>', traceback.format_exc()

	def sub(self, channel):
		def _wrapper(func):
			if channel in self.subscribe_channel_set:
				print 'Already subscribe channel: {}'.format(channel)
			else:
				self.subscribe_channel_set.append(channel)
				self.callback_for_channel[channel] = func
				print self.callback_for_channel
			def __wrapper(*args, **kwargs):
				pass
			return __wrapper
		return _wrapper



