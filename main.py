#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from settings import settings
from urls import urls
from model.db import Pool

def main():
    application = Application(urls, **settings)
    application.db = Pool.instance(settings["dsn"])
    http_server = HTTPServer(application)
    http_server.listen(settings["port"], settings["host"])
    IOLoop.instance().start()

def debug():

    class RouteHandler(RequestHandler):
        def get(self, filename="group.html"):
            self.render(filename, messages=[])

    urls.append((r"/(.*)", RouteHandler))
    main()

def is_debug():
    return settings["debug"]

if __name__ == "__main__":
    try:
        if is_debug():
            debug()
        else:
            main()
    except KeyboardInterrupt as e:
        pass
