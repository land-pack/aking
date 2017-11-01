import ujson
import os
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import tornadoredis


class RepiServer(object):
    def __init__(self, r, name='master', namespace='repi:', info_channel='cluster', port=8888):
        self.redis = r
        self.name = name
        self.namespace = namespace
        self.info_channel = info_channel
        self.port = port


    def subscribe(self, channel):
        channel = self._prefixChannel(channel)
        self.redis.subscribe(channel)


    def unsubscribe(self, channel):
        channel = self._prefixChannel(channel)
        self.redis.unsubscribe(channel)


    def publish(self, command, data=None, channel=None):
        if channel:
            channel = self._prefixChannel(channel)
        else:
            channel = self._prefixChannel(self.info_channel)

        message = {
            'client': self.name,
            'command': command,
            'data': data
        }
        json_message = ujson.dumps(message)
        self.redis.publish(channel, json_message, lambda x: None)


    def run(self):
        application = tornado.web.Application([
            (r'/', MainHandler, dict(repi=self)),
            (r'/ws', RepiConnection, dict(repi=self))
        ])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()


    def _prefixChannel(self, channel):
        return '{}{}'.format(self.namespace, channel)



class MainHandler(tornado.web.RequestHandler):
    def initialize(self, repi, *args, **kwargs):
        self.repi = repi
        super(MainHandler, self).initialize(*args, **kwargs)


    def get(self):
        template_kwargs = {
            'title': 'RePi Server',
            'info_channel': self.repi.info_channel
        }
        self.render(os.path.join('view', 'index.html'), **template_kwargs)




class RepiConnection(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True


    def __init__(self, *args, **kwargs):
        super(RepiConnection, self).__init__(*args, **kwargs)
        self.listen()


    def initialize(self, repi, *args, **kwargs):
        self.repi = repi
        self.channel = self.repi._prefixChannel(self.repi.info_channel)
        super(RepiConnection, self).initialize(*args, **kwargs)


    @tornado.gen.engine
    def listen(self):
        self.redis = tornadoredis.Client()
        self.redis.connect()
        channel = self.repi._prefixChannel(self.repi.info_channel)
        yield tornado.gen.Task(self.redis.subscribe, channel)
        self.redis.listen(self.on_redis_message)


    def on_websocket_message(self, json_message):
        # Decode JSON
        print 'type of message ', type(json_message), 'message:', json_message
        json_message = str(json_message)
        try:
            message = ujson.loads(json_message)
        except ValueError, err:
            print 'Invalid JSON.'
            return

        # Sanity check
        if not {'channel', 'command', 'data'}.issubset(message):
            print 'Invalid protocol.'
            return

        self.repi.publish(message['command'])#, data=message['data'], channel=message['channel'])

    on_message = on_websocket_message


    def on_redis_message(self, message):
        channel = message.channel
        print 'message from redis -->', message
        if message.kind == 'message':
            # Decode JSON
            json_message = str(message.body)
            try:
                message = ujson.loads(json_message)
            except ValueError, err:
                print 'Invalid JSON.'
                return

            # Sanity check
            if not {'client', 'command', 'data'}.issubset(message):
                print 'Invalid protocol.'
                return

            # Write to WebSocket
            self.write_message(json_message)
        elif message.kind == 'disconnect':
            self.close()
        else:
            print 'something other ...'
            # Write to WebSocket
            self.write_message(json_message)


    def on_close(self):
        if self.redis.subscribed:
            self.redis.unsubscribe('test_channel')
            self.redis.disconnect()

if __name__ == '__main__':
    r = tornadoredis.Client()
    repi_server = RepiServer(r)
    # repi_server.subscribe("my_channel")
    repi_server.run()