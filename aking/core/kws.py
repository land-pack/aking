from tornado import web
from tornado import ioloop
from tornado import websocket
from pubsub import PubSub 


pb = PubSub()

@pb.thesub("mysub")
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

	application.listen(9777)
	pb.run(ioloop.IOLoop.instance())
	ioloop.IOLoop.instance().start()
