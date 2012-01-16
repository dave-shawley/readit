import doctest, unittest

test_suite = unittest.TestSuite()
test_suite.addTest(doctest.DocTestSuite('readit.reading'))
test_suite.addTest(doctest.DocTestSuite('readit.user'))

