import redis
import ujson
import copy


MAX_GOLD = 1000
PREFIX = 'prefix_key'
ROOM_INDEX = 'rs:room:index'
ROOM_PREFIX = 'rs:room'
ROOM_MEMBERS = 'rs:room:members:{}'
ROOM_MAX_MEMBERS = '(3'
UID_TO_ROOM = 'rs:uid:room'
UID_TO_INFO = 'rs:uid:to:info:{}' # for ttl
ROOM_INSIDE_PUB = 'rs:pub:room{}'
ROOM_ALL_PUB = 'rs:pub:all'


client = redis.Redis(host="localhost", port=6379, db=0)
class RS(object):

    def usage(self):
        """
        Usage:
            --------------@!@
                     || // 
               //\\  ||//
              //--\\ ||\\
             //    \\|| \\ 
            ==================
        """
        pass
    
    def user_join(self, uid):
        rs_id = client.hget(UID_TO_ROOM, uid)
        if rs_id:
            print '[ A ] User has join the room. roomid={} | uid={}'.format(rs_id, uid)
            self.update_ttl(uid)
            return rs_id
    
        lst = client.zrevrangebyscore(ROOM_PREFIX, ROOM_MAX_MEMBERS, '(0')
        if lst:
            rs_id = lst[0]
            print '[ B ] Find a available room. roomid={} | uid={}'.format(rs_id, uid)
        else:
            client.incr(ROOM_INDEX)
            rs_id = 'r{}'.format(client.get(ROOM_INDEX))
            print '[ C ] Create a new room. roomid={} | uid={}'.format(rs_id, uid)
         

        self._init(rs_id, uid)
        self.update_ttl(uid)
        return rs_id

    def _init(self, rs_id, uid):
        client.set(UID_TO_INFO.format(uid), 1)
        client.zincrby(ROOM_PREFIX,rs_id, 1)
        client.sadd(ROOM_MEMBERS.format(rs_id), str(uid))
        client.hset(UID_TO_ROOM, uid, rs_id) #

    def _clear(self, rs_id, uid):
        client.hdel(UID_TO_ROOM, uid)
        client.srem(ROOM_MEMBERS.format(rs_id), uid)
        client.zincrby(ROOM_PREFIX, rs_id, -1)
        client.delete(UID_TO_INFO.format(uid))

    def is_alive(self, uid):
        if client.get(UID_TO_INFO.format(uid)):
            return True
        else:
            return False


    def user_leave(self, uid):
        rs_id = client.hget(UID_TO_ROOM, uid)
        if rs_id:
            self._clear(rs_id, uid)
            print '[ A ] Remove a user. roomid={} | uid={}'.format(rs_id, uid)
            return 1
        print '[ B ] Can\'t found tark user. roomid={} | uid={}'.format(rs_id, uid)
        return 0

    def update_ttl(self, uid, sec=15):
        """
        Once received a heartbeat from the user, this method will
        be called and then update the expire!
        """
        client.expire(UID_TO_INFO.format(uid),sec)


    def clear(self):
        """
        Run every 10 sec, if user has expire, the user will be
        remove from data base and then publish a message to the
        room which the user are used to live!
        """
        all_uid = client.hgetall(UID_TO_ROOM)
        for uid, rs_id in all_uid.items():
            if self.is_alive(uid):
                print '[ A ] User has keep alive. roomid={} | uid={}'.format(rs_id, uid)
            else:
                print '[ B ] User has keep die . roomid={} | uid={}'.format(rs_id, uid)
                self._clear(rs_id, uid)
                self.pub_to_room(rs_id, {'type':'leave','uid':uid})

    
    def flash(self):
        """
        Clear empty room!
        """
        client.zremrangebyscore(ROOM_PREFIX, 0, '(1')

    def pub_to_room(self, rs_id, data=''):
        client.publish(ROOM_INSIDE_PUB.format(rs_id), data)

    def pub_to_all(self, data=''):
        client.publish(ROOM_ALL_PUB, data)

    def sub_from_room(self, rs_id):
        data = client.pubsub_channels(ROOM_INSIDE_PUB.format(rs_id))
        return data

    def sub_from_all(self):
        data = client.pubsub_channels(ROOM_ALL_PUB)
        return data


    
if __name__ == '__main__':
    #print 'should be r1', RS().user_join(2829)
    #RS().sub_from_all()
    RS().clear()
