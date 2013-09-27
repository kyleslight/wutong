#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

_dbname = os.environ.get('WUTONG_DB', 'wutong')
_user = os.environ.get('WUTONG_USER', 'fz')
_password = os.environ.get('WUTONG_PASSWORD', 'fz')
_host = os.environ.get('WUTONG_HOST', 'localhost')
_port = os.environ.get('WUTONG_PORT', 5432)
dsn = 'dbname=%s user=%s password=%s host=%s port=%s' % (
    _dbname, _user, _password, _host, _port)

assert (_dbname or _user or _password or _host or _port) is not None, (
    'Environment variables for the examples are not set. Please set the following '
    'variables: WUTONG_DB, WUTONG_USER, WUTONG_PASSWORD, '
    'WUTONG_HOST, WUTONG_PORT')


settings = dict(
    sitename=u"梧桐",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=True,
    cookie_secret="k8+GFndWTsGzTXQBDzz4+reCX/K07E6hlh6cx3MJtow=",
    login_url="/login",
    autoescape=None,
)

