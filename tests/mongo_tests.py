from pymongo.objectid import ObjectId

import mock

from .testing import TestCase

import readit.mongo


import distutils.version
mock_version = distutils.version.LooseVersion(mock.__version__)
if mock_version < '0.8.0':
    raise ImportError('this test requires at least mock 0.8')


class MongoStorageTests(TestCase):
    CONNECTION_CLASS = 'pymongo.Connection'

    def setUp(self):
        self.test_value = {'<Attribute>': '<Value>'}
        self.storage = readit.mongo.Storage()
        self.mongo_bin = mock.MagicMock()
        self.mongo_slot = mock.MagicMock()
        self.mongo_cursor = mock.Mock()
        self.mongo_bin.__getitem__.return_value = self.mongo_slot
        self.mongo_slot.__getitem__.return_value = self.mongo_cursor

    def tearDown(self):
        readit.mongo.Storage._CONN = None

    def build_mongo_connection(self, mongo_conn_class):
        conn = mongo_conn_class.return_value
        conn.readit = self.mongo_bin
        return conn

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_opens_connection(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.mongo_cursor.find.return_value = []
        self.storage.retrieve('<Bin>', '<Id>')
        mongo_conn_class.assert_called_with(host=None)
        self.mongo_bin.__getitem__.assert_called_with('<Bin>')
        self.mongo_slot.__getitem__.assert_called_with('<Id>')

    @mock.patch(CONNECTION_CLASS)
    def test_save_opens_connection(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save('<Bin>', '<Id>', pi=(22.0 / 7.0))
        mongo_conn_class.assert_called_with(host=None)
        self.mongo_bin.__getitem__.assert_called_with('<Bin>')
        self.mongo_slot.__getitem__.assert_called_with('<Id>')

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_calls_mongo_find(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.mongo_cursor.find.return_value = []
        self.storage.retrieve('<Bin>', '<Id>', **self.test_value)
        self.mongo_cursor.find.assert_called_with(**self.test_value)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_with_factory(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        factory = mock.Mock()
        instance = factory.return_value
        self.mongo_cursor.find.return_value = [self.test_value]
        self.storage.retrieve('<Bin>', '<Id>', factory=factory)
        instance.from_persistence.assert_called_with(self.test_value)

    @mock.patch(CONNECTION_CLASS)
    def test_save_inserts_data(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save('<Bin>', '<Id>', {'<Attribute>': '<Value>'})
        self.mongo_cursor.insert.assert_called_with(self.test_value)

    @mock.patch(CONNECTION_CLASS)
    def test_filtered_removal(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.remove('<Bin>', '<Id>', attribute='value')
        self.mongo_cursor.remove.assert_called_with({'attribute': 'value'})

    @mock.patch(CONNECTION_CLASS)
    def test_remove_objectizes_oids(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.remove('<Bin>', '<Id>', _id='4f78d1f94e02d89ba0000000')
        self.mongo_cursor.remove.assert_called_with({
            '_id': ObjectId('4f78d1f94e02d89ba0000000')})

    @mock.patch(CONNECTION_CLASS)
    def test_new_connection_uses_storage_url(self, mongo_conn_class):
        self.storage = readit.mongo.Storage('<MongoConnectionUrl>')
        self.build_mongo_connection(mongo_conn_class)
        self.mongo_cursor.find.return_value = []
        self.storage.retrieve('<Bin>', '<Id>')
        mongo_conn_class.assert_called_with(host='<MongoConnectionUrl>')

