from ftw.builder import Builder
from ftw.builder import create
from ftw.file.bumblebee.interfaces import IFilePreviewJournal
from ftw.file.testing import FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestFilePreviewJournal(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.pr = getToolByName(self.portal, 'portal_repository')

    def test_return_empty_list_if_nothing_is_journalized(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewJournal)

        self.assertEqual(
            [], adapter.get_journal())

    def test_return_an_item_for_each_entry(self):
        self.pr.setVersionableContentTypes('File')
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        self.pr.save(dummyfile, comment="Title changed")
        self.pr.save(dummyfile, comment="Description changed")

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewJournal)

        self.assertEqual(2, len(adapter.get_journal()))

    def test_journal_items_has_the_correct_format(self):
        self.pr.setVersionableContentTypes('File')
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        self.pr.save(dummyfile, comment="Title changed")

        adapter = getMultiAdapter(
            (dummyfile, self.request), IFilePreviewJournal)

        self.assertEqual(
            sorted(
                [
                    'time',
                    'relative_time',
                    'action',
                    'actor',
                    'comment',
                    'downloadable_version',
                    'version_id',
                    'version_preview_image_url']),
            sorted(adapter()[0].keys()))
