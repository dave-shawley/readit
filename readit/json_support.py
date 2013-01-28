"""
Pluggable JSON Support Layer
============================
"""
import datetime

import flask
import readit
import pymongo.objectid


class JSONEncoder(flask.json.JSONEncoder):
    """Specialization of :py:class:`flask.json.JSONEncoder` that supports
    encoding some of our objects.
    
    New objects are supported by adding new encoder instances to
    :py:attr:`json_encoder`.  A *encoder instance* is something that implements
    the following simple protocol:
    
     - ``enc.can_encode(object) -> bool``
     - ``enc.encode(object) -> dict``
    
    A number of useful encoders are loaded into :py:attr:`json_encoder`
    automatically and additional encoders can be added as needed.
    """
    def __init__(self, *args, **kwds):
        super(JSONEncoder, self).__init__(*args, **kwds)
        self.json_encoders = [
            DateTimeJSONSupport(),
            ObjectIdJSONSupport(),
            ReadingSupport(),
        ]

    def default(self, o):
        for supporter in self.json_encoders:
            if supporter.can_encode(o):
                return supporter.encode(o)
        return super(JSONEncoder, self).default(o)


class JSONDecoder(flask.json.JSONDecoder):
    """Specialization of :py:class:`flask.json.JSONDecoder` that supports
    decoding of class hinted instances.
    """
    def __init__(self, *args, **kwds):
        kwds['object_hook'] = _deserialize_object_hook
        super(JSONDecoder, self).__init__(*args, **kwds)


class DateTimeJSONSupport(object):
    """I encode :py:class:`datetime.datetime` instances ISO8601 stirngs.
    
    >>> self = DateTimeJSONSupport()
    >>> now = datetime.datetime(1999, 12, 31, 23, 59, 59)
    >>> self.encode(now)
    '1999-12-31T23:59:59Z'
    
    I advertise :py:class:`datetime.datetime` instances as ISO8601
    strings assuming that the input is in UTC time.  Basically, I call
    :py:meth:`datetime.datetime.isoformat` on the instance and append
    'Z' explicitly.
    """
    def __init__(self, *args, **kwds):
        super(DateTimeJSONSupport, self).__init__(*args, **kwds)

    def can_encode(self, obj):
        return isinstance(obj, datetime.datetime)

    def encode(self, obj):
        return obj.isoformat() + 'Z'


class StorableItemJSONSupport(object):
    """I know how to encode instances that implement the ``StorableItem``
    protocol.
    
    ``StorableItem`` instances are actually quite easy to store since the
    ``to_persistence`` method returns a dictionary instance.  All that I do
    is make sure that the method exists, call it when I need to encode an
    instance, and tack on the ``object_id`` as the ``id`` property.
    
    >>> self = StorableItemJSONSupport()
    >>> class Item(object):
    ...   def __init__(self):
    ...      self.object_id = 1234
    ...   def to_persistence(self):
    ...     return {'attribute': 'value'}
    ...
    >>> obj = Item()
    >>> self.can_encode(obj)
    True
    >>> result = self.encode(obj)
    >>> result['attribute'], result['id']
    ('value', 1234)

    Note that the ``id`` property is passed through as an integer in this
    case.  Properties will be recursively processed if necessary.  This is
    important since the ``object_id`` is most likely something like a MongoDB
    py:class:`~pymongo.objectid.ObjectId` instance which is handled by a
    separate support package.
    """
    def __init__(self, *args, **kwds):
        super(StorableItemJSONSupport, self).__init__(*args, **kwds)

    def can_encode(self, obj):
        return hasattr(obj, 'to_persistence')

    def encode(self, obj):
        encoded = obj.to_persistence()
        encoded['id'] = obj.object_id
        return encoded


class ObjectIdJSONSupport(object):
    """I take care of translating MongoDB ObjectId's into JSON.
    
    >>> self = ObjectIdJSONSupport()
    >>> oid = pymongo.objectid.ObjectId('4fadcd174e02d83c8c000000')
    >>> self.can_encode(oid)
    True
    >>> self.encode(oid)
    '4fadcd174e02d83c8c000000'
    
    Object ID's are simply passed around as strings.  They could be easily
    translated into JSONRPC syntax, but that really complicates things
    more than necessary.
    """
    def __init__(self, *args, **kwds):
        super(ObjectIdJSONSupport, self).__init__(*args, **kwds)

    def can_encode(self, obj):
        return isinstance(obj, pymongo.objectid.ObjectId)

    def encode(self, obj):
        return str(obj)


class ReadingSupport(StorableItemJSONSupport):
    """I provide a little additional magic for :py:class:`readit.Reading`
    objects.
    
    >>> self = ReadingSupport()
    >>> a_reading = readit.Reading()
    >>> self.can_encode(a_reading)
    True
    >>> result = self.encode(a_reading)
    """
    def __init__(self, *args, **kwds):
        super(ReadingSupport, self).__init__(*args, **kwds)

    def can_encode(self, obj):
        return (isinstance(obj, readit.Reading)
                or super(ReadingSupport, self).can_encode(obj))

    def encode(self, obj):
        encoded = super(ReadingSupport, self).encode(obj)
        if isinstance(obj, readit.Reading):
            encoded['__class__'] = 'readit.Reading'
        return encoded


def _deserialize_object_hook(a_dict):
    if '__class__' in a_dict:
        #if a_dict['__class__'] == 'readit.Reading':
        #    if 'object_id' in a_dict:
        #        a_dict['_id'] = a_dict['id']
        #        del a_dict['id']
        pass
    return a_dict



