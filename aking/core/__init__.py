from tornado import ioloop
from tornado import web
from core import RS 
from dispatch import BaseMsgManager, Dispatch
from kws import EchoWebSocket
from pubsub import PubSub
from kws import pb
import utils.color


class AKG(object):
	def __init__(self, client=None):
		pass 


	def to_all(self, data):
		pass


	def to_part(self, data):
		pass


	def sub(self):
		pass 

	def run(self, debug=True, port=9777):
		application = web.Application([
		(r'/ws',EchoWebSocket)],
		debug=debug)

		application.listen(port)
		pb.run(ioloop.IOLoop.instance())
		ioloop.IOLoop.instance().start()
