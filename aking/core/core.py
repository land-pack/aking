import time
import traceback
import logging
import redis
import ujson
import copy

logger = logging.getLogger('simple')

ROOM_PREFIX = 'rs:room'
ROOM_INDEX = 'rs:room:index'            # auto increment if have new room create!
ROOM_MEMBERS = 'rs:room:members:{}'     # a redis set type, the key with rs_id as subfix!
ROOM_MEMBER_SET = 'rs:room:member:set'  # room id set
UID_TO_ROOM = 'rs:uid:room'             # user to room map
UID_TO_INFO = 'rs:uid:to:info:{}'       # for ttl

ROOM_INSIDE_PUB = 'rs:pub:room:{}'       # publish data to the target room
ROOM_ALL_PUB = 'rs:MessageToPlayerOnTheSameRoom'  # publish data to all room

# All your configuration should put as below sample
# you can easy modify on redis client side
CONF_MAIN = 'rs:conf:main:'
CONF_FLAG = 'rs:conf:flag'

# client = redis.Redis(host="localhost", port=6379, db=0)

class RS(object):

    def __init__(self, client):
        self.c = client
        self.conf_reset()


    def destroy(self):
        confirm = raw_input("Destroy all data with RS. Are you sure? [Y/N]") or 'N'
        if confirm.upper() in 'YES':
            all_keys = self.c.keys('rs:*')
            for k in all_keys:
                self.c.delete(k)
            print '[ A ] All key with "rs:*" prefix has delete .Total delete {} keys'.format(len(all_keys))
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
        print 'Room index:{}'.format(self.c.get(ROOM_INDEX))
        all_rs_id = self.c.smembers(ROOM_MEMBER_SET)
        for rs_id in all_rs_id:
            print 'Room member:{}:{}'.format(rs_id, self.c.smembers(ROOM_MEMBERS.format(rs_id)))
        print '=' * 120
    

    def user_join(self, uid):
        rs_id = self.c.hget(UID_TO_ROOM, uid)
        if rs_id:
            logger.warning('[ A ] User has join the room. roomid=%s | uid=%s', rs_id, uid)
            self.update_ttl(uid)
            return rs_id

        # TODO add lock here
        room_size = self.c.hget(CONF_MAIN, 'room_size')
        lst = self.c.zrevrangebyscore(ROOM_PREFIX, room_size, '(0')
        if lst:
            rs_id = lst[0]
            logger.info('[ B ] Find a available room. roomid=%s | uid=%s', rs_id, uid)
        else:
            self.c.incr(ROOM_INDEX)
            rs_id = 'r{}'.format(self.c.get(ROOM_INDEX))
            self.c.sadd(ROOM_MEMBER_SET, rs_id)
            logger.info('[ C ] Create a new room. roomid=%s | uid=%s', rs_id, uid)
         

        self._init(rs_id, uid)
        self.update_ttl(uid)
        self.pub_to_room(rs_id, {'type':'join','uid':uid})
        self.bind_to_player_by_pub({'uid':uid, 'rs_id': rs_id})
        return rs_id

    def bind_to_player_by_pub(self, data):
        self.c.publish("PlayerJoinRoom", ujson.dumps(data))


    def _init(self, rs_id, uid):
        self.c.set(UID_TO_INFO.format(uid), 1)
        self.c.zincrby(ROOM_PREFIX,rs_id, 1)
        self.c.sadd(ROOM_MEMBERS.format(rs_id), str(uid))
        self.c.hset(UID_TO_ROOM, uid, rs_id) #


    def _clear(self, rs_id, uid):
        self.c.hdel(UID_TO_ROOM, uid)
        self.c.srem(ROOM_MEMBERS.format(rs_id), uid)
        self.c.zincrby(ROOM_PREFIX, rs_id, -1)
        self.c.delete(UID_TO_INFO.format(uid))

    def rindex(self):
        """
            Room Index Counter
        """
        return self.c.get(ROOM_INDEX)


    def ttl(self, uid):
        return self.c.ttl(UID_TO_INFO.format(uid))

    def is_alive(self, uid):
        if self.ttl(uid) > 0:
            return True
        else:
            return False


    def user_leave(self, uid):
        rs_id = self.c.hget(UID_TO_ROOM, uid)
        if rs_id:
            self._clear(rs_id, uid)
            logger.info('[ A ] Remove a user. roomid=%s | uid=%s', rs_id, uid)
            return 1
        logger.info('[ B ] Can\'t found tark user. roomid=%s | uid=%s', rs_id, uid)
        return 0


    def update_ttl(self, uid, sec=None):
        """
        Once received a heartbeat from the user, this method will
        be called and then update the expire!
        """
        if not sec:
            sec = int(self.c.hget(CONF_MAIN, 'user_ttl'))
        self.c.expire(UID_TO_INFO.format(uid),sec)


    def clear(self):
        """
        Run every 10 sec, if user has expire, the user will be
        remove from data base and then publish a message to the
        room which the user are used to live!
        """
        all_uid = self.c.hgetall(UID_TO_ROOM)
        for uid, rs_id in all_uid.items():
            if self.is_alive(uid):
                logger.info('[ A ] User has keep alive. roomid=%s | uid=%s', rs_id, uid)
            else:
                logger.info('[ B ] User has die. roomid=%s | uid=%s', rs_id, uid)
                self._clear(rs_id, uid)
                self.pub_to_room(rs_id, {'type':'leave','uid':uid})
        logger.info("Clear function call at %s, clear successful!", time.time())

    

    def flush(self):
        """
        Clear empty room!
        """
        empty_room = self.c.zrangebyscore(ROOM_PREFIX, 0, '(1')
        for rs_id in empty_room:
            self.c.srem(ROOM_MEMBER_SET, rs_id)
            logger.info('[ A ] Flash the room. roomid=%s', rs_id)
        logger.info('[ B ] Flash the room total. total empty room=%s', len(empty_room))
        self.c.zremrangebyscore(ROOM_PREFIX, 0, '(1')
        logger.info("Flush function call at %s, clear successful!", time.time())


    def pub_to_room(self, rs_id, data=''):
        self.c.publish(ROOM_INSIDE_PUB.format(rs_id), data)


    def pub_to_all(self, data=''):
        self.c.publish(ROOM_ALL_PUB, data)


    def sub_from_room(self, rs_id):
        data = self.c.pubsub_channels(ROOM_INSIDE_PUB.format(rs_id))
        return data


    def sub_from_all(self):
        data = self.c.pubsub_channels(ROOM_ALL_PUB)
        return data
    
    def conf_reset(self, init=False):
        reset_flag = self.c.get(CONF_FLAG)
        if init or reset_flag: 
            delete_item = len([self.c.delete(k) for k in self.c.keys(CONF_MAIN)])

        self.c.hsetnx(CONF_MAIN, 'user_xx', 1)
        self.c.hsetnx(CONF_MAIN, 'user_ttl', 15)
        self.c.hsetnx(CONF_MAIN, 'room_size', '(3')

    def conf(self):
        """
            You can easily configure your RoomServer.
            Just call this method.
        """
        conf_keys = self.c.hgetall(CONF_MAIN)
        index_to_keys = {}
        i = 0
        for key, value in conf_keys.items():
            i += 1
            index_to_keys[str(i)]= key
            print '[ A ] {}) {} = {}.'.format(i, key, value)

        i = raw_input("Which item you want to modify? please input index id: ")
        k = index_to_keys.get(str(i))
        if k:
            v = raw_input(" Set {}= ".format(k))
            self.c.hset(CONF_MAIN, k, v)
            print '[ B ] {} has update to {}'.format(key, v)
        else:
            print '[ C ] No match option!'

    def my_member(self, uid):
        rs_id = self.c.hget(UID_TO_ROOM, uid)
        members = self.c.smembers(ROOM_MEMBERS.format(rs_id))
        logger.info("my member all include me -->%s | %s", type(members), members) 
        members.remove(str(uid)) # delete self uid
        logger.info("my member without  me -->%s | %s", type(members), members) 
        return members

            

    
if __name__ == '__main__':
    #print 'should be r1', RS().user_join(2829)
    #RS().sub_from_all()
    RS().clear()
