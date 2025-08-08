# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""Tests for the various hooks included in oops-wsgi."""


from io import BytesIO

from oops import Config
from testtools import TestCase
from testtools.matchers import LessThan

from oops_wsgi import install_hooks
from oops_wsgi.hooks import copy_environ, hide_cookie, update_report


class TestInstallHooks(TestCase):

    def test_install_hooks_installs_defaults(self):
        config = Config()
        install_hooks(config)
        self.assertIn(hide_cookie, config.on_create)
        self.assertIn(copy_environ, config.on_create)
        self.assertThat(
            config.on_create.index(copy_environ),
            LessThan(config.on_create.index(hide_cookie)),
        )
        # update report wants to be at the start - its closer to a template
        # than anything.
        self.assertEqual(config.on_create[0], update_report)


class TestHooks(TestCase):

    def test_hide_cookie_no_cookie(self):
        report = {}
        hide_cookie(report, {})
        self.assertEqual({}, report)

    def test_hide_cookie_cookie_present_top_level(self):
        report = {"HTTP_COOKIE": "foo"}
        hide_cookie(report, {})
        self.assertEqual({"HTTP_COOKIE": "<hidden>"}, report)

    def test_hide_cookie_cookie_present_req_vars(self):
        report = {"req_vars": {"HTTP_COOKIE": "foo"}}
        hide_cookie(report, {})
        self.assertEqual({"req_vars": {"HTTP_COOKIE": "<hidden>"}}, report)

    def test_hide_cookie_authorization_present_top_level(self):
        report = {"HTTP_AUTHORIZATION": "Macaroon root=foo, discharge=bar"}
        hide_cookie(report, {})
        self.assertEqual({"HTTP_AUTHORIZATION": "Macaroon <hidden>"}, report)

    def test_hide_cookie_authorization_present_req_vars(self):
        report = {
            "req_vars": {
                "HTTP_AUTHORIZATION": "Macaroon root=foo, discharge=bar",
            },
        }
        hide_cookie(report, {})
        self.assertEqual(
            {"req_vars": {"HTTP_AUTHORIZATION": "Macaroon <hidden>"}}, report
        )

    def test_copy_environ_copied_variables(self):
        environ = {
            "REQUEST_METHOD": "GET",
            "SCRIPT_NAME": "",
            "PATH_INFO": "/foo",
            "QUERY_STRING": "bar=quux",
            "CONTENT_TYPE": "multipart/x-form-encoding",
            "CONTENT_LENGTH": "12",
            "SERVER_NAME": "example.com",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.0",
            "HTTP_COOKIE": "zaphod",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "https",
            "wsgi.input": BytesIO(),
        }
        context = dict(wsgi_environ=environ)
        report = {}
        copy_environ(report, context)
        expected_vars = {
            "REQUEST_METHOD": "GET",
            "SCRIPT_NAME": "",
            "PATH_INFO": "/foo",
            "QUERY_STRING": "bar=quux",
            "CONTENT_TYPE": "multipart/x-form-encoding",
            "CONTENT_LENGTH": "12",
            "SERVER_NAME": "example.com",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.0",
            "HTTP_COOKIE": "zaphod",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "https",
        }
        expected_report = {"req_vars": expected_vars}
        self.assertEqual(expected_report, report)

    def test_update_report_no_wsgi_report(self):
        report = {}
        update_report(report, {})
        update_report(report, {"wsgi_environ": {}})
        self.assertEqual({}, report)

    def test_update_report_copies_wsgi_report_variables(self):
        report = {}
        update_report(report, {"wsgi_environ": {"oops.report": {"foo": "bar"}}})
        self.assertEqual({"foo": "bar"}, report)
