from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.file.bumblebee.interfaces import IFilePreviewFileInfoCollector
from ftw.file.testing import FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getMultiAdapter


class FileInfoCollectorBaseTest(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])


class TestMimetypeAndFilesize(FileInfoCollectorBaseTest):

    def test_values_are_correct(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_mimetype_and_filesize()

        self.assertEqual('PDF document', action.get('leftcolumn'))
        self.assertEqual('12.0 B', action.get('rightcolumn'))


class TestFilename(FileInfoCollectorBaseTest):

    def test_filename_is_correct(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='chucknorris.pdf'))

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_filename()

        self.assertEqual('Filename:', action.get('leftcolumn'))
        self.assertEqual('chucknorris.pdf', action.get('rightcolumn'))


class TestModificationDate(FileInfoCollectorBaseTest):

    def test_modification_date_is_correct(self):
        modified_date = DateTime('10.05.2015 10:25')
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        dummyfile.setModificationDate(modified_date)

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_modified_date()

        self.assertEqual('Modified:', action.get('leftcolumn'))
        self.assertEqual(u'Oct 05, 2015 10:25 AM', action.get('rightcolumn'))


class TestDocumentDate(FileInfoCollectorBaseTest):

    def test_document_date_is_correct(self):
        document_date = DateTime('10.05.2015 10:25')
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf')
            .having(documentDate=document_date))

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_document_date()

        self.assertEqual('Documentdate:', action.get('leftcolumn'))
        self.assertEqual(u'Oct 05, 2015', action.get('rightcolumn'))


class TestDescription(FileInfoCollectorBaseTest):

    def test_return_empty_list_if_no_description_is_available(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_description()

        self.assertEqual({}, action)

    def test_description_is_correct_if_it_exists(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf')
            .having(description="Chuck is the best"))

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_description()

        self.assertEqual('Description:', action.get('leftcolumn'))
        self.assertEqual(u'Chuck is the best', action.get('rightcolumn'))


class TestAuthor(FileInfoCollectorBaseTest):

    def test_do_not_show_author_if_show_author_returns_false(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))

        site_props = getToolByName(
            self.portal, 'portal_properties').site_properties
        site_props.allowAnonymousViewAbout = False
        logout()

        # self.portal.portal_properties.
        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_author()

        self.assertEqual({}, action)

    def test_return_author_name_if_author_url_is_not_available(self):
        api.user.create(
            email='chuck@norris.org',
            username='chuck',
            properties={'fullname': 'Chuck Norris'})
        setRoles(self.portal, 'chuck', ['Manager'])

        logout()
        login(self.portal, 'chuck')

        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))

        logout()
        login(self.portal, TEST_USER_NAME)
        api.user.delete(username='chuck')

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_author()

        self.assertEqual('Author:', action.get('leftcolumn'))
        self.assertEqual('chuck', action.get('rightcolumn'))

    def test_return_author_name_as_a_link_if_author_url_is_available(self):
        api.user.create(
            email='chuck@norris.org',
            username='chuck',
            properties={'fullname': 'Chuck Norris'})
        setRoles(self.portal, 'chuck', ['Manager'])

        logout()
        login(self.portal, 'chuck')

        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))

        logout()
        login(self.portal, TEST_USER_NAME)

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewFileInfoCollector)
        action = adapter._data_author()

        self.assertEqual('Author:', action.get('leftcolumn'))
        self.assertEqual(
            "<a href='http://nohost/plone/author/chuck'>Chuck Norris</a>",
            action.get('rightcolumn'))
