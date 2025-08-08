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

"""Tests for the middleware."""


import errno
import gc
import socket
import sys
import time
from doctest import ELLIPSIS
from textwrap import dedent

from oops import Config
from testtools import TestCase
from testtools.matchers import (
    DocTestMatches,
    Equals,
    MatchesException,
    MatchesListwise,
    Mismatch,
    raises,
)

from oops_wsgi import make_app
from oops_wsgi.middleware import construct_url, generator_tracker


class MismatchesOOPS(Mismatch):

    def __init__(self, mismatches):
        self.mismatches = mismatches

    def describe(self):
        descriptions = ["Differences: ["]
        for mismatch in self.mismatches:
            descriptions.append(mismatch.describe())
        descriptions.append("]")
        return "\n".join(descriptions)


class MatchesOOPS:
    """Matches an OOPS checking some keys and ignoring the rest."""

    def __init__(self, checkkeys=None):
        """Create a MatchesOOPS.

        :param checkkeys: A dict describing the keys to check. For each key in
        the dict the report must either have a matching key with the same value
        or a matching key whose value is matched by the matcher given.
        e.g. MatchesOOPS(
            dict(id=2, req_vars=MatchesSetwise(Equals(("foo", "bar")))))
        will check the id is 2, that req_vars is equivalent to [("foo", "bar")]
        and will ignore all other keys in the report.
        """
        self.checkkeys = checkkeys or {}

    def match(self, report):
        if type(report) is not dict:
            return Mismatch("Report is not a dict: '{}'".format(report))
        sentinel = object()
        mismatches = []
        for key, value in self.checkkeys.items():
            if key not in report:
                mismatches.append(Mismatch("Report has no key '%s'" % key))
            if getattr(value, "match", sentinel) is sentinel:
                matcher = Equals(value)
            else:
                matcher = value
            mismatch = matcher.match(report[key])
            if mismatch is not None:
                mismatches.append(mismatch)
        if mismatches:
            return MismatchesOOPS(mismatches)

    def __str__(self):
        return "MatchesOOPS(%s)" % self.checkkeys


