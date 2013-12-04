#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(_path)

def is_debug():
    return "debug" in sys.argv

# return abspath(wutong)/p
def path(p):
    return os.path.join(_path, p)
