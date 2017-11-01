import traceback
import redis
import tornadoredis
from tornado import gen
from tornado import web
from tornado import ioloop
from tornado import websocket

subscribe_channel_set = []
callback_for_channel = {}
subscribe_handler = None

@gen.engine
def listen():
	global subscribe_handler
	yield gen.Task(subscribe_handler.subscribe, subscribe_channel_set)
	subscribe_handler.listen(subscribe_callback)

def run(io_loop):
	global subscribe_handler
	subscribe_handler = tornadoredis.Client(
			host='127.0.0.1',
			port=6379,
			selected_db=1,
			io_loop=io_loop
		)
	subscribe_handler.connect()

	listen()




	# @classmethod
def subscribe_callback(msg):
	global subscribe_callback, callback_for_channel
	if msg.kind != 'message':
		print 'msg is no kind of message, is ', msg
		return 
	try:
		callback_for_channel[msg.channel](msg.channel, msg.body)
	except:
		print 'Error >>', traceback.format_exc()

	# @classmethod
def thesub(channel):
	global subscribe_callback, callback_for_channel
	def _wrapper(func):
		if channel in subscribe_channel_set:
			print 'Already subscribe channel: {}'.format(channel)
		else:
			subscribe_channel_set.append(channel)
			callback_for_channel[channel] = func
			print callback_for_channel
		def __wrapper(*args, **kwargs):
			pass
		return __wrapper
	return _wrapper



@thesub("mysub")
def my_sub(channel, body):
	print 'channel -->', channel, 'body', body


class EchoWebSocket(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True


	def open(self):
		print("WebSocket opened")
		self.write_message(u"connected")

	def on_message(self, message):
		self.write_message(u"You said: " + message)

	def on_close(self):
		print("WebSocket closed")


if __name__ == '__main__':
	application = web.Application([
	(r'/ws',EchoWebSocket)],
	debug=True)

	application.listen(7777)
	run(ioloop.IOLoop.instance())
	ioloop.IOLoop.instance().start()