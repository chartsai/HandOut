#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut Base handlers."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from ..import version as system_version
from ..db import SQL_Session

import tornado.web
from tornado.escape import json_encode
from tornado.options import options


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def prepare(self):
        """This method is executed at the beginning of each request.

        """
        self.sql_session = SQL_Session()

    def on_finish(self):
        """Finish this response, ending the HTTP request 
        and properly close the database.
        """
        try:
            self.sql_session.close()
        except AttributeError:
            pass

    def get_current_user(self):
        """Gets the current user logged in from the cookies
        If a valid cookie is retrieved, return a User object.
        Otherwise, return None.
        """
        session_key = self.get_secure_cookie('session_key')
        if not session_key:
            return None
        login_session = Login_Session.get_by_key(session_key, self.sql_session)
        if not login_session:
            return None
        return User.by_key(login_session.userkey, self.sql_session).scalar()

    def get_template_namespace(self):
        _ = super(BaseHandler, self).get_template_namespace()

        # Call this to set the cookie
        self.xsrf_token

        return _

    @property
    def HTTPError(self):
        return tornado.web.HTTPError
    
    def write_error(self, error, **kargs):
        self.render('error.html', error=error)

    @staticmethod
    def authenticated(method):
        return tornado.web.authenticated(method)

    @staticmethod
    def check_is_admin_user(method):
        def wrapper(self, *args, **kwargs):
            if not self.current_user or not self.current_user.admin:
                raise self.HTTPError(403)
            return method(self, *args, **kwargs)
        return wrapper
