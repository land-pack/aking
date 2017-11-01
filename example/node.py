from collections import defaultdict
import redis
from tornado import web
from tornado import ioloop
from tornado import websocket

connect_map = defaultdict(set)

class ConnectMap(dict):
	def __setitem__(self, key ,value):
		super(ConnectMap, self).__setitem__(key, value)

d = ConnectMap()

class EchoWebSocket(websocket.WebSocketHandler):

	def prepare(self):
		[setattr(self, '{}'.format(k), v[0])
		for k, v in self.request.arguments.iteritems()]

	def check_origin(self, origin):
		return True


	def open(self):
		print("WebSocket opened")
		self.write_message(u"connected")
		d[self.uid] = self


	def on_message(self, message):
		
		# self.write_message(u"You said: " + message)
		# Dispatch(MsgManager=ExampleMsgManager).route(self, message)


	def on_close(self):
		print("WebSocket closed")


if __name__ == '__main__':
	application = web.Application([
	(r'/ws',EchoWebSocket)],
	debug=True)

	application.listen(7777)
	ioloop.IOLoop.instance().start()