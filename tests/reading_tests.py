import datetime

import mock

import readit

import testing


class ReadingTests(testing.TestCase):
    def setUp(self):
        super(ReadingTests, self).setUp()
        self.user = readit.User()
        self.reading = readit.Reading('<Title>', '<Link>')
        # we need a datetime object after we patch below so create it here
        self.now = datetime.datetime(2012, 1, 19, 14, 15, 25)

    def test_list_for_unknown_user_is_empty(self):
        self.assertEqual(0, len(self.user.readings))

    @mock.patch('datetime.datetime')
    def test_when_defaults_to_now(self, datetime_cls):
        datetime_cls.utcnow.return_value = self.now
        self.reading = readit.Reading('<Title>', '<Link>')
        self.assertIsNotNone(self.reading.when)
        self.assertEquals(self.now, self.reading.when)

    def test_add_reading(self):
        self.user.add_reading(self.reading)
        self.assertEqual(1, len(self.user.readings))
        self.assertEqual(self.reading, self.user.readings[0])

    def test_reading_equals(self):
        self.assertEqual(self.reading, readit.Reading(
                self.reading.title, self.reading.link))
        self.assertNotEqual(self.reading, readit.Reading(
                self.reading.title, '<Other Link>'))
        self.assertNotEqual(self.reading, readit.Reading(
                '<Other Title>', self.reading.link))
        self.assertNotEqual(self.reading, None)

    def test_remove_reading(self):
        self.user.add_reading(self.reading)
        self.user.remove_reading(readit.Reading('<Title>', '<Link>'))
        self.assertEquals(0, len(self.user.readings))

    def test_add_reading_idempotent(self):
        self.user.add_reading(self.reading)
        self.user.add_reading(self.reading)
        self.assertEquals(1, len(self.user.readings))

    def test_str_magic_behaves(self):
        reading1 = readit.Reading('<Title>', '<Link>')
        reading2 = readit.Reading('<Title>', '<Link>')
        reading3 = readit.Reading(None, None)
        self.assertEquals(str(reading1), str(reading2))
        self.assertNotEquals(str(reading1), str(reading3))

    def test_iso8601_is_valid_when_value(self):
        now = datetime.datetime.utcnow()
        self.reading.when = now.strftime('%Y-%m-%dT%H:%M:%S')
        # Note - subsecond portion stripped
        now -= datetime.timedelta(microseconds=now.microsecond)
        self.assertEquals(now, self.reading.when)

    def test_datetime_is_valid_when_value(self):
        now = datetime.datetime.utcnow()
        self.reading.when = now
        # Note - subsecond portion stripped
        now -= datetime.timedelta(microseconds=now.microsecond)
        self.assertEquals(now, self.reading.when)


class StorableProtocolTests(testing.StorableItemTestCase):
    StorableClass = readit.Reading
    REQUIRED_ATTRIBUTES = ['title', 'link', 'when', 'user_id']

    def create_storable_instance(self):
        a_reading = readit.Reading(title='<Title>', link='<Link>')
        a_reading.user_id = '<UserId>'
        return a_reading


