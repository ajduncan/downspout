#!/usr/bin/env python

import unittest

from downspout.utils import *


class UtilsTest(unittest.TestCase):

    def setUp(self):
        foo
        self.filename = "herp!@%$!%# derp.ext"

    def test_safe_filename(self):
        self.assertEqual(safe_filename(self.filename), "herp_derp.ext")
