from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.protect.authenticator import createToken
from unittest import TestCase
from zExceptions import BadRequest
import json


class TestAjaxUpload(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.file_ = create(
            Builder('file')
            .titled(u'Document')
            .attach_file_containing('My PDF', name=u'test.pdf')
        )

        self.new_file = StringIO('Raw file data')
        self.new_file.filename = u'new_file.txt'
        self.new_file.content_type = u'text/plain'

    def test_replace_file(self):
        self.portal.REQUEST.set('file', self.new_file)
        self.portal.REQUEST.set('_authenticator', createToken())

        ajax_upload_view = self.file_.restrictedTraverse('ajax-upload')
        response = json.loads(ajax_upload_view())
        self.assertEqual(response['success'], True)

        self.new_file.seek(0)
        self.assertEqual(self.file_.file.filename, self.new_file.filename)
        self.assertEqual(self.file_.file.data, self.new_file.read())

    def test_no_file(self):
        with self.assertRaises(BadRequest):
            self.file_.restrictedTraverse('ajax-upload')()

    def test_new_version(self):
        portal = api.portal.get()
        repository_tool = getToolByName(portal, 'portal_repository')
        repository_tool.setVersionableContentTypes('ftw.file.File')

        history = repository_tool.getHistory(self.file_)
        self.assertEqual(0, len(history))

        self.portal.REQUEST.set('file', self.new_file)
        self.portal.REQUEST.set('_authenticator', createToken())
        self.file_.restrictedTraverse('ajax-upload')()

        history = repository_tool.getHistory(self.file_)
        self.assertEqual(1, len(history))
        self.assertEqual(u'File "test.pdf" replaced with "new_file.txt" via drag & drop.',
                         history[0].comment)
