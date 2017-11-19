import redis
from core.core import RS


r = redis.Redis()
rs = RS(r)


rs.usage()
