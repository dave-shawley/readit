from __future__ import with_statement

import functools
import pymongo
import threading
from pymongo.objectid import ObjectId

import readit


class Storage(readit.Storage):
    _CONN = None
    _CONN_LOCK = threading.Lock()

    def __init__(self, storage_url=None):
        super(Storage, self).__init__()
        self.storage_url = storage_url

    def _add_to_bin(self, storage_bin, storage_id, persist_value):
        conn = self.get_mongo_connection()
        conn[storage_bin][storage_id].insert(persist_value)

    def retrieve(self, storage_bin, storage_id, factory=None, **constraint):
        conn = self.get_mongo_connection()
        values = conn[storage_bin][storage_id].find(**constraint)
        if factory and values:
            create = functools.partial(self._create_from_factory, factory)
            values = map(create, values)
        return list(values)

    def remove(self, storage_bin, storage_id, **constraint):
        if '_id' in constraint:
            constraint['_id'] = ObjectId(constraint['_id'])
        conn = self.get_mongo_connection()
        collection = conn[storage_bin][storage_id]
        print 'deleting', str(constraint), 'from', str(collection)
        collection.remove(constraint)

    def get_mongo_connection(self):
        if Storage._CONN is None:
            with Storage._CONN_LOCK:
                if Storage._CONN is None:
                    Storage._CONN = pymongo.Connection(host=self.storage_url)
        return Storage._CONN.readit

