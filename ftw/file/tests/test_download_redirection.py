from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testing import browser
from ftw.testing.pages import Plone
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from unittest2 import TestCase


class TestDownloadRedirection(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser('reader', TEST_USER_PASSWORD,
                                    ['Reader'], [])
        acl_users.userFolderAddUser('contributor', TEST_USER_PASSWORD,
                                    ['Contributor'], [])

        login(portal, 'contributor')

    def test_redirects_to_details_view_when_i_can_edit(self):
        obj = create(Builder('file'))
        Plone().login('contributor')

        browser().visit(obj.absolute_url())

        self.assertEquals('http://nohost/plone/file/view',
                          browser().url)

    def test_redirects_to_download_when_i_cannot_edit(self):
        obj = create(Builder('file'))
        Plone().login('reader')

        browser().visit(obj.absolute_url())

        self.assertEquals('http://nohost/plone/file/download',
                          browser().url)
