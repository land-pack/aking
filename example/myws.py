from tornado import web
from tornado import ioloop
from tornado import websocket
from dispatch import Dispatch
from msg_manager import ExampleMsgManager


class EchoWebSocket(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True


	def open(self):
		print("WebSocket opened")
		self.write_message(u"connected")

	def on_message(self, message):
		self.write_message(u"You said: " + message)
		Dispatch(MsgManager=ExampleMsgManager).route(self, message)


	def on_close(self):
		print("WebSocket closed")


if __name__ == '__main__':
	application = web.Application([
	(r'/ws',EchoWebSocket)],
	debug=True)

	application.listen(7777)
	ioloop.IOLoop.instance().start()
