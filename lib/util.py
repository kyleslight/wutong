#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Last Modified time: 2014-02-23 20:54:58

import os
import re
import uuid
import time
import string
import random
from HTMLParser import HTMLParser
from hashlib import sha1
from datetime import datetime
from Crypto.Cipher import AES
from Crypto import Random
from tornado.web import create_signed_value, decode_signed_value


illegal_chars = set("""`~!@#$%^&*()+<>?:;'"[]{},./\\| \t\n\r""")
def has_illegal_char(s):
    if set(s).intersection(illegal_chars):
        return True
    return False

def is_bool(s):
    return s.lower() in ('0', '1', 't', 'f', 'true', 'false')

def get_bool(s):
    s = s.lower()
    if s in ('1', 't', 'true'):
        return True
    elif s in ('0', 'f', 'false'):
        return False
    return None

def is_english_or_chinese(s):
    if all(u'\u4e00' <= c <= u'\u9fff' for c in s):
        return True
    elif all(c.isspace() or c.isalpha() for c in s):
        return True
    return False

def is_email(email):
    pattern = re.compile(r'^[\.\w]{1,}[@]\w+[.]\w+$')
    if pattern.match(email):
        return True
    return False

def is_phone(phone):
    pattern = re.compile(r'^13\d{1}\d{8}$|15[0189]{1}\d{8}$|189\d{8}$')
    if pattern.match(phone):
        return True
    return False

def is_time(time):
    return True if str2time(time) else False

def is_http_url(url):
    return url.startswith('http://') or url.startswith('https://')

def is_picture(filename):
    return get_suffix(filename).lower() in ('png', 'gif', 'jpg', 'jpeg')

def get_abstract_str(s, length=10, suffix=u'...'):
    title = s[:length]
    if len(s) > length:
        title += suffix
    return title

def str2time(s):
    """
    convert `str` to `struct_time`
    """
    t = None
    try:
        t = time.strptime(s, "%Y-%m-%d")
    except ValueError:
        try:
            t = time.strptime(s, "%Y-%m-%d %H:%M:%S")
        except:
            pass
    return t

def split(txt, seps=u';；'):
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]

def html2text(html):
    class MLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.fed = []
        def handle_data(self, d):
            self.fed.append(d)
        def handle_entityref(self, name):
            self.fed.append('&%s;' % name)
        def get_data(self):
            return ''.join(self.fed)

    s = MLStripper()
    s.feed(html)
    return s.get_data()

def random_string(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def hexstring(salt, string):
    hexstr = sha1((salt + string).encode("utf-8"))
    hexstr = sha1(hexstr.hexdigest().encode("utf-8"))
    hexstr = str(hexstr.hexdigest())
    return hexstr

encrypt_url = None
def _secret_and_name():
    url = encrypt_url or "secret.wutong.com"
    secret = uuid.uuid5(uuid.NAMESPACE_URL, url).hex
    name = uuid.uuid3(uuid.NAMESPACE_URL, url).hex
    return secret, name

def encodestr(s):
    secret, name = _secret_and_name()
    return create_signed_value(secret, name, s)

def decodestr(encrpstr):
    secret, name = _secret_and_name()
    return decode_signed_value(secret, name, encrpstr)

def encrypt(s):
    key = bytes(random_string(16))
    iv = random_string(8).encode("hex")
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encrys = (key + cipher.encrypt(bytes(s)) + iv).encode("hex")
    return encrys

def decrypt(s):
    s = s.decode("hex")
    key = s[:16]
    iv = s[-16:]
    s = s[16:-16]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(s)

def str2datetime(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

def prettytime(dt):
    if isinstance(dt, basestring):
        dt = str2datetime(dt)
    dtdate = dt.date()
    now = datetime.now()
    nowdate = now.date()

    if nowdate == dtdate:
         return dt.strftime("%H:%M:%S")
    else:
         return dt.strftime("%Y-%m-%d %H:%M")

def get_path_url(path):
    path = os.path.abspath(path)
    wutong_dir = os.path.abspath(os.path.curdir)
    url = path.partition(wutong_dir)[-1]
    return url

def get_suffix(filename):
    return filename.rsplit('.', 1)[-1]

def add_suffix(basename, suffix):
    return basename + '.' + suffix
