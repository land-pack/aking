import redis
import ujson
import copy






ROOM_PREFIX = 'rs:room'
ROOM_INDEX = 'rs:room:index'            # auto increment if have new room create!
ROOM_MEMBERS = 'rs:room:members:{}'     # a redis set type, the key with rs_id as subfix!
ROOM_MEMBER_SET = 'rs:room:member:set'  # room id set
UID_TO_ROOM = 'rs:uid:room'             # user to room map
UID_TO_INFO = 'rs:uid:to:info:{}'       # for ttl

ROOM_INSIDE_PUB = 'rs:pub:room:{}'       # publish data to the target room
ROOM_ALL_PUB = 'rs:pub:all'             # publish data to all room

# All your configuration should put as below sample
# you can easy modify on redis client side
CONF_MAIN = 'rs:conf:main'
CF_TTL_KEY = 'ttl:sec'                  # user ttl sec
CF_TTL_DEFAULT = 15                     # user ttl default value if no given ,use this
CF_ROOM_SIZE = '(3'


client = redis.Redis(host="localhost", port=6379, db=0)

class RS(object):

    def destroy(self):
        confirm = raw_input("Destroy all data with RS. Are you sure? [Y/N]") or 'N'
        if confirm.upper() in 'YES':
            all_keys = client.keys('rs:*')
            for k in all_keys:
                client.delete(k)
            print '[ A ] All key with "rs:*" has delete .Total delete {}'.format(len(all_keys))
        else:
            print '[ B ] Keep store it ..'


    def usage(self):
        """

               -------------------
                /\   || // 
               //\\  ||//
              //--\\ ||\\
             //    \\|| \\ 
        =====================
        """
        print '=' * 120
        print 'Room index:{}'.format(client.get(ROOM_INDEX))
        all_rs_id = client.smembers(ROOM_MEMBER_SET)
        for rs_id in all_rs_id:
            print 'Room member:{}:{}'.format(rs_id, client.smembers(ROOM_MEMBERS.format(rs_id)))
        print '=' * 120
    

    def user_join(self, uid):
        rs_id = client.hget(UID_TO_ROOM, uid)
        if rs_id:
            print '[ A ] User has join the room. roomid={} | uid={}'.format(rs_id, uid)
            self.update_ttl(uid)
            return rs_id
    
        lst = client.zrevrangebyscore(ROOM_PREFIX, CF_ROOM_SIZE, '(0')
        if lst:
            rs_id = lst[0]
            print '[ B ] Find a available room. roomid={} | uid={}'.format(rs_id, uid)
        else:
            client.incr(ROOM_INDEX)
            rs_id = 'r{}'.format(client.get(ROOM_INDEX))
            client.sadd(ROOM_MEMBER_SET, rs_id)
            print '[ C ] Create a new room. roomid={} | uid={}'.format(rs_id, uid)
         

        self._init(rs_id, uid)
        self.update_ttl(uid)
        self.pub_to_room(rs_id, {'type':'join','uid':uid})
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


    def update_ttl(self, uid, sec=None):
        """
        Once received a heartbeat from the user, this method will
        be called and then update the expire!
        """
        if not sec:
            ttl_value = client.hget(CONF_MAIN, CF_TTL_KEY) or CF_TTL_DEFAULT
            sec = int(ttl_value)
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
        empty_room = client.zrangebyscore(ROOM_PREFIX, 0, '(1')
        for rs_id in empty_room:
            client.srem(ROOM_MEMBER_SET, rs_id)
            print '[ A ] Flash the room. roomid={}'.format(rs_id)
        print '[ B ] Flash the room total. total empty room={}'.format(len(empty_room))
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
