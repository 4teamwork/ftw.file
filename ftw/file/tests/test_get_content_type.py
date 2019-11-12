from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest import TestCase


class TestContentType(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_get_content_type(self):
        file_ = create(Builder('file')
                       .titled(u'Some title')
                       .attach_asset(u'transparent.gif'))
        self.assertTrue('image/gif', file_.getContentType())

        file_ = create(Builder('file')
                       .titled(u'Some title')
                       .attach_asset(u'transparent.gif'))
        self.assertTrue('application/pdf', file_.getContentType())

    def test_get_content_type_fallback(self):
        file_ = create(Builder('file')
                       .titled(u'Some title')
                       .attach_asset(u'testfile.NonsenseExtension'))
        self.assertTrue('application/octet-stream', file_.getContentType())
