from tornado import web
from tornado import ioloop
from tornado import websocket
from kws import EchoWebSocket
from kws import pb


if __name__ == '__main__':
	application = web.Application([
	(r'/ws',EchoWebSocket)],
	debug=True)

	application.listen(9777)
	pb.run(ioloop.IOLoop.instance())
	ioloop.IOLoop.instance().start()
