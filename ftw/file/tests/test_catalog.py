from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestCatalog(TestCase):
    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.catalog = getToolByName(self.layer['portal'], 'portal_catalog')

    def test_getCategoryUids_index_registered(self):
        self.assertIn('documentDate', self.catalog.indexes())

    def test_getCategoryUids_metadata_registered(self):
        self.assertIn('documentDate', self.catalog.schema())
