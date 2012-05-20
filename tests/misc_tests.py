import warnings

import readit.helpers

from .testing import TestCase


class MiscellaneousTests(TestCase):
    def test_deprecation_decorator(self):
        @readit.helpers.deprecated
        def func():
            pass
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('default')
            func()
            self.assertEquals(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))

