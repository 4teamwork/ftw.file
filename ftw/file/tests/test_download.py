from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.file.interfaces import IFileDownloadedEvent
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from StringIO import StringIO
from unittest2 import TestCase
from webdav.common import rfc1123_date
from zope.component import eventtesting
import transaction


class TestFileDownload(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.file = StringIO(1234 * 'dummy')
        setattr(self.file, 'filename', 'file.doc')
        self.portal.invokeFactory('File', 'f1', file=self.file)
        self.context = self.portal.f1

        # We need a modification date in ._p_mtime
        transaction.commit()

    def index_html(self, disposition='attachment'):
        request = self.layer['request']
        response = request.RESPONSE
        return self.context.getField('file').index_html(self.context,
            REQUEST=request, RESPONSE=response, disposition=disposition)


    def test_content_length_header(self):
        self.index_html()
        response = self.layer['request'].RESPONSE
        self.assertEqual(
            '6170',
            response.getHeader('Content-Length')
        )

    def test_handle_if_modified_since_requests(self):
        self.layer['request'].environ.update({
            'HTTP_IF_MODIFIED_SINCE': rfc1123_date(self.context._p_mtime+1)
        })
        self.index_html()
        response = self.layer['request'].RESPONSE
        self.assertEqual(304, response.getStatus())

    def test_handle_range_requests(self):
        self.layer['request'].environ.update({'HTTP_RANGE': 'bytes=0-'})
        self.index_html()
        response = self.layer['request'].RESPONSE
        self.assertEqual(206, response.getStatus())
        self.assertEqual(
            'bytes 0-6169/6170',
            response.getHeader('Content-Range'))

    def test_download_returns_stream_iterator(self):
        self.assertEqual(self.file.getvalue(),self.index_html().next())

    def test_file_download_notification(self):
        eventtesting.setUp()
        self.index_html()
        events = [e for e in eventtesting.getEvents()
                  if IFileDownloadedEvent.providedBy(e)]
        self.assertEqual(1, len(events))
