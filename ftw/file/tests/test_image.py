from unittest2 import TestCase
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from StringIO import StringIO
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
import os


class TestIsImage(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_isimage(self):
        file_data = open("%s/assets/transparent.gif" % os.path.split(__file__)[0], 'r')
        file_ = self.portal.get(self.portal.invokeFactory('File', 'myfile', file=file_data))
        self.assertTrue(file_.is_image())

    def test_isnotimage(self):
        file_data = StringIO('blubber blubb')
        file_ = self.portal.get(self.portal.invokeFactory('File', 'myfile', file=file_data))
        self.assertFalse(file_.is_image())
