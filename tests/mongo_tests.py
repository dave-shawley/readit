import os
from pymongo.objectid import ObjectId

import mock
from .testing import TestCase

import readit.mongo


import distutils.version
mock_version = distutils.version.LooseVersion(mock.__version__)
if mock_version < '0.8.0':
    raise ImportError('this test requires at least mock 0.8')

CONNECTION_CLASS = 'pymongo.Connection'


class TestStorable:
    def __init__(self, **attributes):
        self.object_id = None
        self.attributes = attributes.copy()

    def to_persistence(self):
        return self.attributes.copy()

    @classmethod
    def from_persistence(clazz, value_dict):
        return TestStorable(**value_dict)


class MongoTestCase(TestCase):
    BIN_NAME = '<Bin>'

    def setUp(self):
        self.storage_id = ''.join(('{:02x}'.format(ord(x))
                                   for x in os.urandom(12)))
        self.storage = readit.mongo.Storage()
        self.collection = mock.MagicMock()
        self.cursor = mock.Mock()
        self.collection.__getitem__.return_value = self.cursor
        self.cursor.insert.side_effect = self.mongo_insert
        self.insert_call_args = []

    def tearDown(self):
        # ick ick ick
        readit.mongo.Storage._CONN = None
        self.cursor.reset_mock()

    def assertMongoCollectionWas(self, collection_name):
        self.collection.__getitem__.assert_called_with(collection_name)

    def build_mongo_connection(self, mongo_connection_class_mock):
        self.connection = mongo_connection_class_mock.return_value
        self.connection.readit = self.collection

    def mongo_insert(self, persist_dict):
        self.insert_call_args.append(persist_dict.copy())
        if '_id' not in persist_dict:
            persist_dict['_id'] = ObjectId()


class MongoConnectionTests(MongoTestCase):
    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_opens_connection(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        self.storage.retrieve(self.BIN_NAME, storage_id=self.storage_id,
                clazz=TestStorable)
        mongo_conn_class.assert_called_with(host=None)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_one_opens_connection(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = [{'_id':1}]
        self.storage.retrieve_one(self.BIN_NAME, storage_id=self.storage_id,
                clazz=TestStorable)
        mongo_conn_class.assert_called_with(host=None)

    @mock.patch(CONNECTION_CLASS)
    def test_save_opens_connection(self, mongo_conn_class):
        storable = TestStorable()
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save(self.BIN_NAME, storable)
        mongo_conn_class.assert_called_with(host=None)

    @mock.patch(CONNECTION_CLASS)
    def test_new_connection_uses_storage_url(self, mongo_conn_class):
        self.storage = readit.mongo.Storage('<MongoConnectionUrl>')
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        self.storage.retrieve(self.BIN_NAME, storage_id=self.storage_id,
                clazz=TestStorable)
        mongo_conn_class.assert_called_with(host='<MongoConnectionUrl>')


class MongoRetrieveTests(MongoTestCase):
    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_calls_mongo_find(self, mongo_conn_class):
        args = {'attribute': 'value', 'one': 1}
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        self.storage.retrieve(self.BIN_NAME, storage_id=self.storage_id,
                clazz=TestStorable, **args)
        self.assertMongoCollectionWas(self.BIN_NAME)
        args['_id'] = ObjectId(self.storage_id)
        self.cursor.find.assert_called_with(args)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_one_fails_for_multiple_results(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        # a minimum object includes an _id so we need at least that
        self.cursor.find.return_value = [{'_id':1}, {'_id':2}]
        with self.assertRaises(readit.MoreThanOneResultError):
            self.storage.retrieve_one(self.BIN_NAME,
                    storage_id=self.storage_id, clazz=TestStorable)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_creates_class_instances(self, mongo_conn_class):
        first_object_id, second_object_id = ObjectId(), ObjectId()
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = [
            {'_id': first_object_id, 'name': 'first object'},
            {'_id': second_object_id, 'name': 'second object'},
        ]
        
        result = self.storage.retrieve(self.BIN_NAME,
                storage_id=self.storage_id, clazz=TestStorable)
        
        self.assertMongoCollectionWas(self.BIN_NAME)
        self.cursor.find.assert_called_with({'_id': ObjectId(self.storage_id)})
        self.assertEquals(len(result), 2)
        self.assertEquals(result[0].object_id, str(first_object_id))
        self.assertEquals(result[0].attributes['name'], 'first object')
        self.assertEquals(result[1].object_id, str(second_object_id))
        self.assertEquals(result[1].attributes['name'], 'second object')

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_one_creates_class_instances(self, mongo_conn_class):
        oid = ObjectId()
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = [{'_id': oid, 'name': 'value'}]
        result = self.storage.retrieve_one(self.BIN_NAME,
                storage_id=self.storage_id, clazz=TestStorable)
        self.assertMongoCollectionWas(self.BIN_NAME)
        self.cursor.find.assert_called_with({'_id': ObjectId(self.storage_id)})
        self.assertEquals(result.object_id, str(oid))
        self.assertEquals(result.attributes['name'], 'value')

    @mock.patch(CONNECTION_CLASS)
    def test_retrieving_empty_lists(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        result = self.storage.retrieve(self.BIN_NAME,
                storage_id=self.storage_id)
        self.assertEquals(result, [])
        result = self.storage.retrieve_one(self.BIN_NAME,
                storage_id=self.storage_id)
        self.assertIsNone(result)


class MongoRemoveTests(MongoTestCase):
    @mock.patch(CONNECTION_CLASS)
    def test_filtered_removal(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.remove(self.BIN_NAME, self.storage_id, attribute='value')
        self.assertMongoCollectionWas(self.BIN_NAME)
        self.cursor.remove.assert_called_with({
            'attribute': 'value', '_id': ObjectId(self.storage_id)})

    @mock.patch(CONNECTION_CLASS)
    def test_ignores_specified_objectids(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.remove(self.BIN_NAME, self.storage_id)
        self.assertMongoCollectionWas(self.BIN_NAME)
        self.cursor.remove.assert_called_with({
            '_id': ObjectId(self.storage_id)})


class MongoSaveTests(MongoTestCase):
    @mock.patch(CONNECTION_CLASS)
    def test_save_inserts_data(self, mongo_conn_class):
        instance = TestStorable(attribute='value')
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save(self.BIN_NAME, instance)
        self.assertMongoCollectionWas(self.BIN_NAME)
        self.assertEquals(self.insert_call_args, [{'attribute': 'value'}])
        self.assertIsNotNone(instance.object_id)

    @mock.patch(CONNECTION_CLASS)
    def test_save_use_object_id(self, mongo_conn_class):
        instance = TestStorable(attribute='value')
        instance.object_id = self.storage_id
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save(self.BIN_NAME, instance)
        self.assertMongoCollectionWas(self.BIN_NAME)
        self.assertEquals(self.insert_call_args,
                [{'_id': ObjectId(self.storage_id), 'attribute': 'value'}])
        self.assertEquals(instance.object_id, self.storage_id)


