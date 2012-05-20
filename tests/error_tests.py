from .testing import ReaditTestCase


class _LinkTestMixin(object):
    def assertions(self, response):
        self.assertEquals(response.status_code, self.EXPECTED_STATUS_CODE)

    def test_logout(self):
        rv = self.client.delete(self.get_session_url_for(''))
        self.assertions(rv)

    def test_link_retrieval(self):
        rv = self.client.get(self.get_session_url_for('links'))
        self.assertions(rv)

    def test_get_readings(self):
        rv = self.client.get(self.get_session_url_for('readings'))
        self.assertions(rv)


class SessionMismatchTests(ReaditTestCase, _LinkTestMixin):
    EXPECTED_STATUS_CODE = 409

    def setUp(self):
        super(SessionMismatchTests, self).setUp()
        self.load_session(session_key=self.session_key)
        self.session_key = '<FakeSessionKey>'


class MissingSessionKeyTests(ReaditTestCase, _LinkTestMixin):
    EXPECTED_STATUS_CODE = 303


class AddReadingErrorTests(ReaditTestCase):
    def setUp(self):
        super(AddReadingErrorTests, self).setUp()
        self.load_session(session_key=self.session_key, user_id='<UserId>')

    def test_add_reading_without_title(self):
        rsp = self.client.post(self.get_session_url_for('readings'),
                data='{"link":"<Link>"}', content_type='application/json')
        self.assertEquals(400, rsp.status_code)

    def test_add_reading_without_link(self):
        rsp = self.client.post(self.get_session_url_for('readings'),
                data='{"title":"<Title>"}', content_type='application/json')
        self.assertEquals(400, rsp.status_code)


