import unittest
from . import fx_test
from . import *

def fx_tests_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(fx_test)
    return suite

def outcome_tests_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOutcome)
    unittest.TextTestRunner(verbosity=2).run(suite)

def signal_tests_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSignal)
    unittest.TextTestRunner(verbosity=2).run(suite)
