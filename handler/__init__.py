#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut-handler-init.

route.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .basehandler import BaseHandler

import os


class IndexHandler(BaseHandler):
    def get(self,  *a, **kwargs):
        self.render('index.html')


class NotFoundHandler(BaseHandler):
    def get(self,  *a, **kwargs):
        self.render('error.html', error='QAQ 404!')


from .userhandler import LoginHandler, LogoutHandler, SignupHandler
from .filehandler import FileHandler
from .presenthandler import QueryPresentHandler, ViewPresentHandler, SubmitPresentHandler
