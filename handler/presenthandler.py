#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut presentation."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import BaseHandler
from ..db import Presentation, FileList

# import re
import os
import uuid
import shutil
# import subprocess
# import mimetypes
# from datetime import datetime


class QueryPresentHandler(BaseHandler):
    def get(self):
        self.write("<h1>List of Presentation!!</h1>")


class ViewPresentHandler(BaseHandler):
    def get(self, present_id):
        present = Presentation.by_p_key(present_id, self.sql_session).scalar()
        present_file = FileList.by_present_id(present_id, self.sql_session).scalar()
        self.render('viewpresent.html',
                        title = present.title,
                        owner = present.owner,
                        file_path = '/download/%s/%s' % (present_file.key, present_file.filename))


class SubmitPresentHandler(BaseHandler):
    def initialize(self):
        super(SubmitPresentHandler, self).initialize()
        self.file_folder = os.path.join(os.path.dirname(__file__), '../file')
        if not os.path.exists(self.file_folder):
            os.makedirs(self.file_folder)

    def prepare(self):
        super(SubmitPresentHandler, self).prepare()
        self.kw = {
            'present_id': '',
            'title': '',
            'owner': '',
            'lat': 0.0,
            'lng': 0.0,
            'presentation': {},
        }

    def get(self, present_id):
        if present_id:
            old_present = Presentation.by_p_key(present_id, self.sql_session).scalar()
            if not old_present:
                raise self.HTTPError(404)
            self.kw['present_id'] = present_id
            self.kw['title'] = old_present.title
            self.kw['owner'] = old_present.owner
            self.kw['lat'] = old_present.lat
            self.kw['lng'] = old_present.lng

        self.render('submitpresent.html', **self.kw)

    def post(self, present_id):
        self.kw['title'] = self.get_argument('title', 'Whatever')
        self.kw['owner'] = self.get_argument('owner', 'Whoever')
        self.kw['lat'] = self.get_argument('lat', 0.0)
        self.kw['lng'] = self.get_argument('lng', 0.0)
        if self.request.files.get('presentation'):
            self.kw['presentation'] = self.request.files['presentation'][0]

        if present_id:
            # Old presentation
            q = Presentation.by_p_key(present_id, self.sql_session)
            old_present = q.scalar()
            if not old_present:
                raise self.HTTPError(404)

            q.update({
                    'title': self.kw['title'],
                    'owner': self.kw['owner'],
                    'lat': self.kw['lat'],
                    'lng': self.kw['lng']
                })
            # Old presentation doesn't request ppt file
            # Delete old ppt file
            if self.kw.get('presentation'):
                q = FileList.by_present_id(present_id, self.sql_session)
                old_file = q.scalar()
                shutil.rmtree(os.path.join(self.file_folder, old_file.key))
                FileList.by_present_id(present_id, self.sql_session).delete()
        else:
            # New presentation
            # New presentation requests ppt file
            if not self.kw.get('presentation'):
                raise self.HTTPError(400)

            new_present = Presentation(**self.kw)
            self.sql_session.add(new_present)
            self.sql_session.flush()
            self.sql_session.refresh(new_present)
            present_id = new_present.p_key

        # Add new ppt file
        if self.kw.get('presentation'):
            self.kw['presentation']['key'] = uuid.uuid1().hex
            # TODO : get file_type
            self.kw['presentation']['file_type'] = 'pptx'
            self.kw['presentation']['present_id'] = present_id

            new_file = FileList(**self.kw['presentation'])
            file_hash_folder = os.path.join(self.file_folder, new_file.key)
            if os.path.exists(file_hash_folder):
                raise self.HTTPError(500)
            os.makedirs(file_hash_folder)
            with open(os.path.join(file_hash_folder, new_file.filename), 'wb') as f:
                f.write(self.kw['presentation']['body'])
            self.sql_session.add(new_file)

        self.sql_session.commit()
        self.redirect('/present/%s' % present_id)
