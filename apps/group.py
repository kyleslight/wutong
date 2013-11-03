from tornado.web import authenticated
from tornado.websocket import WebSocketHandler
from tornado.escape import to_basestring
from base import BaseHandler

class IndexHandler(BaseHandler):

    def get(self, id=None):
        # message[] = to_basestring(self.render_string("message.html", messages=messages))
        self.render("group.html", messages=[])

    @authenticated
    def post(self, id):
        pass

class MessageHandler(BaseHandler, WebSocketHandler):
    waiters = dict()

    def open(self, id):
        logging.info(id)
        self.waiters.add(self)

    def on_close(self):
        logging.info("on_close")
        self.waiters.remove(self)

    def on_message(self, message):
        logging.info("on_message")
        Mydb.insert(message)
        for waiter in self.waiters:
            waiter.write_message(message)


