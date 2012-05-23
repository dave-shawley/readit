import os
import uuid

from pymongo.objectid import ObjectId

import mock
from .testing import TestCase

import readit.mongo


import distutils.version
mock_version = distutils.version.LooseVersion(mock.__version__)
if mock_version < '0.8.0':
    raise ImportError('this test requires at least mock 0.8')

# flask.g.db.retrieve_one('users', email=response.email)
# flask.g.db.retrieve('readings', flask.g.user.user_id, factory=readit.Reading)
# flask.g.db.save('readings', flask.g.user.user_id, reading)
# flask.g.db.remove('readings', flask.g.user.user_id, _id=reading_id)



CONNECTION_CLASS = 'pymongo.Connection'


class MongoTestCase(TestCase):
    BIN_NAME = '<Bin>'

    def setUp(self):
        self.storage_id = ''.join(('{:02x}'.format(ord(x))
                                        for x in os.urandom(12)))
        self.storage = readit.mongo.Storage()
        self.collection = mock.MagicMock()
        self.cursor = mock.Mock()
        self.collection.__getitem__.return_value = self.cursor

    def tearDown(self):
        # ick ick ick
        readit.mongo.Storage._CONN = None

    def build_mongo_connection(self, mongo_connection_class_mock):
        self.connection = mongo_connection_class_mock.return_value
        self.connection.readit = self.collection


class MongoConnectionTests(MongoTestCase):

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_opens_connection(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        self.storage.retrieve(self.BIN_NAME)
        mongo_conn_class.assert_called_with(host=None)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_one_opens_connection(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        self.storage.retrieve_one(self.BIN_NAME, storage_id=self.storage_id)
        mongo_conn_class.assert_called_with(host=None)

    @mock.patch(CONNECTION_CLASS)
    def test_save_opens_connection(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save(self.BIN_NAME, storage_id=self.storage_id,
                pi=(22.0 / 7.0))
        mongo_conn_class.assert_called_with(host=None)

    @mock.patch(CONNECTION_CLASS)
    def test_new_connection_uses_storage_url(self, mongo_conn_class):
        self.storage = readit.mongo.Storage('<MongoConnectionUrl>')
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        self.storage.retrieve(self.BIN_NAME, self.storage_id)
        mongo_conn_class.assert_called_with(host='<MongoConnectionUrl>')


class MongoRetrieveTests(MongoTestCase):

    def setUp(self):
        super(MongoRetrieveTests, self).setUp()
        self.test_value = {'<Attribute>': '<Value>'}

    def adjust_test_value(self):
        """Adds _id=self.storage_id to self.test_value."""
        self.test_value['_id'] = ObjectId(self.storage_id)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_calls_mongo_find(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = []
        self.storage.retrieve(self.BIN_NAME, self.storage_id, **self.test_value)
        self.adjust_test_value()
        self.cursor.find.assert_called_with(**self.test_value)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_with_factory(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        factory = mock.Mock()
        instance = factory.return_value
        self.cursor.find.return_value = [self.test_value]
        self.storage.retrieve(self.BIN_NAME, self.storage_id, factory=factory)
        self.adjust_test_value()
        instance.from_persistence.assert_called_with(self.test_value)

    @mock.patch(CONNECTION_CLASS)
    def test_retrieve_one_fails_for_multiple_results(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.cursor.find.return_value = [1, 2, 3]
        with self.assertRaises(readit.MoreThanOneResultError):
            self.storage.retrieve_one(self.BIN_NAME,
                    storage_id=self.storage_id)


class MongoRemoveTests(MongoTestCase):

    @mock.patch(CONNECTION_CLASS)
    def test_filtered_removal(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.remove(self.BIN_NAME, self.storage_id, attribute='value')
        self.cursor.remove.assert_called_with({
            'attribute': 'value', '_id': ObjectId(self.storage_id)})

    @mock.patch(CONNECTION_CLASS)
    def test_ignores_specified_objectids(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.remove(self.BIN_NAME, self.storage_id)
        self.cursor.remove.assert_called_with({
            '_id': ObjectId(self.storage_id)})


class MongoSaveTests(MongoTestCase):

    @mock.patch(CONNECTION_CLASS)
    def test_save_inserts_data(self, mongo_conn_class):
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save(self.BIN_NAME, storage_id=self.storage_id,
                storable={'<Attribute>': '<Value>'})
        self.cursor.insert.assert_called_with({
            '<Attribute>': '<Value>', '_id': ObjectId(self.storage_id)})

    @mock.patch(CONNECTION_CLASS)
    def test_save_uses_id_extractor(self, mongo_conn_class):
        def get_name(an_object):
            return an_object['name']
        mongo_id = '{:024x}'.format(hash('Dave'))
        self.build_mongo_connection(mongo_conn_class)
        self.storage = readit.mongo.Storage(id_extractor=get_name)
        self.storage.save(self.BIN_NAME, name='Dave', age=37)
        self.cursor.insert.assert_called_with({
            'name': 'Dave', 'age': 37, '_id': ObjectId(mongo_id)})

    @mock.patch(CONNECTION_CLASS)
    def test_uuid_is_valid_object_id(self, mongo_conn_class):
        self.storage_id = uuid.uuid4()
        vals = str(self.storage_id).split('-')
        expected_oid = vals[0] + vals[3] + vals[4]
        self.build_mongo_connection(mongo_conn_class)
        self.storage.save(self.BIN_NAME, storage_id=self.storage_id,
                storable={'<Attribute>': '<Value>'})
        self.cursor.insert.assert_called_with({
            '<Attribute>': '<Value>', '_id': ObjectId(expected_oid)})

