import datetime
import pymongo.objectid

from .testing import TestCase

import readit
import readit.json_support


class CoordinateObject(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.object_id = pymongo.objectid.ObjectId()

    def to_persistence(self):
        return {'x': self.x, 'y': self.y}


class JSONTests(TestCase):
    def setUp(self):
        self.encoder = readit.json_support.JSONEncoder()
        self.decoder = readit.json_support.JSONDecoder()

    def test_storable_support(self):
        item = CoordinateObject(1, 2)
        json_str = self.encoder.encode(item)
        result = self.decoder.decode(json_str)
        self.assertEquals(result['x'], item.x)
        self.assertEquals(result['y'], item.y)
        self.assertEquals(result['object_id'], str(item.object_id))

    def test_datetime_support(self):
        ts = datetime.datetime.utcnow()
        json_str = self.encoder.encode({'timestamp': ts})
        value = self.decoder.decode(json_str)
        self.assertEquals(ts.isoformat() + 'Z', value['timestamp'])

    def test_basic_encode_decode(self):
        objects = [
                {'one': 1, 'two': 2},
                [1, 2, 3],
                'simple string',
                u'unicode string',
                42,
                22.7
                ]
        for obj in objects:
            json_str = self.encoder.encode(obj)
            result = self.decoder.decode(json_str)
            self.assertEquals(obj, result)

    def test_encode_unknown_fails(self):
        with self.assertRaises(TypeError):
            self.encoder.encode(object())

    def test_decode_unknown_is_passthru(self):
        json_str = '{"unknown":{"__jsonclass__":"Unknown"}}'
        result = self.decoder.decode(json_str)
        self.assertEquals({'unknown': {'__jsonclass__': 'Unknown'}}, result)

    def test_mongo_objectid_support(self):
        oid = pymongo.objectid.ObjectId()
        json_str = self.encoder.encode({'objectid': oid})
        value = self.decoder.decode(json_str)
        self.assertEquals(str(oid), value['objectid'])

    def test_reading_support_with_uuid_based_id(self):
        a_reading = readit.Reading(title='Title', link='Link')
        a_reading.object_id = pymongo.objectid.ObjectId()
        json_str = self.encoder.encode(a_reading)
        print json_str
        value = self.decoder.decode(json_str)
        self.assertEquals(value['__class__'], 'readit.Reading')
        self.assertEquals(value['title'], a_reading.title)
        self.assertEquals(value['link'], a_reading.link)
        self.assertEquals(value['when'], a_reading.when.isoformat()+'Z')
        self.assertEquals(value['object_id'], str(a_reading.object_id))

