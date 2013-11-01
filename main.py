from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from settings import get_settings
from urls import urls


def main():
    settings = get_settings()
    application = Application(urls, **settings)
    http_server = HTTPServer(application)
    http_server.listen(settings["port"], settings["localhost"])
    IOLoop.instance().start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        pass
