#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut FileHandler handlers.

TODO: Fix bug.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .basehandler import BaseHandler
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
from tornado.web import StaticFileHandler


class FileHandler(StaticFileHandler, BaseHandler):
    @gen.coroutine
    def get(self, *arg, **kargs):
        yield super(FileHandler, self).get(*arg, **kargs)
