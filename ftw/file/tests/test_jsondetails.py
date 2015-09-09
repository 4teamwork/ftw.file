from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.TinyMCE.adapters.interfaces.JSONDetails import IJSONDetails
from unittest2 import TestCase
import json


class TestJsondetails(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
        self.file = create(Builder('file'))

    def test_jsondetails(self):
        details = IJSONDetails(self.file).getDetails()
        details = json.loads(details)
        self.assertEquals('file', details['title'])
