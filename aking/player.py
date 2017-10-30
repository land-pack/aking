import time
from collections import defaultdict

class Player(object):

    def __init__(self, handler, uid):
        self.handler = handler
        self.uid = uid

    def update_before_join(self):
    	self.timeline = time.time()

    def __str__(self):
        return '{}'.format(self.uid)

    def __repr__(self):
    	return self.__str__()



class PlayerList(set):
	def before_add(self, item):
		"""
		You can override this method, if you do 
		really want to modify the item !
		"""
		item.update_before_join() # can be user information for real time
		return item

	def add(self, item):
		item = self.before_add(item)
		super(PlayerList, self).add(item)


if __name__ == '__main__':
	pl = PlayerList()
	p1 = Player(object(), 123)
	p2 = Player(object(), 133)
	pl.add(p1)
	pl.add(p2)

	print pl

	for p in pl:
		print 'uid->', p.uid, 'timeline->', p.timeline


