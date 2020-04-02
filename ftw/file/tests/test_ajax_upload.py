import json
from StringIO import StringIO
from Products.ATContentTypes.interfaces import IATFile
from Products.CMFCore.utils import getToolByName

from ftw.builder import Builder
from ftw.builder import create
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import TestCase

from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING


class TestAjaxUpload(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.file_ = create(
            Builder('file')
                .titled('Document')
                .attach_file_containing('My PDF', name='test.pdf')
        )

        self.new_file = StringIO('Raw file data')
        self.new_file.filename = 'new_file.txt'
        self.new_file.content_type = 'text/plain'

    def test_replace_file(self):
        self.portal.REQUEST.set('file', self.new_file)

        ajax_upload_view = self.file_.restrictedTraverse('ajax-upload')
        response = json.loads(ajax_upload_view())

        self.assertEqual(response['success'], True)
        replaced_file = IATFile(self.portal['document']).getFile()
        self.assertEqual(replaced_file.filename, 'new_file.txt')
        self.assertEqual(replaced_file.data, 'Raw file data')

    def test_empty_file(self):
        """ Archetypes validator should stop updates with an empty file """
        empty_file = StringIO('')
        empty_file.filename = 'empty_file.txt'
        empty_file.content_type = 'text/plain'
        self.portal.REQUEST.set('file', empty_file)

        ajax_upload_view = self.file_.restrictedTraverse('ajax-upload')
        response = json.loads(ajax_upload_view())

        self.assertFalse(response['success'])
        self.assertIn('Uploaded file is empty',
                      response['errors'][0]['message'])

    def test_no_file(self):
        ajax_upload_view = self.file_.restrictedTraverse('ajax-upload')
        response = json.loads(ajax_upload_view())

        self.assertFalse(response['success'])
        self.assertEqual('No content provided.',
                         response['errors'][0]['message'])

    def test_new_version(self):
        portal = api.portal.get()
        repository_tool = getToolByName(portal, 'portal_repository')
        repository_tool.setVersionableContentTypes('File')

        self.portal.REQUEST.set('file', self.new_file)
        self.file_.restrictedTraverse('ajax-upload')()

        history = repository_tool.getHistory(self.file_)
        self.assertEqual(1, len(history))
        replaced_file = IATFile(self.portal['document']).getFile()
        self.assertEqual(replaced_file.filename, 'new_file.txt')
        self.assertEqual(replaced_file.data, 'Raw file data')
