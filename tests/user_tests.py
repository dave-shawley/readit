import os

import mock

import readit

import testing


class UserTests(testing.TestCase):
    def setUp(self):
        self.random_session_key = os.urandom(16)
        self.user = readit.User(None)

    def test_session_key_is_preserved(self):
        u = readit.User(self.random_session_key)
        self.assertEqual(u.session_key, self.random_session_key)

    def test_session_key_can_be_none(self):
        self.assertEqual(self.user.session_key, None)

    def test_login_generates_session_key(self):
        self.user.login(mock.Mock())
        self.assertIsNotNone(self.user.session_key)

    def test_login_and_logout(self):
        self.user.login(mock.Mock())
        self.assertTrue(self.user.logged_in)
        self.user.logout()
        self.assertFalse(self.user.logged_in)

    def test_open_id_property(self):
        oid_details = mock.Mock()
        oid_details.identity_url = 'identity url'
        self.user.login(oid_details)
        self.assertTrue(self.user.open_id, 'identity url')

    def test_name_defaults_to_oid(self):
        oid_details = mock.Mock()
        oid_details.identity_url = 'identity url'
        self.user.login(oid_details)
        self.assertTrue(self.user.display_name, 'identity url')

    def test_email_overrides_oid_for_name(self):
        oid_details = mock.Mock()
        oid_details.email = 'email address'
        oid_details.identity_url = 'identity url'
        self.user.login(oid_details)
        self.assertTrue(self.user.display_name, 'email address')

    def test_nickname_preferred_for_name(self):
        oid_details = mock.Mock()
        oid_details.email = 'email address'
        oid_details.identity_url = 'identity url'
        oid_details.nickname = 'nickname'
        self.user.login(oid_details)
        self.assertTrue(self.user.display_name, 'nickname')

    def test_fullname_preferred_for_name(self):
        oid_details = mock.Mock()
        oid_details.email = 'email address'
        oid_details.fullname = 'full name'
        oid_details.identity_url = 'identity url'
        oid_details.nickname = 'nickname'
        self.user.login(oid_details)
        self.assertTrue(self.user.display_name, 'full name')

    def test_user_id_property(self):
        self.assertIsNone(self.user.user_id)
        self.user.user_id = mock.sentinel.user_id
        oid_details = mock.Mock()
        oid_details.identity_url = mock.sentinel.identity_url
        self.user.login(oid_details)
        self.assertEquals(self.user.user_id, mock.sentinel.user_id)

    def test_object_id_property(self):
        self.user.object_id = 42  # this will be stringified
        self.assertEquals(self.user.object_id, '42')
        self.assertEquals(self.user.object_id, self.user.user_id)


class StorableProtocolTests(testing.StorableItemTestCase):
    StorableClass = readit.User
    REQUIRED_ATTRIBUTES = ['email']
    OPTIONAL_ATTRIBUTES = ['display_name']

    def create_storable_instance(self):
        a_user = readit.User()
        a_user.email = '<EMailAddress>'
        return a_user



