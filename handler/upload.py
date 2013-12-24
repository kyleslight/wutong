#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from md5 import md5
from tornado.web import authenticated
from tornado.escape import json_decode, json_encode
from base import BaseHandler
from lib.util import prettytime


class FileHandler(BaseHandler):
    def init_content(self):
        # byte
        self.max_file_size = 20000000
        self.save_dir = os.path.join(self.settings['static_path'], 'uploads')

    def get_save_path(self, filename):
        return os.path.join(self.save_dir, filename)

    # download
    def get(self):
        self.render('test_upload_image.html')

    # upload
    def post(self):
        self.init_content()
        if not self.request.files:
            self.write('failed')
            return
        try:
            filesize = int(self.request.headers['Content-Length'])
            if filesize > self.max_file_size:
                self.write('exceed')
                return
            upload_file = self.request.files['file'][0]
            data = upload_file['body']
            filename = upload_file['filename']
            suffix = filename.rsplit('.', 1)[-1]
            filename = md5(data).hexdigest() + '.' + suffix
            save_path = self.get_save_path(filename)
            with open(save_path, 'w') as fp:
                fp.write(data)
        except:
            self.write('failed')
        else:
            self.write(filename)
