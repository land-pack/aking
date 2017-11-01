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
		# global self.subscribe_handler
		yield gen.Task(self.subscribe_handler.subscribe, self.subscribe_channel_set)
		self.subscribe_handler.listen(self.subscribe_callback)

	def run(self, io_loop):
		# global self.subscribe_handler
		self.subscribe_handler = tornadoredis.Client(
				host='127.0.0.1',
				port=6379,
				selected_db=1,
				io_loop=io_loop
			)
		self.subscribe_handler.connect()
		self.listen()


	def subscribe_callback(self, msg):
		# global subscribe_callback, self.callback_for_channel
		if msg.kind != 'message':
			print 'msg is no kind of message, is ', msg
			return 
		try:
			self.callback_for_channel[msg.channel](msg.channel, msg.body)
		except:
			print 'Error >>', traceback.format_exc()

	def thesub(self, channel):
		# global subscribe_callback, self.callback_for_channel
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



