#!/usr/bin/env python

import unittest


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for all_tests in unittest.defaultTestLoader.discover('tests/', pattern='*_test.py'):
        for test_suite in all_tests:
            suite.addTests(test_suite)
    return suite


if __name__ == '__main__':
    unittest.main()