class TestMakeApp(TestCase):

    def setUp(self):
        super().setUp()
        self.calls = []

    def make_outer_environ(self):
        environ = {}
        # Shove enough stuff in to let url reconstruction work:
        environ["wsgi.url_scheme"] = "http"
        environ["HTTP_HOST"] = "example.com"
        environ["PATH_INFO"] = "/demo"
        environ["QUERY_STRING"] = "param=value"
        return environ

    def make_inner_environ(self, context={}):
        environ = self.make_outer_environ()
        environ["oops.report"] = {}
        environ["oops.context"] = context
        return environ

    def wrap_and_run(
        self,
        inner,
        config,
        failing_write=False,
        failing_start=False,
        failing_server_write=False,
        params=None,
        environ_extra=None,
    ):
        if not params:
            params = {}
        app = make_app(inner, config, **params)
        environ = self.make_outer_environ()
        if environ_extra:
            environ.update(environ_extra)

        def start_response(status, headers, exc_info=None):
            if exc_info:
                # If an exception is raised after we have written (via the app
                # calling our oops_write) or after we have yielded data, we
                # must supply exc_info in the call to start_response, per the
                # wsgi spec. The easiest way to do that is to always supply
                # exc_info when reporting an exception - that will DTRT if
                # start_response upstream had already written data. Thus
                # our test start_response which lives above the oops middleware
                # captures the fact exc_info was called and all our tests that
                # expect oopses raised expect the exc_info to be present.
                self.calls.append(
                    ("start error", status, headers, exc_info[0], exc_info[1].args)
                )
                return self.calls.append
            if failing_start:
                raise OSError(errno.EPIPE, "Connection closed")
            self.calls.append((status, headers))
            if failing_write:

                def fail(bytes):
                    raise OSError(errno.EPIPE, "Connection closed")

                return fail
            else:
                return self.calls.append

        if not failing_server_write:
            return "".join(list(app(environ, start_response)))
        else:
            iterator = iter(app(environ, start_response))
            # get one item from it, which is enough to ensure we've activated
            # all the frames.
            step = next(iterator)
            # the client pipe is closed or something - we discard the iterator
            del iterator
            gc.collect()
            return step

    def test_make_app_returns_app(self):
        def inner(environ, start_response):
            start_response("200 OK", [("Content-Type", "text/html")])
            self.calls.append("inner")
            yield ""

        self.wrap_and_run(inner, Config())
        self.assertEqual(
            [
                # the start_reponse gets buffered.
                "inner",
                ("200 OK", [("Content-Type", "text/html")]),
            ],
            self.calls,
        )

    def test_empty_body(self):
        def inner(environ, start_response):
            start_response("200 OK", [("Content-Type", "text/html")])
            self.calls.append("inner")
            return []

        self.wrap_and_run(inner, Config())
        self.assertEqual(
            [
                # the start_reponse gets buffered in case the body production
                # fails.
                "inner",
                ("200 OK", [("Content-Type", "text/html")]),
            ],
            self.calls,
        )

    def test_unpublished_exception_raises(self):
        def inner(environ, start_response):
            raise ValueError("foo")
            yield ""

        self.assertThat(
            lambda: self.wrap_and_run(inner, Config()), raises(ValueError("foo"))
        )

    def test_filtered_exception_raises(self):
        def inner(environ, start_response):
            raise ValueError("foo")
            yield ""

        config = Config()
        config.filters.append(lambda report: True)
        self.assertThat(
            lambda: self.wrap_and_run(inner, Config()), raises(ValueError("foo"))
        )

    def publish_to_calls(self, report):
        self.calls.append(report)
        report["id"] = len(self.calls)
        return report["id"]

    def test_write_with_socket_exceptions_raise_no_oops(self):
        # When the wrapped app uses the 'write' function (which is
        # deprecated..., socket errors will raise within the oops middleware
        # but should be ignored.
        def inner(environ, start_response):
            write = start_response("200 OK", [("Content-Type", "text/html")])
            write("")

        config = Config()
        config.publishers.append(self.publish_to_calls)
        self.assertThat(
            lambda: self.wrap_and_run(inner, config, failing_write=True),
            raises(socket.error),
        )
        self.assertEqual(
            [
                ("200 OK", [("Content-Type", "text/html")]),
            ],
            self.calls,
        )

    def test_GeneratorExit_while_iterating_raise_no_oops(self):
        # if the wgsi server encounters a dropped socket, any iterators will be
        # interrupted with GeneratorExit, and this is normal - its not caught
        # or put into the OOPS system.
        def inner(environ, start_response):
            start_response("200 OK", [("Content-Type", "text/html")])
            while True:
                yield ""

        config = Config()
        config.publishers.append(self.publish_to_calls)
        self.assertEqual(
            "", self.wrap_and_run(inner, config, failing_server_write=True)
        )
        self.assertEqual(
            [
                ("200 OK", [("Content-Type", "text/html")]),
            ],
            self.calls,
        )

    def test_socket_error_from_start_response_raise_no_oops(self):
        def inner(environ, start_response):
            start_response("200 OK", [("Content-Type", "text/html")])
            yield ""

        config = Config()
        config.publishers.append(self.publish_to_calls)
        self.assertThat(
            lambda: self.wrap_and_run(inner, config, failing_start=True),
            raises(socket.error),
        )
        self.assertEqual([], self.calls)

    def test_start_response_not_called_if_fails_after_start_no_oops(self):
        # oops middle ware needs to buffer the start_response call in case the
        # wrapped app blows up before it starts streaming data - otherwise the
        # response cannot be replaced. If the exception is one that would not
        # oops (e.g. no publishers), start_response is never called.
        def inner(environ, start_response):
            start_response("200 OK", [("Content-Type", "text/html")])
            raise ValueError("boom, yo")
            yield ""

        config = Config()
        self.assertThat(
            lambda: self.wrap_and_run(
                inner,
                config,
            ),
            raises(ValueError("boom, yo")),
        )
        self.assertEqual([], self.calls)

    def config_for_oopsing(self, capture_create=False):
        config = Config()
        config.publishers.append(self.publish_to_calls)
        if capture_create:
            config.on_create.append(self.context_to_calls)
        return config

    def context_to_calls(self, report, context):
        self.calls.append(context)

    def test_oops_start_reponse_adds_x_oops_id_header(self):
        # When the oops middleware generates the error page itself, it includes
        # an x-oops-id header (vs adding one when we decorate a start_response
        # including exc_info from the wrapped app.
        def inner(environ, start_response):
            raise ValueError("booyah")

        config = self.config_for_oopsing()
        self.wrap_and_run(inner, config)
        headers = [("Content-Type", "text/html"), ("X-Oops-Id", "1")]
        expected_start_response = (
            "start error",
            "500 Internal Server Error",
            headers,
            ValueError,
            ("booyah",),
        )
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # The oops is logged:
                    MatchesOOPS({"value": "booyah"}),
                    # And the containing start_response was called with our custom
                    # headers.
                    Equals(expected_start_response),
                ]
            ),
        )

    def test_start_response_500_if_fails_after_start_before_body(self):
        # oops middle ware needs to buffer the start_response call in case the
        # wrapped app blows up before it starts streaming data - otherwise the
        # response cannot be replaced. If the exception is one that would
        # oops start_response is only called with 500.
        def inner(environ, start_response):
            start_response("200 OK", [("Content-Type", "text/html")])
            raise ValueError("boom, yo")
            yield ""

        config = self.config_for_oopsing()
        iterated = self.wrap_and_run(inner, config)
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # First the oops is generated
                    MatchesOOPS({"value": "boom, yo"}),
                    # Then the middleware responses
                    Equals(
                        (
                            "start error",
                            "500 Internal Server Error",
                            [("Content-Type", "text/html"), ("X-Oops-Id", "1")],
                            ValueError,
                            ("boom, yo",),
                        )
                    ),
                ]
            ),
        )
        self.assertThat(
            iterated,
            DocTestMatches(
                dedent(
                    """\
            <html>
            <head><title>Oops! - ...</title></head>
            <body>
            <h1>Oops!</h1>
            <p>Something broke while generating the page.
            Please try again in a few minutes, and if the problem persists file
            a bug or contact customer support. Please quote OOPS-ID
            <strong>...</strong>
            </p></body></html>
            """
                ),
                ELLIPSIS,
            ),
        )

    def test_custom_template_content_type(self):
        def inner(environ, start_response):
            raise ValueError("boom, yo")

        config = self.config_for_oopsing()
        iterated = self.wrap_and_run(
            inner,
            config,
            params=dict(content_type="text/json", template='{"oopsid" : "%(id)s"}'),
        )
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # First the oops is generated
                    MatchesOOPS({"value": "boom, yo"}),
                    # Then the middleware responses
                    Equals(
                        (
                            "start error",
                            "500 Internal Server Error",
                            [("Content-Type", "text/json"), ("X-Oops-Id", "1")],
                            ValueError,
                            ("boom, yo",),
                        )
                    ),
                ]
            ),
        )
        self.assertThat(
            iterated,
            DocTestMatches(
                dedent(
                    """\
            {"oopsid" : "..."}"""
                ),
                ELLIPSIS,
            ),
        )

    def test_custom_renderer(self):
        def inner(environ, start_response):
            raise ValueError("boom, yo")

        config = self.config_for_oopsing()

        def error_render(report):
            return "woo"

        iterated = self.wrap_and_run(
            inner, config, params=dict(error_render=error_render)
        )
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # First the oops is generated
                    MatchesOOPS({"value": "boom, yo"}),
                    # Then the middleware responses
                    Equals(
                        (
                            "start error",
                            "500 Internal Server Error",
                            [("Content-Type", "text/html"), ("X-Oops-Id", "1")],
                            ValueError,
                            ("boom, yo",),
                        )
                    ),
                ]
            ),
        )
        self.assertEqual(iterated, "woo")

    def test_oops_url_in_context(self):
        def inner(environ, start_response):
            raise ValueError("boom, yo")

        config = self.config_for_oopsing()
        self.wrap_and_run(inner, config)
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # First the oops is generated - with a url.
                    MatchesOOPS({"url": "http://example.com/demo?param=value"}),
                    # Then the middleware responses
                    Equals(
                        (
                            "start error",
                            "500 Internal Server Error",
                            [("Content-Type", "text/html"), ("X-Oops-Id", "1")],
                            ValueError,
                            ("boom, yo",),
                        )
                    ),
                ]
            ),
        )

    def test_timeline_dot_timeline_in_context(self):
        # By default if the environ has a timeline.timeline when raising, it is
        # copied to the context - this permits the oops-timeline hooks to find
        # it.
        def inner(environ, start_response):
            raise ValueError("boom, yo")

        config = self.config_for_oopsing(capture_create=True)
        timeline = object()
        self.wrap_and_run(inner, config, environ_extra={"timeline.timeline": timeline})
        self.assertEqual(timeline, self.calls[0]["timeline"])

    def test_arbitrary_mapping_in_context(self):
        def inner(environ, start_response):
            raise ValueError("boom, yo")

        config = self.config_for_oopsing(capture_create=True)
        thing = object()
        self.wrap_and_run(
            inner,
            config,
            environ_extra={"foo": thing},
            params=dict(map_environ=dict(foo="bar")),
        )
        self.assertEqual(thing, self.calls[0]["bar"])

    def test_error_in_app_context_sets_oops_context(self):
        # When the app blows up we attach the environment and the oops.context
        # wsgi variable injects straight into the context.
        def inner(environ, start_response):
            environ["oops.context"]["foo"] = "bar"
            raise ValueError("boom, yo")

        config = self.config_for_oopsing(capture_create=True)
        self.wrap_and_run(inner, config)
        self.assertEqual(
            self.make_inner_environ({"foo": "bar"}), self.calls[0]["wsgi_environ"]
        )
        self.assertEqual("bar", self.calls[0]["foo"])

    def test_start_response_with_just_exc_info_generates_oops(self):
        def inner(environ, start_response):
            try:
                raise ValueError("boom, yo")
            except ValueError:
                exc_info = sys.exc_info()
            try:
                start_response("500 FAIL", [("content-type", "text/plain")], exc_info)
            finally:
                del exc_info
            yield "body"

        config = self.config_for_oopsing()
        contents = self.wrap_and_run(inner, config)
        # The body from the wrapped app is preserved.
        self.assertEqual("body", contents)
        # The header though have an X-Oops-Id header added:
        headers = [("content-type", "text/plain"), ("X-Oops-Id", "1")]
        expected_start_response = (
            "start error",
            "500 FAIL",
            headers,
            ValueError,
            ("boom, yo",),
        )
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # The oops is logged:
                    MatchesOOPS({"value": "boom, yo"}),
                    # And we have forwarded on the wrapped apps start_response call.
                    Equals(expected_start_response),
                ]
            ),
        )

    def test_start_response_exc_info_includes_environ_and_context(self):
        # When the app handles its own error we still attach the environment
        # and the wsgi.context wsgi variable.
        def inner(environ, start_response):
            # Set a custom variable for the context
            environ["oops.context"]["foo"] = "bar"
            try:
                raise ValueError("boom, yo")
            except ValueError:
                exc_info = sys.exc_info()
            try:
                start_response("500 FAIL", [("content-type", "text/plain")], exc_info)
            finally:
                del exc_info
            yield "body"

        config = self.config_for_oopsing(capture_create=True)
        self.wrap_and_run(inner, config)
        self.assertEqual(
            self.make_inner_environ({"foo": "bar"}), self.calls[0]["wsgi_environ"]
        )
        self.assertEqual("bar", self.calls[0]["foo"])

    def test_sniff_404_not_published_does_not_error(self):
        # If the OOPS is not published, the start_response just passes through
        # as though we were not sniffing responses.
        def inner(environ, start_response):
            start_response("404 MISSING", [])
            yield "pretty 404"

        contents = self.wrap_and_run(
            inner, Config(), params=dict(oops_on_status=["404"])
        )
        self.assertEqual("pretty 404", contents)
        expected_start_response = ("404 MISSING", [])
        self.assertEqual([expected_start_response], self.calls)

    def test_sniff_404_published_does_not_error(self):
        # Sniffing of unexpected pages to gather oops data doesn't alter the
        # wrapped apps page. It also does not add an X-OOPS-ID header because
        # client side scripts often look for that to signal errors.
        def inner(environ, start_response):
            start_response("404 MISSING", [])
            yield "pretty 404"

        config = self.config_for_oopsing()
        contents = self.wrap_and_run(inner, config, params=dict(oops_on_status=["404"]))
        self.assertEqual("pretty 404", contents)
        expected_start_response = ("404 MISSING", [])
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # An OOPS is logged with the observed response code.
                    MatchesOOPS({"HTTP_STATUS": "404"}),
                    Equals(expected_start_response),
                ]
            ),
        )

    def test_sniff_oops_context_includes_wsgi_environ_and_context(self):
        def inner(environ, start_response):
            environ["oops.context"]["foo"] = "bar"
            start_response("404 MISSING", [])
            yield "pretty 404"

        config = self.config_for_oopsing(capture_create=True)
        self.wrap_and_run(inner, config, params=dict(oops_on_status=["404"]))
        self.assertEqual(
            self.make_inner_environ({"foo": "bar"}), self.calls[0]["wsgi_environ"]
        )
        self.assertEqual("bar", self.calls[0]["foo"])

    def test_inner_environ_has_oops_report_and_oops_context_variables(self):
        def inner(environ, start_response):
            self.assertEqual({}, environ["oops.report"])
            self.assertEqual({}, environ["oops.context"])
            start_response("200 OK", [])
            yield "success"

        config = self.config_for_oopsing()
        body = self.wrap_and_run(inner, config)
        self.assertEqual("success", body)

    def test_custom_tracker(self):
        def myapp(environ, start_response):
            start_response("200 OK", [])
            yield "success"

        def mytracker(on_first_bytes, on_finish, on_error, body):
            return "tracker"

        app = make_app(myapp, Config(), tracker=mytracker)
        self.assertEqual("tracker", app({}, lambda status, headers: None))

    def test_soft_start_timeout_below_threshold(self):
        # When a request responds below the timeout, no OOPS is made.
        def myapp(environ, start_response):
            start_response("200 OK", [])
            yield "success"

        config = self.config_for_oopsing()
        body = self.wrap_and_run(myapp, config, params=dict(soft_start_timeout=1000))
        self.assertEqual("success", body)
        expected_start_response = ("200 OK", [])
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    Equals(expected_start_response),
                ]
            ),
        )

    def test_soft_start_timeout_above_threshold(self):
        # When a request responds above the timeout, an OOPS is made with a
        # SoftTimeout exception and backtrace.
        def myapp(environ, start_response):
            time.sleep(0.002)
            start_response("200 OK", [])
            yield "success"

        config = self.config_for_oopsing()
        body = self.wrap_and_run(myapp, config, params=dict(soft_start_timeout=1))
        self.assertEqual("success", body)
        expected_start_response = ("200 OK", [])
        self.assertThat(
            self.calls,
            MatchesListwise(
                [
                    # An OOPS is logged with the observed response code.
                    MatchesOOPS({"type": "SoftRequestTimeout"}),
                    Equals(expected_start_response),
                ]
            ),
        )

    def test_calls_start_response_with_positional_exc_info(self):
        def myapp(environ, start_response):
            raise ValueError("boom, yo")

        config = self.config_for_oopsing(capture_create=True)
        app = make_app(myapp, config)
        environ = self.make_outer_environ()

        def start_response(*args, **kwargs):
            if kwargs:
                raise AssertionError("start_response takes no kwargs: %s" % str(kwargs))
            return self.calls.append

        list(app(environ, start_response))
        self.assertEqual(2, len(self.calls))
        self.assertThat(
            self.calls[0]["exc_info"], MatchesException(ValueError("boom, yo"))
        )
        self.assertThat(self.calls[1], MatchesOOPS({"value": "boom, yo"}))


