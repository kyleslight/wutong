#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import StringIO
from md5 import md5
try:
    from PIL import Image
except ImportError:
    import Image
from tornado.web import authenticated, asynchronous
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode, json_encode
from tornado import gen
from lib import util
from base import BaseHandler, catch_exception, authenticated


def genavatar(bindata, filepath, **kwargs):
    """
    resize image to 200x200 and return avatar url
    """
    fp = StringIO.StringIO(bindata)
    avatar = Image.open(fp)
    w, h = avatar.size
    x1 = kwargs.get('x1', 0)
    y1 = kwargs.get('y1', 0)
    x2 = kwargs.get('x2', w)
    y2 = kwargs.get('y2', h)

    avatar = avatar.crop((x1, y1, x2, y2))
    avatar_200x200 = avatar.resize((200, 200), Image.ANTIALIAS)
    avatar_200x200.save(filepath, "PNG")
    fp.close()
    return util.add_suffix(filepath, 'png')


class FileBaseHandler(BaseHandler):
    # 最大文件尺寸20Mb
    max_file_size = 20000000

    def get_save_path(self, filename, suffix=None):
        if suffix:
            filename = util.add_suffix(filename, suffix)
        return os.path.join(self.settings['upload_path'], filename)

    def is_file_exist(self, filename, suffix=None):
        if suffix:
            filename = util.add_suffix(filename, suffix)
        filename = self.get_save_path(filename)
        isfile = os.path.isfile(filename)
        return isfile


class UploadHandler(FileBaseHandler):
    @catch_exception
    def get(self):
        md5 = self.get_argument('md5')
        if not md5 or len(md5) != 32:
            raise Exception('error md5 value')
        isfile = self.is_file_exist(md5)
        self.write_result(isfile)

    @gen.coroutine
    def post(self):
        try:
            url = self.get_argument('url')
            if url:
                if not util.is_http_url(url):
                    raise Exception('invalid url')
                yield self.upload_from_url(url)
            else:
                self.upload_from_request(self.request)
        except Exception as e:
            self.write_errmsg(e)

    def upload_from_url(self, url):
        raise NotImplementedError

    @catch_exception
    @authenticated
    def upload_from_request(self, request, filetypes=None):
        filesize = int(request.headers['Content-Length'])
        if filesize > self.max_file_size:
            raise Exception('file size exceed')
        if not request.files:
            raise Exception('no upload file')

        upload_file = request.files['file'][0]
        data = upload_file['body']
        filename = upload_file['filename']
        suffix = util.get_suffix(filename)
        if not self.is_legal_filetype(suffix):
            raise Exception('invalid filetype')
        if filetypes and suffix not in filetypes:
            raise Exception('invalid file type')

        md5, filepath = self.save_data_as_file(data)
        res = self.get_file_info(md5=md5,
                                 filename=filename,
                                 suffix=suffix,
                                 filepath=filepath)
        self.write_json(res)

    def is_legal_filetype(self, suffix):
        return True

    def save_data_as_file(self, data, target=None):
        md5str = md5(data).hexdigest()
        filepath = target or self.get_save_path(md5str)
        with open(filepath, 'w') as fp:
            fp.write(data)
        return md5str, filepath

    def get_file_info(self, **kwargs):
        md5 = kwargs.get('md5')
        filename = kwargs.get('filename')
        res = {
            'md5': md5,
            'filename': filename,
            'url': '/file/download?md5=%s&filename=%s' % (md5, filename)
        }
        return res


class DownloadHandler(FileBaseHandler):
    @asynchronous
    @catch_exception
    def get(self):
        md5 = self.get_argument('md5')
        filename = self.get_argument('filename', md5)
        if not self.is_file_exist(md5):
            raise Exception('file not exist')

        self.set_header(u'Content-Disposition', 'attachment; filename=' + filename)
        filepath = self.get_save_path(md5)
        with open(filepath, "r") as fp:
            self.write(fp.read())
        self.finish()


class PictureHandler(UploadHandler):
    # 最大图片尺寸5Mb
    max_file_size = 5000000

    def get_file_info(self, **kwargs):
        md5 = kwargs.get('md5')
        filepath = kwargs.get('filepath')

        res = {
            'md5': md5,
            'url': util.get_path_url(filepath)
        }
        return res

    @gen.coroutine
    def upload_from_url(self, url):
        try:
            if not self.current_user:
                raise Exception('need login')
            client = AsyncHTTPClient()
            response = yield gen.Task(client.fetch, url)
            filesize = int(response.headers['Content-Length'])
            if filesize > self.max_file_size:
                raise Exception('file size exceed')
            data = response.body
            md5, filepath = self.save_data_as_file(data)
            res = self.get_file_info(md5=md5, filepath=filepath)
            self.write_json(res)
        except Exception as e:
            self.write_errmsg(e)

    def is_legal_filetype(self, suffix):
        return suffix.lower() in ('png', 'gif', 'jpg', 'jpeg')


class UserAvatarHandler(PictureHandler):
    # 最大图片尺寸500Kb
    max_file_size = 500000

    def save_data_as_file(self, data, target=None):
        filepath = os.path.join(self.settings['avatar_path'], self.current_user['nickname'])
        filepath = genavatar(data, filepath, x1=0, x2=0)
        md5str = md5(data).hexdigest()
        with open(filepath, 'w') as fp:
            fp.write(data)
        return md5str, filepath
