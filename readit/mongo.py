from __future__ import with_statement

import bson.errors
import functools
import pymongo
import threading
import uuid

from pymongo.objectid import ObjectId

import readit


class Storage(object):
    """I store object states as simple :py:class:`dict` instances.
    
    Instances are stored as dictionaries identified by an calcualted
    identifier.  The ID is either assigned by the caller or formulated
    using a generation function that is identified when the
    :py:class:`Storage` instance is created.
    """

    _CONN = None
    _CONN_LOCK = threading.Lock()

    def __init__(self, storage_url=None, id_extractor=None):
        self.storage_url = storage_url
        self.id_extractor = id_extractor

    def save(self, storage_bin, storage_id=None, storable=None, **persist_values):
        if storable is None:
            storable = persist_values
        if storage_id is None:
            storage_id = self.id_extractor(storable)
        self._add_to_bin(storage_bin, storage_id, storable)

    def retrieve_one(self, storage_bin, **arguments):
        result = self.retrieve(storage_bin, **arguments)
        if len(result) > 1:
            raise readit.MoreThanOneResultError()
        return result

    def retrieve(self, storage_bin, storage_id=None, factory=None, **constraint):
        conn = self.get_mongo_connection()
        if storage_id is not None:
            constraint['_id'] = self._create_object_id(storage_id)
        values = conn[storage_bin].find(**constraint)
        if factory and values:
            def manufacture(data):
                value = factory()
                value.from_persistence(data)
                return value
            values = (manufacture(v) for v in values)
        return list(values)

    def remove(self, storage_bin, storage_id, **constraint):
        constraint['_id'] = self._create_object_id(storage_id)
        conn = self.get_mongo_connection()
        collection = conn[storage_bin]
        print 'deleting', str(constraint), 'from', str(collection)
        collection.remove(constraint)

    def get_mongo_connection(self):
        if Storage._CONN is None:
            with Storage._CONN_LOCK:
                if Storage._CONN is None:
                    Storage._CONN = pymongo.Connection(host=self.storage_url)
        return Storage._CONN.readit

    def _add_to_bin(self, storage_bin, storage_id, persist_value):
        conn = self.get_mongo_connection()
        persist_value['_id'] = self._create_object_id(storage_id)
        conn[storage_bin].insert(persist_value)

    def _create_object_id(self, storage_id):
        try:
            return ObjectId(storage_id)
        except Exception:  # we tried!
            pass
        if isinstance(storage_id, uuid.UUID):
            return ObjectId('{0:08x}{3:02x}{4:02x}{5:012x}'.format(
                *storage_id.get_fields()))
        hash_value = abs(hash(storage_id))
        return ObjectId('{:024x}'.format(hash_value))

