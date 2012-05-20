import os
import os.path


def load_tests(loader, standard_tests, pattern):
    this_dir = os.path.dirname(__file__)
    parent_dir = os.path.normpath(os.path.join(this_dir, os.path.pardir))
    tests = loader.discover(start_dir=this_dir, pattern='*_tests.py',
            top_level_dir=parent_dir)
    standard_tests.addTests(tests)
    return standard_tests

load_tests.__test__ = False

