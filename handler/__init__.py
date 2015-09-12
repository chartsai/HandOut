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
from .submitpresenthandler import SubmitPresentHandler

route = [
    (r'/', IndexHandler),
    (r'/login/?', LoginHandler),
    (r'/logout/?', LogoutHandler),
    (r'/signup/?', SignupHandler),

    (r'/present/submit(?:/([0-9]+))?/?', SubmitPresentHandler),

    # Att and File
    (r'/file/(.*)', FileHandler, {"path": os.path.join(os.path.dirname(__file__), '../../file')})
]
