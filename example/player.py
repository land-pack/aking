import traceback
import time
import ujson
from collections import defaultdict

class Player(object):

    def __init__(self, handler, uid):
        self.handler = handler
        self.uid = uid
        self.member = set()


    def update_before_join(self):
    	"""
    	Override this method, if you want to
    	update to latest information about player!
    	"""
    	self.timeline = time.time()

    def group_chat(self, data):
    	for player in self.member:
    		try:
    			player.handler.write_message(ujson.dumps(data))
    		except:
    			print 'error', traceback.format_exc()

    def __str__(self):
        return '{}'.format(self.uid)

    def __repr__(self):
    	return self.__str__()



class PlayerList(set):

	def __init__(self, rs_id=None, *args, **kwargs):
		self.rs_id = rs_id
		self.uid_to_obj = {}
		super(PlayerList, self).__init__(*args, **kwargs)

	def before_add(self, item):
		"""
		You can override this method, if you do 
		really want to modify the item !
		"""
		item.update_before_join() # can be user information for real time
		return item

	def add(self, item):
		item = self.before_add(item)
		setattr(item, 'member', self)
		super(PlayerList, self).add(item)
		self.uid_to_obj[str(item.uid)] = item

	def remove(self, name):
		item = self.uid_to_obj.get(str(name))
		super(PlayerList, self).remove(item)


class PlayerManager(object):

	rs_id_to_player_list = {}

	@classmethod
	def get(cls, rs_id):
		if rs_id in cls.rs_id_to_player_list:
			return cls.rs_id_to_player_list[rs_id]
		else:
			obj = PlayerList(rs_id)
			cls.rs_id_to_player_list[rs_id] = obj
			return obj


	@classmethod
	def usage(cls):
		return '{}'.format(cls.rs_id_to_player_list)




if __name__ == '__main__':
	# pl = PlayerList()
	# p1 = Player(object(), 123)
	# p2 = Player(object(), 133)
	# pl.add(p1)
	# pl.add(p2)


	# print pl
	# print '=' * 20

	# for p in pl:
	# 	print 'uid->', p.uid, 'timeline->', p.timeline

	# print 'my uid=',p1.uid, 'my frends=', p1.member

	# # p1.group_chat('hello')

	# p3 = Player(object(), 143)
	# pl.add(p3)

	# # p1.group_chat('say')
	# print pl
	# print '=' * 20

	# pl.remove('123')
	# print 'after remove'
	# print pl

	p3 = Player(object(), 143)
	p4 = Player(object(), 144)
	p5 = Player(object(), 145)
	p6 = Player(object(), 146)
	p7 = Player(object(), 147)
	# pl.add(p3)
	pm = PlayerManager.get(2023)
	# pl = pm[2022]
	pm.add(p3)
	pm.add(p4)
	pm.add(p5)
	pm = PlayerManager.get(2024)
	pm.add(p6)
	pm.add(p7)
	# print pl
	print pm
	print PlayerManager.usage()
	# pm.add(item)

