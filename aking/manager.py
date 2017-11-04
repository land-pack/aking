import logging
import logging.config
from tornado import web
from tornado import ioloop
from tornado import websocket
from core.kws import EchoWebSocket
from core.kws import pb
logging.config.fileConfig("./etc/node_log.conf")

if __name__ == '__main__':
	application = web.Application([
	(r'/ws',EchoWebSocket)],
	debug=True)

	application.listen(9777)
	pb.run(ioloop.IOLoop.instance())
	ioloop.IOLoop.instance().start()
