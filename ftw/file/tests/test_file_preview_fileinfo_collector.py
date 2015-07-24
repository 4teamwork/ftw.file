from ftw.builder import Builder
from ftw.builder import create
from ftw.file.interfaces import IFilePreviewFileInfoCollector
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from zope.component import getMultiAdapter
from DateTime import DateTime


class FileInfoCollectorBaseTest(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())
        self.view = self.dummyfile.unrestrictedTraverse('@@file_preview')
        self.adapter = getMultiAdapter(
            (self.dummyfile, self.view), IFilePreviewFileInfoCollector)


class TestMimetypeAndFilesize(FileInfoCollectorBaseTest):

    def test_values_are_correct(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_mimetype_and_filesize()

        self.assertEqual('PDF document', action.get('leftcolumn'))
        self.assertEqual('12.0 B', action.get('rightcolumn'))


class TestFilename(FileInfoCollectorBaseTest):

    def test_filename_is_correct(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='chucknorris.pdf'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_filename()

        self.assertEqual('Filename:', action.get('leftcolumn'))
        self.assertEqual('chucknorris.pdf', action.get('rightcolumn'))


class TestModificationDate(FileInfoCollectorBaseTest):

    def test_modification_date_is_correct(self):
        modified_date = DateTime('10.05.2015 10:25')
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        dummyfile.setModificationDate(modified_date)
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_modified_date()

        self.assertEqual('Modified:', action.get('leftcolumn'))
        self.assertEqual(u'Oct 05, 2015 10:25 AM', action.get('rightcolumn'))


class TestDocumentDate(FileInfoCollectorBaseTest):

    def test_document_date_is_correct(self):
        document_date = DateTime('10.05.2015 10:25')
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf')
            .having(documentDate=document_date))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_document_date()

        self.assertEqual('Documentdate:', action.get('leftcolumn'))
        self.assertEqual(u'Oct 05, 2015', action.get('rightcolumn'))


class TestDescription(FileInfoCollectorBaseTest):

    def test_return_empty_list_if_no_description_is_available(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_description()

        self.assertEqual({}, action)

    def test_description_is_correct_if_it_exists(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf')
            .having(description="Chuck is the best"))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_description()

        self.assertEqual('Description:', action.get('leftcolumn'))
        self.assertEqual(u'Chuck is the best', action.get('rightcolumn'))


class TestAuthor(FileInfoCollectorBaseTest):

    def test_do_not_show_author_if_show_author_returns_false(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        view.show_author = lambda: False

        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_author()

        self.assertEqual({}, action)

    def test_return_author_name_if_author_url_is_not_available(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        view.get_author = lambda: {'url': '', 'name': 'Chuck Norris'}

        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_author()

        self.assertEqual('Author:', action.get('leftcolumn'))
        self.assertEqual('Chuck Norris', action.get('rightcolumn'))

    def test_return_author_name_as_a_link_if_author_url_is_available(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        view.get_author = lambda: {'url': 'url-to-author',
                                   'name': 'Chuck Norris'}

        adapter = getMultiAdapter(
            (dummyfile, view), IFilePreviewFileInfoCollector)
        action = adapter._data_author()

        self.assertEqual('Author:', action.get('leftcolumn'))
        self.assertEqual(
            "<a href='url-to-author'>Chuck Norris</a>",
            action.get('rightcolumn'))
