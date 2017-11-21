import core
import redis
r = redis.Redis()

akg = core.AKG(client=r)

if __name__ == '__main__':
	akg.run(port=9788)