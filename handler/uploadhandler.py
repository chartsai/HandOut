#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut announce handlers.

FileHandler.

TODO: Fix bug.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import BaseHandler
from ..db import FileList

import re
import os
import uuid
import shutil
import subprocess
import mimetypes
from datetime import datetime

import tornado
from tornado import gen
from tornado.web import stream_request_body, StaticFileHandler


class StartPresentHandler(BaseHandler):
    def get(self,  *a, **kwargs):
        self.render('index.html')
