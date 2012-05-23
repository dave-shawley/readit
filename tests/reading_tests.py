import datetime

import mock

import readit

from .testing import TestCase


class ReadingTests(TestCase):
    def setUp(self):
        super(ReadingTests, self).setUp()
        self.user = readit.User()
        self.reading = readit.Reading('<Title>', '<Link>')
        # we need a datetime object after we patch below
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
        self.assertEqual(self.reading, readit.Reading('<Title>', '<Link>'))

    def test_remove_reading(self):
        self.user.add_reading(self.reading)
        self.user.remove_reading(readit.Reading('<Title>', '<Link>'))
        self.assertEquals(0, len(self.user.readings))

    def test_add_reading_idempotent(self):
        self.user.add_reading(self.reading)
        self.user.add_reading(self.reading)
        self.assertEquals(1, len(self.user.readings))

    def test_reading_is_hashable(self):
        readings = set()
        readings.add(readit.Reading('<Title>', '<Link>'))
        self.assertEquals(1, len(readings))
        readings.add(readit.Reading('<Title>', '<Link>'))
        self.assertEquals(1, len(readings))
        readings.remove(readit.Reading('<Title>', '<Link>'))
        self.assertEquals(0, len(readings))

    def test_hash_magic_behaves(self):
        reading1 = readit.Reading('<Title>', '<Link>')
        reading2 = readit.Reading('<title>', '<Link>')
        reading3 = readit.Reading('<Title>', '<Link>')
        self.assertNotEquals(hash(reading1), hash(reading2))
        self.assertEquals(hash(reading1), hash(reading3))
        self.assertEquals(hash(readit.Reading(None, None)),
                hash(readit.Reading(None, None)))

    def test_str_magic_behaves(self):
        reading1 = readit.Reading('<Title>', '<Link>')
        reading2 = readit.Reading('<Title>', '<Link>')
        reading3 = readit.Reading(None, None)
        reading1._id = reading2._id
        self.assertEquals(str(reading1), str(reading2))
        self.assertNotEquals(str(reading1), str(reading3))

    def test_reading_implements_storable_protocol(self):
        persist = self.reading.to_persistence()
        for attr_name in self.reading._PERSIST:
            self.assertEqual(getattr(self.reading, attr_name),
                    persist[attr_name])
        new_reading = readit.Reading()
        new_reading.from_persistence(persist)
        self.assertEquals(self.reading, new_reading)

    def test_important_attributes_stored(self):
        persist = self.reading.to_persistence()
        self.assertIn('title', persist)
        self.assertIn('link', persist)
        self.assertIn('when', persist)

    def test_reading_has_unique_id(self):
        reading1 = readit.Reading('<Title>', '<Link>')
        reading2 = readit.Reading('<Title>', '<Link>')
        self.assertNotEquals(reading1._id, reading2._id)

