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

# this makes nose ignore tests defined in this file
__test__ = False


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

    def create_failure_side_effect(self, message):
        def throw_exception(*args, **ignored):
            raise Exception(message)
        return throw_exception

    def should_not_be_called(self, mock, method_name):
        """Configure a method on a mock that will throw an exception
        if it is called.
        
        :param mock.Mock mock: the mock object to add the method to
        :param str method_name: the name of the method to add
        """
        method_mock = getattr(mock, method_name)
        method_mock.side_effect = self.create_failure_side_effect(
            method_name + ' should not be called'
        )

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


class StorableItemTestCase(TestCase, object):
    '''Version of :py:class:`unittest.TestCase` that verifies that a
    class faithfully implements the ``StorableItem`` protocol.'''

    StorableClass = None      # you are required to set this in the subclass
    REQUIRED_ATTRIBUTES = []  # populate this appropriately
    OPTIONAL_ATTRIBUTES = []  # populate this appropriately

    def setUp(self):
        self.storable = self.create_storable_instance()
        self.assertIsInstance(self.storable, self.StorableClass)
        for reqd_attr in self.REQUIRED_ATTRIBUTES:
            self.assertIsNotNone(getattr(self.storable, reqd_attr),
                reqd_attr + ' should not be None in test instance')

    def test_storable_protocol_implemented(self):
        self.storable.object_id = '<ThisValueIsIgnored>'
        persist = self.storable.to_persistence()
        new_instance = self.StorableClass.from_persistence(persist)
        for attr in persist:
            self.assertEquals(getattr(new_instance, attr), persist[attr])
        # this will be added by the persistence layer
        self.assertIsNone(new_instance.object_id)

    def test_required_attributes_are_stored(self):
        persist = self.storable.to_persistence()
        for attr_name in self.REQUIRED_ATTRIBUTES:
            self.assertIn(attr_name, persist)

    def test_optional_attributes_can_be_round_tripped(self):
        if self.OPTIONAL_ATTRIBUTES:
            for attr_name in self.OPTIONAL_ATTRIBUTES:
                setattr(self.storable, attr_name, '<' + attr_name + 'Value>')
            persist = self.storable.to_persistence()
            self.StorableClass.from_persistence(persist)
            for attr_name in self.OPTIONAL_ATTRIBUTES:
                self.assertIsNotNone(getattr(self.storable, attr_name))

    def test_from_persistence_requires_attributes(self):
        for attr_name in self.REQUIRED_ATTRIBUTES:
            persist = self.storable.to_persistence()
            del persist[attr_name]
            with self.assertRaises(KeyError):
                self.StorableClass.from_persistence(persist)

    def create_storable_instance(self):
        """Subclasses are required to implement this.  It is required to answer
        with an instance of ``StorableClass`` that sets the attributes listed
        in ``REQUIRED_ATTRIBUTES``."""
        raise NotImplementedError('create_storable_instance is not '
                + 'implemented by ' + str(self.__class__))


def skipped(f):
    """Make unittest skip the decorated function."""
    @functools.wraps(f)
    def wrapper(*args):
        sys.stderr.write('\n*** IGNORING %s.%s\n' % (f.__module__, f.__name__))
    return wrapper


def expect_exception(exc_type):
    """Wrap a test case that raises a specific exception type."""
    def decorator(test_case):
        @functools.wraps(test_case)
        def wrapper(self, *pos, **kwds):
            try:
                test_case(self, *pos, **kwds)
            except Exception, exc:
                if not isinstance(exc, exc_type):
                    raise AssertionError(
                        'expected exception of type %s, got %s' % (
                            exc_type, exc.__class__))
                return
            raise AssertionError(
                'expected exception of type %s, none raised' % exc_type)
        return wrapper
    return decorator

