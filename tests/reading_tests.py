import datetime

import mock

import readit

import testing


def truncate_datetime_instance(dt):
    """Answers a :py:class:`datetime.datetime` instance equal to
    :py:param:`dt` truncated to seconds."""
    return dt - datetime.timedelta(microseconds=dt.microsecond)


class ReadingTests(testing.TestCase):
    def setUp(self):
        super(ReadingTests, self).setUp()
        self.user = readit.User()
        self.reading = readit.Reading('<Title>', '<Link>')
        # we need a datetime object after we patch below so create it here
        self.instance_in_time = datetime.datetime.utcnow()
        # and a truncated version as well
        self.truncated_instance = truncate_datetime_instance(
            self.instance_in_time)

    def test_list_for_unknown_user_is_empty(self):
        self.assertEqual(0, len(self.user.readings))

    @mock.patch('datetime.datetime')
    def test_when_defaults_to_now(self, datetime_cls):
        datetime_cls.utcnow.return_value = self.instance_in_time
        self.reading = readit.Reading('<Title>', '<Link>')
        self.assertIsNotNone(self.reading.when)
        self.assertEquals(self.reading.when, self.truncated_instance)

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

    def test_when_property_can_be_assigned_iso8601_string(self):
        self.reading.when = self.instance_in_time.strftime('%Y-%m-%dT%H:%M:%S')
        self.assertEquals(self.reading.when, self.truncated_instance)

    def test_when_property_can_be_assigned_datetime_instance(self):
        self.reading.when = self.instance_in_time
        self.assertEquals(self.reading.when, self.truncated_instance)

    def test_when_property_is_in_seconds(self):
        # we want to make sure that we have a non-zero microseconds in the
        # ``when`` value to verify that truncation will occur.  The other
        # tests will succeed when truncation is unnecessary.
        then = datetime.datetime(2013, 01, 22, 10, 12, 42, 92304)
        self.reading.when = then
        self.assertNotEqual(self.reading.when, then)
        self.assertEquals(self.reading.when, truncate_datetime_instance(then))

    def test_user_id_of_None_is_not_stringified(self):
        self.reading.user_id = None
        self.assertIsNone(self.reading.user_id)

class StorableProtocolTests(testing.StorableItemTestCase):
    StorableClass = readit.Reading
    REQUIRED_ATTRIBUTES = ['title', 'link', 'when', 'user_id']

    def create_storable_instance(self):
        a_reading = readit.Reading(title='<Title>', link='<Link>')
        a_reading._user_id = '<UserId>'
        return a_reading


