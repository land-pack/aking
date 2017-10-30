class ExampleMsgManager(object):
	def user_join(self, handler, data):
		print 'recv data ', data

	def user_leave(self, handler, data):
		print 'recv data ', data