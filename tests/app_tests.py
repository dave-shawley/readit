from __future__ import with_statement

import os
import os.path
import re
import urllib

import flask
import mock

import readit

from .testing import ReaditTestCase


#  Change this to the class that should be patched for storage
#  related calls.
STORAGE_CLASS = 'readit.mongo.Storage'


class LoginTests(ReaditTestCase):

    def setUp(self):
        super(LoginTests, self).setUp()
        self.saved_oid = readit.app.oid
        self.fake_user = readit.User()
        self.fake_user.email = '<EmailAddress>'
        self.fake_user.user_id = '<UserId>'
        self.fake_oid_details = mock.Mock()
        self.fake_oid_details.openid = '<ReturnedOpenId>'
        self.fake_oid_details.identity_url = '<IdentityUrl>'
        self.fake_oid_details.email = '<EmailAddress>'

    def tearDown(self):
        readit.app.oid = self.saved_oid
        super(LoginTests, self).tearDown()

    def test_openid_login(self):
        open_id = mock.Mock()
        open_id.try_login.return_value = 'Open ID return value'
        readit.app.oid = open_id
        rv = self.client.post('/login', data={
            'openid': 'Open ID input value',
            })
        self.assertEquals(rv.data, 'Open ID return value')
        open_id.get_next_url.return_value = 'http://next.url/'
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()  # invoke before handlers
            flask.g.db = mock.Mock()
            flask.g.db.retrieve_one.return_value = self.fake_user
            rv = readit.app._login_succeeded(self.fake_oid_details)
            self.assertTrue(300 <= rv.status_code < 400)
            self.assertEquals(rv.headers['location'], 'http://next.url/')
            self.assertEquals(flask.g.user.open_id,
                    self.fake_oid_details.identity_url)
            self.assertEquals(flask.session['session_key'],
                    flask.g.user.session_key)

    def test_openid_login_honors_next_param(self):
        readit.app.oid = mock.Mock()
        self.should_not_be_called(readit.app.oid, 'get_next_url')
        with readit.app.test_request_context(
                '/login?next=http%3A//next.url/', method='POST',
                data={'openid': '<RequestedOpenId>'}):
            readit.app.preprocess_request()  # invoke before handlers
            flask.g.db = mock.Mock()
            flask.g.db.retrieve_one.return_value = self.fake_user
            rv = readit.app._login_succeeded(self.fake_oid_details)
            self.assertTrue(300 <= rv.status_code < 400)
            self.assertEquals(rv.headers['location'], 'http://next.url/')
            self.assertEquals(flask.g.user.open_id,
                    self.fake_oid_details.identity_url)
            self.assertEquals(flask.session['session_key'],
                    flask.g.user.session_key)

    def test_login_form_honors_next_param(self):
        rv = self.client.get('/login?next=http%3A//next.url/')
        self.assertEquals(200, rv.status_code)
        m = re.search('input.*name="next".*value="(?P<next>[^"]*)"', rv.data)
        self.assertIsNotNone(m)
        self.assertEquals('http://next.url/', m.group('next'))

    @mock.patch(STORAGE_CLASS)
    def test_user_lookup_in_login(self, storage_class):
        storage = storage_class.return_value
        storage.retrieve_one.return_value = self.fake_user
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()
            self.assertNotIn('user_id', flask.session)
            readit.app._login_succeeded(self.fake_oid_details)
            storage.retrieve_one.assert_called_once_with('users',
                    email=self.fake_oid_details.email,
                    clazz=readit.User)
            self.assertEquals(flask.session['user_id'],
                    self.fake_user.user_id)

    @mock.patch(STORAGE_CLASS)
    def test_login_fails_for_unknown_user(self, storage_class):
        storage = storage_class.return_value
        storage.retrieve_one.return_value = None
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()
            rv = readit.app._login_succeeded(self.fake_oid_details)
            self.assertEquals(404, rv.status_code)

    def test_openid_failure_triggers_500(self):
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()
            open_id = mock.Mock()
            
            def side_effect(*args, **ignored):
                readit.app._report_openid_error('failure')
            open_id.try_login.side_effect = side_effect
            readit.app.oid = open_id
            rsp = self.client.post('/login', data={'openid': '<OpenId>'})
            self.assertEquals(500, rsp.status_code)

    def test_login_missing_openid_in_form_triggers_500(self):
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()
            rsp = self.client.post('/login', data={})
            self.assertEquals(500, rsp.status_code)


