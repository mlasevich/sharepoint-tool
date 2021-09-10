"""
Unit Tests for utils
"""
import os
import unittest

from sp_tool.sharepoint import utils

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class SharepointUtilsTests(unittest.TestCase):
    """ Unit Tests for sp_tool.sharepoint.utils"""

    def setUp(self):
        """ Setup """

    def test_urlencode(self):
        """ utils.urlencode() """
        tests = [
            ('', ''),
            (' ', '%20'),
            ('$ & < > ? ; # : = , " \' + %',
             '%24%20%26%20%3C%20%3E%20%3F%20%3B%20%23%20%3A%20%3D%20%2C%20%22'
             '%20%27%20%2B%20%25')
        ]
        for source, expected in tests:
            actual = utils.urlencode(source)
            self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
