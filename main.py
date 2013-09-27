from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from settings import settings, dsn
from momoko import Pool
from urls import urls
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)
define('debug', default=True, help='run in debug mode with autoreload (default: true)', type=bool)

if __name__ == "__main__":
    try:
        options.parse_command_line()
        settings['debug'] = options.debug
        application = Application(urls, **settings)
        application.db = Pool(dsn=dsn)
        http_server = HTTPServer(application)
        http_server.listen(options.port, 'localhost')
        IOLoop.instance().start()
    except KeyboardInterrupt as e:
        print(str(e))
