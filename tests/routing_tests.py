from __future__ import with_statement
import json
import urlparse

import mock

import readit

from .testing import ReaditTestCase


class RoutingTests(ReaditTestCase):
    def test_not_logged_in_redirect(self):
        rv = self.client.get('/')
        self.assert_is_http_redirect(rv)
        url = urlparse.urlparse(rv.location)
        self.assertEquals('/login', url.path)

    def test_root_redirect_when_logged_in(self):
        self.load_session(session_key=self.session_key)
        rv = self.client.get('/')
        self.assert_is_http_redirect(rv)
        url = urlparse.urlparse(rv.location)
        self.assertEquals(self.links['get-readings']['url'], url.path)

    def test_login_redirects_when_logged_in(self):
        readit.app.oid = mock.Mock()
        readit.app.oid.get_next_url.return_value = 'http://next.url'
        self.load_session(session_key=self.session_key)
        rv = self.client.get('/login')
        self.assert_is_http_redirect(rv)
        self.assertEquals('http://next.url', rv.location)

    def test_login_honors_next_param_when_logged_in(self):
        readit.app.oid = mock.Mock()
        self.should_not_be_called(readit.app.oid, 'get_next_url')
        self.load_session(session_key=self.session_key)
        rv = self.client.get('/login?next=http%3A//next.url')
        self.assert_is_http_redirect(rv)
        self.assertEquals('http://next.url', rv.location)

    def test_logout_clears_session(self):
        self.load_session(session_key=self.session_key)
        rv = self.walk_link('logout')
        self.assertEquals(200, rv.status_code)
        with self.client.session_transaction() as flask_sess:
            self.assertNotIn('session_key', flask_sess)

    def test_json_redirect_hack(self):
        self.load_session(session_key=self.session_key)
        rv = self.client.get('/',
                headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(rv.content_type, 'application/json')
        data = json.loads(rv.data)
        self.assertIn('redirect_to', data)
        url = urlparse.urlparse(data['redirect_to'])
        self.assertEquals(self.links['get-readings']['url'], url.path)

