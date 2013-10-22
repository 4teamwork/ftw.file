from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from unittest2 import TestCase
import os
from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login, setRoles


class TestFileName(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.file_ = open("%s/testfile.NonsenseExtension" % os.path.split(__file__)[0], 'r')
        mtr = getToolByName(self.portal, 'mimetypes_registry')
        mtr.manage_addMimeType('customimage type', ['image/x-custom-image'], ['NonsenseExtension'], 'customicon.png')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        
    def test_custom_icon(self):
        plonefile = self.portal.get(self.portal.invokeFactory('File', 'myfile', file=self.file_))
        self.assertEqual('plone/customicon.png', plonefile.getIcon())