from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest import TestCase


class TestIsImage(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_isimage(self):
        file_ = create(Builder('file')
                       .titled(u'Some title')
                       .attach_asset(u'transparent.gif'))

        self.assertTrue(file_.is_image())

    def test_isnotimage(self):
        file_ = create(Builder('file')
                       .titled(u'Some title')
                       .attach_asset(u'test.pdf'))

        self.assertFalse(file_.is_image())

    def test_ioerror(self):
        """Check if IOError isn't raised when PIL can't open the file.
            This applies to filetype where we only need libaries in some cases
            and broken images.
        """
        file_ = create(Builder('file')
                       .titled(u'Some title')
                       .attach_asset(u'CCITT_1.TIF'))

        self.assertTrue(file_.is_image())
        view = file_.restrictedTraverse('@@file_view')
        self.assertFalse(view.get_image_tag())
