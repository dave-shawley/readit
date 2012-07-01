from __future__ import with_statement
import uuid

import readit

from .testing import TestCase, skipped


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