class TestGeneratorTracker(TestCase):

    def setUp(self):
        super().setUp()
        self.calls = []

    def on_first_bytes(self):
        self.calls.append("on_first_bytes")

    def on_finish(self):
        self.calls.append("on_finish")

    def on_exception_ok(self, exc_info):
        self.calls.append("on exception {}".format(exc_info[1]))
        return "error page"

    def on_exception_fail(self, exc_info):
        self.calls.append("on exception {}".format(exc_info[1]))
        raise ValueError("fail")

    def test_constructor(self):
        generator_tracker(None, None, None, [])

    def test_call_order_empty(self):
        tracker = generator_tracker(self.on_first_bytes, self.on_finish, None, [])
        self.assertEqual([], list(tracker))
        self.assertEqual(["on_finish"], self.calls)

    def test_call_order_one_item(self):
        tracker = generator_tracker(self.on_first_bytes, self.on_finish, None, ["foo"])
        for result in tracker:
            self.calls.append(result)
        self.assertEqual(["on_first_bytes", "foo", "on_finish"], self.calls)

    def test_call_order_two_items(self):
        def on_first_bytes():
            self.calls.append("on_first_bytes")

        tracker = generator_tracker(
            self.on_first_bytes, self.on_finish, None, ["foo", "bar"]
        )
        for result in tracker:
            self.calls.append(result)
        self.assertEqual(["on_first_bytes", "foo", "bar", "on_finish"], self.calls)

    def test_on_exception_iter(self):
        def failing_iter():
            raise ValueError("foo")
            yield ""

        tracker = generator_tracker(
            self.on_first_bytes, self.on_finish, self.on_exception_ok, failing_iter()
        )
        for result in tracker:
            self.calls.append(result)
        self.assertEqual(["on exception foo", "error page"], self.calls)

    def test_on_exception_exceptions_propogate(self):
        def failing_iter():
            raise ValueError("foo")
            yield ""

        tracker = generator_tracker(
            self.on_first_bytes, self.on_finish, self.on_exception_fail, failing_iter()
        )
        self.assertThat(lambda: next(tracker), raises(ValueError("fail")))
        self.assertEqual(["on exception foo"], self.calls)

    def test_closes_iterator(self):
        class mock_iterator(list):
            def close(self):
                self.close_called = True

        mock_app_body = mock_iterator()
        tracker = generator_tracker(
            self.on_first_bytes, self.on_finish, None, mock_app_body
        )
        for result in tracker:
            pass
        self.assertTrue(mock_app_body.close_called)


class TestConstructURL(TestCase):

    def test_with_normal_string(self):
        result = construct_url(
            {
                "HTTP_HOST": "localhost:8000",
                "wsgi.url_scheme": "http",
                "PATH_INFO": "/test/foo",
            }
        )
        self.assertEqual("http://localhost:8000/test/foo", result)

    def test_with_unicode_string(self):
        result = construct_url(
            {
                "HTTP_HOST": "localhost:8000",
                "wsgi.url_scheme": "http",
                "PATH_INFO": "/test/\xf9/",
            }
        )
        self.assertEqual("http://localhost:8000/test/%C3%B9/", result)
