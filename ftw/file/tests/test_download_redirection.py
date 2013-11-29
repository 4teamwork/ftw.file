from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testing import browser
from ftw.testing.pages import Plone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
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
        obj = create(Builder('file')
                     .with_dummy_content())
        Plone().login('reader')

        browser().visit(obj.absolute_url())

        self.assertEquals(
            'http://nohost/plone/file/@@download/file/test.doc',
            browser().url)



class TestDownloadRedirectToURLWithFilename(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

    def test_download_view_redirects_to_url_with_filename(self):
        obj = create(Builder('file')
                     .titled('Document')
                     .attach_file_containing('PDF CONTENT', name='doc.pdf'))

        Plone().login().visit(obj, '@@download')

        self.assertEquals(
            'http://nohost/plone/document/@@download/file/doc.pdf',
            browser().url)

        self.assertEquals('PDF CONTENT', browser().html)

    def test_download_method_redirects_to_url_with_filename(self):
        obj = create(Builder('file')
                     .titled('Document')
                     .attach_file_containing('PDF CONTENT', name='doc.pdf'))

        Plone().login().visit(obj, 'download')

        self.assertEquals(
            'http://nohost/plone/document/@@download/file/doc.pdf',
            browser().url)

        self.assertEquals('PDF CONTENT', browser().html)

    def test_supports_special_characters_and_umlauts_in_filename(self):
        obj = create(
            Builder('file')
            .titled('Document')
            .attach_file_containing(
                'PDF CONTENT',
                name='w\xc3\xb6rter & bilder.pdf'))

        Plone().login().visit(obj, 'download')

        self.assertEquals(
            'http://nohost/plone/document/@@download/' + \
                'file/w%C3%B6rter%20%26%20bilder.pdf',
            browser().url)

        self.assertEquals('PDF CONTENT', browser().html)

    def test_supports_unicode_special_characters_in_filename(self):
        obj = create(
            Builder('file')
            .titled('Document')
            .attach_file_containing(
                'PDF CONTENT',
                name='w\xc3\xb6rter & bilder.pdf'.decode('utf-8')))

        Plone().login().visit(obj, 'download')

        self.assertEquals(
            'http://nohost/plone/document/@@download/' + \
                'file/w%C3%B6rter%20%26%20bilder.pdf',
            browser().url)

        self.assertEquals('PDF CONTENT', browser().html)

    def test_remove_percent_signs_form_filename(self):
        obj = create(
            Builder('file')
            .titled('Document')
            .attach_file_containing(
                'PDF CONTENT',
                name='50%to80%.pdf'.decode('utf-8')))

        Plone().login().visit(obj, 'download')

        self.assertEquals(
            'http://nohost/plone/document/@@download/' + \
                'file/50to80.pdf',
            browser().url)

        self.assertEquals('PDF CONTENT', browser().html)