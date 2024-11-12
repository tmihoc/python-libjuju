# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
Tests for the gocookies code.
"""

import os
import shutil
import tempfile
import unittest
import urllib.request

import pyrfc3339
from juju.client.gocookies import GoCookieJar

# cookie_content holds the JSON contents of a Go-produced
# cookie file (reformatted so it's not all on one line but
# otherwise unchanged).
cookie_content = """
[
    {
        "CanonicalHost": "bar.com",
        "Creation": "2017-11-17T08:53:55.088820092Z",
        "Domain": "bar.com",
        "Expires": "2345-11-15T18:16:08Z",
        "HostOnly": true,
        "HttpOnly": false,
        "LastAccess": "2017-11-17T08:53:55.088822562Z",
        "Name": "bar",
        "Path": "/",
        "Persistent": true,
        "Secure": false,
        "Updated": "2017-11-17T08:53:55.088822562Z",
        "Value": "bar-value"
    },
    {
        "CanonicalHost": "x.foo.com",
        "Creation": "2017-11-17T08:53:55.088814857Z",
        "Domain": "x.foo.com",
        "Expires": "2345-11-15T18:16:05Z",
        "HostOnly": true,
        "HttpOnly": false,
        "LastAccess": "2017-11-17T08:53:55.088884015Z",
        "Name": "foo",
        "Path": "/path",
        "Persistent": true,
        "Secure": false,
        "Updated": "2017-11-17T08:53:55.088814857Z",
        "Value": "foo-path-value"
    },
    {
        "CanonicalHost": "x.foo.com",
        "Creation": "2017-11-17T08:53:55.088814857Z",
        "Domain": "foo.com",
        "Expires": "2345-11-15T18:16:06Z",
        "HostOnly": false,
        "HttpOnly": false,
        "LastAccess": "2017-11-17T08:53:55.088919437Z",
        "Name": "foo4",
        "Path": "/path",
        "Persistent": true,
        "Secure": false,
        "Updated": "2017-11-17T08:53:55.088814857Z",
        "Value": "foo4-value"
    },
    {
        "CanonicalHost": "x.foo.com",
        "Creation": "2017-11-17T08:53:55.088790709Z",
        "Domain": "x.foo.com",
        "Expires": "2345-11-15T18:16:01Z",
        "HostOnly": true,
        "HttpOnly": false,
        "LastAccess": "2017-11-17T08:53:55.088884015Z",
        "Name": "foo",
        "Path": "/",
        "Persistent": true,
        "Secure": false,
        "Updated": "2017-11-17T08:53:55.088790709Z",
        "Value": "foo-value"
    },
    {
        "CanonicalHost": "x.foo.com",
        "Creation": "2017-11-17T08:53:55.088790709Z",
        "Domain": "foo.com",
        "Expires": "2345-11-15T18:16:02Z",
        "HostOnly": false,
        "HttpOnly": false,
        "LastAccess": "2017-11-17T08:53:55.088919437Z",
        "Name": "foo1",
        "Path": "/",
        "Persistent": true,
        "Secure": false,
        "Updated": "2017-11-17T08:53:55.088790709Z",
        "Value": "foo1-value"
    },
    {
        "CanonicalHost": "x.foo.com",
        "Creation": "2017-11-17T08:53:55.088790709Z",
        "Domain": "x.foo.com",
        "Expires": "2345-11-15T18:16:03Z",
        "HostOnly": true,
        "HttpOnly": false,
        "LastAccess": "2017-11-17T08:53:55.088850252Z",
        "Name": "foo2",
        "Path": "/",
        "Persistent": true,
        "Secure": true,
        "Updated": "2017-11-17T08:53:55.088790709Z",
        "Value": "foo2-value"
    },
    {
        "CanonicalHost": "x.foo.com",
        "Creation": "2017-11-17T08:53:55.088790709Z",
        "Domain": "foo.com",
        "Expires": "2345-11-15T18:16:04Z",
        "HostOnly": false,
        "HttpOnly": false,
        "LastAccess": "2017-11-17T08:53:55.088919437Z",
        "Name": "foo3",
        "Path": "/",
        "Persistent": true,
        "Secure": false,
        "Updated": "2017-11-17T08:53:55.088790709Z",
        "Value": "foo3-value"
    }
]
"""

# cookie_content_queries holds a set of queries
# that were automatically generated by running
# the queries on the above cookie_content data
# and printing the results.
cookie_content_queries = [
    (
        "http://x.foo.com",
        [
            ("foo", "foo-value"),
            ("foo1", "foo1-value"),
            ("foo3", "foo3-value"),
        ],
    ),
    (
        "https://x.foo.com",
        [
            ("foo", "foo-value"),
            ("foo1", "foo1-value"),
            ("foo2", "foo2-value"),
            ("foo3", "foo3-value"),
        ],
    ),
    (
        "http://arble.foo.com",
        [
            ("foo1", "foo1-value"),
            ("foo3", "foo3-value"),
        ],
    ),
    ("http://arble.com", []),
    (
        "http://x.foo.com/path/x",
        [
            ("foo", "foo-path-value"),
            ("foo4", "foo4-value"),
            ("foo", "foo-value"),
            ("foo1", "foo1-value"),
            ("foo3", "foo3-value"),
        ],
    ),
    (
        "http://arble.foo.com/path/x",
        [
            ("foo4", "foo4-value"),
            ("foo1", "foo1-value"),
            ("foo3", "foo3-value"),
        ],
    ),
    (
        "http://foo.com/path/x",
        [
            ("foo4", "foo4-value"),
            ("foo1", "foo1-value"),
            ("foo3", "foo3-value"),
        ],
    ),
]


class TestGoCookieJar(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_readcookies(self):
        jar = self.load_jar(cookie_content)
        self.assert_jar_queries(jar, cookie_content_queries)

    def test_roundtrip(self):
        jar = self.load_jar(cookie_content)
        filename2 = os.path.join(self.dir, "cookies2")
        jar.save(filename=filename2)
        jar = GoCookieJar()
        jar.load(filename=filename2)
        self.assert_jar_queries(jar, cookie_content_queries)

    def test_expiry_time(self):
        content = """[
            {
                "CanonicalHost": "bar.com",
                "Creation": "2017-11-17T08:53:55.088820092Z",
                "Domain": "bar.com",
                "Expires": "2345-11-15T18:16:08Z",
                "HostOnly": true,
                "HttpOnly": false,
                "LastAccess": "2017-11-17T08:53:55.088822562Z",
                "Name": "bar",
                "Path": "/",
                "Persistent": true,
                "Secure": false,
                "Updated": "2017-11-17T08:53:55.088822562Z",
                "Value": "bar-value"
            }
        ]"""
        jar = self.load_jar(content)
        got_expires = tuple(jar)[0].expires
        want_expires = int(pyrfc3339.parse("2345-11-15T18:16:08Z").timestamp())
        self.assertEqual(got_expires, want_expires)

    def load_jar(self, content):
        filename = os.path.join(self.dir, "cookies")
        with open(filename, "x") as f:
            f.write(content)
        jar = GoCookieJar()
        jar.load(filename=filename)
        return jar

    def assert_jar_queries(self, jar, queries):
        """Assert that all the given queries (see cookie_content_queries)
        are satisfied when run on the given cookie jar.
        :param jar CookieJar: the cookie jar to query
        :param queries: the queries to run.
        """
        for url, want_cookies in queries:
            req = urllib.request.Request(url)
            jar.add_cookie_header(req)
            # We can't use SimpleCookie to find out what cookies
            # have been presented, because SimpleCookie
            # only allows one cookie with a given name,
            # so we naively parse the cookies ourselves, which
            # is OK because we know we don't have to deal
            # with any complex cases.

            cookie_header = req.get_header("Cookie")
            got_cookies = []
            if cookie_header is not None:
                got_cookies = [
                    tuple(part.split("=")) for part in cookie_header.split("; ")
                ]
                got_cookies.sort()
            want_cookies = list(want_cookies)
            want_cookies.sort()
            self.assertEqual(
                got_cookies,
                want_cookies,
                msg="query {}; got {}; want {}".format(url, got_cookies, want_cookies),
            )
