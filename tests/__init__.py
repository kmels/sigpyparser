import unittest
from . import fx_test

def fx_tests_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(fx_test)
    return suite
