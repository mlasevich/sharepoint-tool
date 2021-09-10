"""
Unit Tests for utils
"""
import os
import unittest

from sp_tool.sharepoint import url


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TENANT = "tenant"
SITE = "site"


class SharepointURLTests(unittest.TestCase):
    """ Unit Tests for sp_tool.sharepoint.url"""

    def setUp(self):
        """ Setup """
        self.url = url.SharepointURL(TENANT, SITE)
        self.url_no_site = url.SharepointURL(TENANT, None)

    def test_site_uri_site(self):
        """ Check site_uri if site is declared """
        self.assertEqual(self.url.site_uri, f"/sites/{SITE}")

    def test_site_uri_no_site(self):
        """ Check site_uri if site is not declared """
        self.assertEqual(self.url_no_site.site_uri, "/")

    def test_host_site(self):
        """ test url.host"""
        self.assertEqual(self.url.host, f"{TENANT}.sharepoint.com")

    def test_host_no_site(self):
        """ test url.host"""
        self.assertEqual(self.url_no_site.host, f"{TENANT}.sharepoint.com")


if __name__ == '__main__':
    unittest.main()
