'''
Testing Helpers
---------------

This module contains some useful testing classes as well as some version
workarounds.  :class:`TestCase` is a version of :class:`unittest.TestCase`
that implements whatever methods are neccessary to make it look like we
are running in Python 2.7.  A number of useful methods were added in 2.7
that are not present in the Python that is readily available in most stable
Linux distros.
'''
import datetime
import functools
import json
import re
import sys
import uuid
import unittest

import readit


(major, minor) = sys.version_info[0:2]
if major < 2 or (major == 2 and minor < 7):
    class AssertRaisesContext(object):
        """I was shamelessly stolen from the 2.7 source tree!"""
        def __init__(self, expected, test_case, expected_regexp=None):
            self.expected = expected
            self.failureException = test_case.failureException
            self.expected_regexp = expected_regexp

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                try:
                    exc_name = self.expected.__name__
                except AttributeError:
                    exc_name = str(self.expected)
                raise self.failureException(
                        "{0} not raised".format(exc_name))
            if not issubclass(exc_type, self.expected):
                return False  # unexpected exceptions handled elsewhere
            self.exception = exc_value  # stash this away
            if self.expected_regexp is None:
                return True
            expected_regexp = self.expected_regexp
            if isinstance(expected_regexp, basestring):
                expected_regexp = re.compile(expected_regexp)
            if not expected_regexp.search(str(exc_value)):
                raise self.failureException('"%s" does not match "%s"' %
                        (expected_regexp.pattern, str(exc_value)))
            return True

    class TestCase(unittest.TestCase):
        def assertIs(self, a, b):
            self.assertTrue(a is b)

        def assertIsNot(self, a, b):
            self.assertTrue(a is not b)

        def assertIsNone(self, x):
            self.assertIs(x, None)

        def assertIsNotNone(self, x):
            self.assertIsNot(x, None)

        def assertIn(self, a, b):
            self.assertTrue(a in b)

        def assertNotIn(self, a, b):
            self.assertTrue(a not in b)

        def assertRaises(self, exc, callable=None, *args, **kwds):
            context = AssertRaisesContext(exc, self)
            if callable is None:
                return context
            with context:
                callable(*args, **kwds)
else:
    TestCase = unittest.TestCase


class HttpTestHelper(TestCase):
    """Version of :class:`unittest.TestCase` that adds some HTTP
    response handling helpers.
    """

    def __init__(self, *args, **kwds):
        TestCase.__init__(self, *args, **kwds)

    def should_not_be_called(self, mock, method_name):
        """Configure a method on a mock that will throw an exception
        if it is called.
        
        :param mock.Mock mock: the mock object to add the method to
        :param str method_name: the name of the method to add
        """
        def throw_exception():
            raise Exception(method_name + ' should not be called')
        method_mock = getattr(mock, method_name)
        method_mock.side_effect = Exception(method_name +
                ' should not be called')

    def assert_is_http_success(self, response):
        status = self._get_status_code(response)
        self.assertTrue(200 <= status < 400,
                msg='{0} is not a successful status code'.format(status))

    def assert_is_http_redirect(self, response):
        status = self._get_status_code(response)
        self.assertTrue(300 <= status < 400,
                msg='{0} is not a redirect status code'.format(status))
        self.assertIsNotNone(response.location)

    def _get_status_code(self, response):
        if isinstance(response, (str, unicode)):
            response = int(response)
        if not isinstance(response, (int, long)):
            response = response.status_code
        return response


class ReaditTestCase(HttpTestHelper):
    '''Version of :class:`unittest.TestCase` that adds a Flask-based
    test client as :data:`self.client` and a few useful methods too.
    '''
    def __init__(self, *args, **kwds):
        HttpTestHelper.__init__(self, *args, **kwds)

    def setUp(self):
        readit.app.config['TESTING'] = True
        self.client = readit.app.test_client()
        self.session_key = str(uuid.uuid4())
        self.in_past = (datetime.datetime.utcnow() -
                datetime.timedelta(days=1))
        self.in_future = (datetime.datetime.utcnow() +
                datetime.timedelta(days=1))
        self._link_map = None

    def load_session(self, **sess_values):
        with self.client.session_transaction() as flask_sess:
            for (name, value) in sess_values.iteritems():
                flask_sess[name] = value

    def get_session_url_for(self, path):
        if path and not path.startswith('/'):
            path = '/' + path
        return '/' + self.session_key + path

    @property
    def links(self):
        if self._link_map is None:
            rv = self.client.get(self.get_session_url_for('/links'))
            self.assertEquals(200, rv.status_code)
            self.assertEquals('application/json', rv.mimetype)
            self._link_map = json.loads(rv.data)
        return self._link_map

    def walk_link(self, link_name, data=None):
        link_data = self.links[link_name]
        if link_data['method'] == 'DELETE':
            return self.client.delete(link_data['url'])
        if link_data['method'] == 'GET':
            return self.client.get(link_data['url'])
        self.fail('unhandled link ' + str(link_data))


def skipped(f):
    """Make unittest skip the decorated function."""
    @functools.wraps(f)
    def wrapper(*args):
        print '***', 'IGNORING', f.__module__ + '.' + f.__name__
    return wrapper

