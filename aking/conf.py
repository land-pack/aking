import redis
from core.core import RS


if __name__ == '__main__':
	r = redis.Redis()
	rs = RS(r)
	rs.conf()
