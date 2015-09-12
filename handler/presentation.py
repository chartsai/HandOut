#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut presentation."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import BaseHandler
from ..db import FileList

# import re
# import os
# import uuid
# import shutil
# import subprocess
# import mimetypes
# from datetime import datetime


class QueryPresentHandler(BaseHandler):
    def get(self):
        self.write("<h1>List of Presentation!!</h1>")


class ViewPresentHandler(BaseHandler):
    def get(self):
        self.write("<h1>Presentation Detail!!</h1>")


class SubmitPresentHandler(BaseHandler):
    def get(self, present_id):
        self.write("<h1>Presentation Submit!!</h1>")

    def post(self, present_id):
        if present_id:
            raise self.HTTPError(404)
        if not self.request.files.get('file'):
            raise self.HTTPError(400)

        filename = self.request.files['file'][0]['filename']
        body = self.request.files['file'][0]['body']
        content_type = self.request.files['file'][0]['content_type']
