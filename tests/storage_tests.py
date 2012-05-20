from __future__ import with_statement
import uuid

import readit

from .testing import TestCase


def load_storage_data(storage, storage_bin, storage_id):
    objects = [
            {'name': 'Guido', 'origin': 'Netherlands', 'sign': 'Aquarius'},
            {'name': 'Bjarne', 'origin': 'Denmark', 'sign': 'Capricorn'},
            {'name': 'Larry', 'origin': 'USA', 'sign': 'Libra'},
            {'name': 'Bertrand', 'origin': 'France', 'sign': 'Scorio'},
            {'name': 'Dennis', 'origin': 'USA', 'sign': 'Virgo'},
            ]
    for obj in objects:
        storage.save(storage_bin, storage_id, obj)
    return objects


class StorableItem(readit.StorableItem):
    def __init__(self, ident=None, value=None):
        super(StorableItem, self).__init__('ident', 'value')
        self.ident, self.value = ident, value

    def __repr__(self):
        attributes = []
        for attr in self._PERSIST:
            attributes.append('{0}={1}'.format(attr,
                getattr(self, attr, None)))
        return '<{0} {1}>'.format(self.__class__.__name__,
                ','.join(attributes))


class StorageTests(TestCase):
    def setUp(self):
        super(StorageTests, self).setUp()
        self.storage = readit.Storage()
        self.storage_bin = '<Bin>'
        self.random_id = '<Id {0}>'.format(uuid.uuid4())
        self.items = []
        self.items.append(StorableItem('1', 'one'))
        self.items.append(StorableItem('2', 'two'))
        self.items.append(StorableItem('3', 'three'))
        self.items.append(StorableItem('4', 'four'))

    def test_retrieve_missing_item_returns_default(self):
        value = self.storage.retrieve_one(self.storage_bin, self.random_id,
                default='defaulted value')
        self.assertEquals('defaulted value', value)

    def test_save_and_retrieve(self):
        self.storage.save(self.storage_bin, self.random_id, self.items[0])
        result = self.storage.retrieve_one(self.storage_bin, self.random_id)
        self.assertEquals(self.items[0].to_persistence(), result)

    def test_save_and_retrieve_object(self):
        self.storage.save(self.storage_bin, self.random_id, self.items[0])
        result = self.storage.retrieve_one(self.storage_bin, self.random_id)
        new_item = StorableItem()
        new_item.from_persistence(result)
        self.assertEquals(self.items[0], new_item)

    def test_save_and_retrieve_multiple_values(self):
        for data_pt in self.items:
            self.storage.save(self.storage_bin, self.random_id, data_pt)
        results = self.storage.retrieve(self.storage_bin, self.random_id)
        self.assertEquals(len(self.items), len(results))
        for item in self.items:
            self.assertIn(item.to_persistence(), results)

    def test_multiple_bins(self):
        def fib(n):
            if n < 2:
                return n
            return fib(n - 1) + fib(n - 2)

        def fact(n):
            if n < 2:
                return 1
            return n * fact(n - 1)

        for n in range(1, 10):
            self.storage.save('fib', n, value=fib(n))
            self.storage.save('fact', n, value=fact(n))
        for n in range(1, 10):
            self.assertEquals(fib(n),
                    self.storage.retrieve_one('fib', n)['value'])
            self.assertEquals(fact(n),
                    self.storage.retrieve_one('fact', n)['value'])

    def test_retrieve_one_with_multiple_fails(self):
        multiple_results = [{'one': 1}, {'two': 2}]
        for data in multiple_results:
            self.storage.save(self.storage_bin, self.random_id, **data)
        with self.assertRaises(readit.MoreThanOneResultError):
            self.storage.retrieve_one(self.storage_bin, self.random_id)

    def test_remove_single_item(self):
        self.storage.save(self.storage_bin, self.random_id, self.items[0])
        self.assertEquals(self.items[0].to_persistence(),
                self.storage.retrieve_one(self.storage_bin, self.random_id))
        self.storage.remove_all(self.storage_bin, self.random_id)
        self.assertIsNone(self.storage.retrieve_one(self.storage_bin,
            self.random_id))

    def test_remove_nonexistant_item(self):
        self.storage.remove_all(self.storage_bin, self.random_id)

    def test_remove_multiple(self):
        self.storage.save(self.storage_bin, self.random_id, one=1)
        self.storage.save(self.storage_bin, self.random_id, two=2)
        values = self.storage.retrieve(self.storage_bin, self.random_id)
        self.assertEquals(2, len(values))
        
        self.storage.remove_all(self.storage_bin, self.random_id)
        self.assertIsNone(self.storage.retrieve_one(self.storage_bin,
            self.random_id))

    def test_unqualified_remove_removes_all(self):
        self.storage.save(self.storage_bin, self.random_id, one=1)
        self.storage.save(self.storage_bin, self.random_id, two=2)
        init_values = self.storage.retrieve(self.storage_bin, self.random_id)
        self.assertEquals(2, len(init_values))
        
        self.storage.remove(self.storage_bin, self.random_id)
        final_values = self.storage.retrieve(self.storage_bin, self.random_id)
        self.assertEquals(0, len(final_values))

    def test_remove_one(self):
        objects = [{'one': 1}, {'two': 2}]
        for obj in objects:
            self.storage.save(self.storage_bin, self.random_id, **obj)
        self.storage.remove_one(self.storage_bin, self.random_id, objects[0])
        values = self.storage.retrieve(self.storage_bin, self.random_id)
        self.assertEquals(1, len(values))
        self.assertEquals(objects[1], values[0])

    def test_filtered_retrieval(self):
        objects = load_storage_data(self.storage, self.storage_bin,
                self.random_id)
        results = self.storage.retrieve(self.storage_bin, self.random_id,
                sign='Virgo')
        self.assertEquals(1, len(results))
        self.assertEquals(objects[4], results[0])
        result = self.storage.retrieve_one(self.storage_bin, self.random_id,
                sign='Aquarius')
        self.assertEquals(objects[0], result)

    def test_retrieval_with_factory(self):
        item = StorableItem('<Ident>', '<Value>')
        self.storage.save(self.storage_bin, self.random_id,
                {'ident': item.ident, 'value': item.value})
        results = self.storage.retrieve(self.storage_bin, self.random_id,
                factory=StorableItem)
        self.assertEquals(1, len(results))
        self.assertEquals(item, results[0])
        result = self.storage.retrieve_one(self.storage_bin, self.random_id,
                factory=StorableItem)
        self.assertEquals(item, result)

    def test_filtered_removal(self):
        objects = load_storage_data(self.storage, self.storage_bin,
                self.random_id)
        self.storage.remove(self.storage_bin, self.random_id, origin='USA')
        values = self.storage.retrieve(self.storage_bin, self.random_id)
        self.assertEquals(len(values),
                len(filter(lambda x: x['origin'] != 'USA', objects)))


class StorableItemTests(TestCase):
    def test_identity(self):
        control = StorableItem('<Id>', '<Value>')
        variable = StorableItem()
        variable.from_persistence(control.to_persistence())
        self.assertEquals(control, variable)

    def test_attribute_mismatch_creates_different_objects(self):
        control = StorableItem('<Id>', '<Value>')
        control._PERSIST.append('custom')
        control.custom = '<Custom>'
        variable = StorableItem()
        variable.from_persistence(control.to_persistence())
        self.assertNotEquals(control, variable)

    def test_missing_attribute_results_in_none(self):
        control = StorableItem('<Id>', '<Value>')
        control._PERSIST.append('missing')
        persistent = control.to_persistence()
        self.assertIn('missing', persistent)
        self.assertIsNone(persistent['missing'])

    def test_transient_attributes(self):
        control = StorableItem('<Id>', '<Value>')
        control.transient_attribute = '<Transient>'
        control.from_persistence(control.to_persistence())
        self.assertEquals(control.transient_attribute, '<Transient>')

