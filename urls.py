#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apps import edit

urls = [(r"/", edit.IndexHandler),
        (r"/show/(\d+)", edit.ShowHandler)]
