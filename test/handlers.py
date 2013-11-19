#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import path
import unittest
import requests

class TestHandlerBase(unittest.TestCase):

    def setup(self):
        do_something()

    def tearDown(self):
        pass

    def do_something()
        pass

def suite():
    suite = unittest.TestSuite()
    # TODO
    return suite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    main()
