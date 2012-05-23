from __future__ import with_statement
import uuid

import readit

from .testing import TestCase, skipped


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

def load_storag_data(storage, bin):
    objects = [
            {'name': 'Guido', 'origin': 'Netherlands', 'sign': 'Aquarius'},
            {'name': 'Bjarne', 'origin': 'Denmark', 'sign': 'Capricorn'},
            {'name': 'Larry', 'origin': 'USA', 'sign': 'Libra'},
            {'name': 'Bertrand', 'origin': 'France', 'sign': 'Scorio'},
            {'name': 'Dennis', 'origin': 'USA', 'sign': 'Virgo'},
            ]
    for obj in objects:
        storage.save(bin, storable=obj)
    return objects

def extract_name(data_object):
    return data_object['name']


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

