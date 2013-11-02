from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from settings import settings
from urls import urls


def main():
    application = Application(urls, **settings())
    http_server = HTTPServer(application)
    http_server.listen(settings("port"), settings("host"))
    IOLoop.instance().start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        pass
