#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut Presentation handlers.

TODO: All.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .basehandler import BaseHandler

class SubmitPresentHandler(BaseHandler):
    def get(self,  *a, **kwargs):
        self.render('submitpresent.html')
