#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import psycopg2
import tornado.web
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.httpserver
settings = dict(
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    debug=True,
    xsrf_cookies=False,
    autoescape=None,
    login_url="/login",
    cookie_secret="k8+GFndWTsGzTXQBDzz4+reCX/K07E6hlh6cx3MJtow=",
)

_dbname = 'wutong_test'
_dbuser = 'postgres'
_dbpassword = '135450218989'
_dbhost = 'localhost'
_dbport = '5432'
_dsn = 'dbname=%s user=%s password=%s host=%s port=%s' % \
      (_dbname, _dbuser, _dbpassword, _dbhost, _dbport)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('group.html')

class TestHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        if not hasattr(self.application, 'db'):
            self.application.db = psycopg2.connect(dsn=_dsn)
        return self.application.db

    def get(self):
        topic_id = self.get_argument('topic_id', '0')
        cursor = self.db.cursor()
        cursor.execute('select * from test where id > %s limit 30', (topic_id, ))
        self.db.commit()
        results = cursor.fetchall()

        if not results:
            self.write('')
            return

        entrys = []
        for result in results:
            entrys.append(dict(id=str(result[0]),
                               ip=str(result[1]),
                               submit_time=str(result[2]),
                               content=str(result[3])))

        self.write(tornado.escape.json_encode(entrys))

    def post(self):
        ip = self.request.remote_ip
        content = self.get_argument('content', '')
        if not content:
            self.write('no content')
            return
        cursor = self.db.cursor()
        cursor.execute('insert into test (ip, content) values (%s, %s);', (ip, content,))
        self.db.commit()

urls = [(r"/", IndexHandler), (r"/test", TestHandler)]
host = '10.12.69.137'
port = '8888'

if __name__ == "__main__":
    try:
        tornado.options.parse_command_line()
        application = tornado.web.Application(urls, **settings)
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(port, host)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt as e:
        print(str(e))