class ApplicationTests(ReaditTestCase):

    def test_static_file_fetch(self):
        rv = self.client.get('/favicon.ico')
        self.assertEquals(rv.status_code, 200)
        last_mod = rv.headers['last-modified']
        rv = self.client.get('/favicon.ico', headers=[
            ('if-modified-since', last_mod),
            ])
        self.assertEquals(rv.status_code, 304)

    def test_cache_timeout_override(self):
        static_folder, debug, lifetime = (readit.app.static_folder,
                readit.app.debug, readit.app.JAVASCRIPT_DEBUG_FILE_LIFETIME)
        try:
            @readit.app.route('/readit.js')
            def test_javascript():
                return readit.app.send_static_file('readit.js')
            path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(path, '../javascript')
            path = os.path.abspath(path)
            readit.app.static_folder = path
            readit.app.debug = True
            readit.app.JAVASCRIPT_DEBUG_FILE_LIFETIME *= 2
            rv = self.client.get('/readit.js')
            self.assertEquals(rv.cache_control.max_age,
                    readit.app.JAVASCRIPT_DEBUG_FILE_LIFETIME)
        finally:
            readit.app.static_folder = static_folder
            readit.app.debug = debug
            readit.app.JAVASCRIPT_DEBUG_FILE_LIFETIME = lifetime

    def test_reading_list_as_html(self):
        self.load_session(session_key=self.session_key)
        rv = self.client.get(self.get_session_url_for('/readings'), headers=[
                ('Accept', 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8')
            ])
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(rv.mimetype, 'text/html')

    @mock.patch(STORAGE_CLASS)
    def test_reading_list_as_json(self, storage_class):
        storage = storage_class.return_value
        storage.retrieve.return_value = {'readings': {}}
        self.load_session(session_key=self.session_key)
        rv = self.client.get(self.get_session_url_for('/readings'), headers=[
                ('Accept', 'application/json,text/javascript,*/*;q=0.1')
            ])
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(rv.mimetype, 'application/json')

    @mock.patch(STORAGE_CLASS)
    def test_retrieve_readings_from_storage(self, storage_class):
        reading_link = self.get_session_url_for('/readings')
        headers = [('Accept', 'application/json')]
        storage = storage_class.return_value
        self.load_session(session_key=self.session_key, user_id='<UserId>')
        with readit.app.test_request_context(reading_link):
            readit.app.preprocess_request()
            storage.retrieve.return_value = {'readings': {}}
            self.client.get(reading_link, headers=headers)
            storage.retrieve.assert_called_with('readings',
                    user_id='<UserId>', clazz=readit.Reading)

    @mock.patch(STORAGE_CLASS)
    def test_add_json_reading(self, storage_class):
        storage = storage_class.return_value
        self.load_session(session_key=self.session_key, user_id='<UserId>')
        reading_link = self.get_session_url_for('/readings')
        reading_obj = readit.Reading()
        reading_obj.title = 'Method Resolution Order'
        reading_obj.link = ('http://python-history.blogspot.com/2010/06/'
                'method-resolution-order.html')
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()
            data = '{{"title":"{0}","link":"{1}"}}'.format(
                    reading_obj.title, reading_obj.link)
            rsp = self.client.post(reading_link, data=data,
                    content_type='application/json')
            self.assert_is_http_success(rsp)
            storage.save.assert_called_with('readings', reading_obj)

    @mock.patch(STORAGE_CLASS)
    def test_add_form_reading(self, storage_class):
        storage = storage_class.return_value
        self.load_session(session_key=self.session_key, user_id='<UserId>')
        reading_link = self.get_session_url_for('/readings')
        reading_obj = readit.Reading()
        reading_obj.title = 'Method Resolution Order'
        reading_obj.link = ('http://python-history.blogspot.com/2010/06/'
                'method-resolution-order.html')
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()
            rsp = self.client.post(reading_link, data={
                'title': reading_obj.title, 'link': reading_obj.link})
            self.assert_is_http_success(rsp)
            storage.save.assert_called_with('readings', reading_obj)

    @mock.patch(STORAGE_CLASS)
    def test_remove_reading(self, storage_class):
        storage = storage_class.return_value
        self.load_session(session_key=self.session_key, user_id='<UserId>')
        reading_obj = readit.Reading()
        reading_obj.object_id = "123456abcdef"
        reading_obj.title = 'Method Resolution Order'
        reading_obj.link = ('http://python-history.blogspot.com/2010/06/'
                'method-resolution-order.html')
        reading_link = self.get_session_url_for('/readings/' +
                urllib.quote(reading_obj.object_id))
        with readit.app.test_request_context('/'):
            readit.app.preprocess_request()
            rsp = self.client.delete(reading_link)
            self.assert_is_http_success(rsp)
            storage.remove.assert_called_with('readings', '<UserId>',
                    _id=reading_obj.object_id)

    @mock.patch(STORAGE_CLASS)
    @mock.patch.dict('os.environ', {'MONGOURL': '<MongoStorageUrl>'})
    def test_connection_string_comes_from_env(self, storage_class):
        readit.app.load_configuration()
        storage = storage_class.return_value
        storage.retrieve.return_value = {'readings': {}}
        self.load_session(session_key=self.session_key)
        request_url = self.get_session_url_for('/readings')
        with readit.app.test_request_context(request_url):
            readit.app.preprocess_request()
            self.client.get(request_url)
            storage_class.assert_called_with(storage_url='<MongoStorageUrl>')

