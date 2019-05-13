from ftw.file.interfaces import IFileDownloadedEvent
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser import LIB_TRAVERSAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from StringIO import StringIO
from unittest2 import TestCase
from webdav.common import rfc1123_date
from zope.component import eventtesting
from zope.component import queryMultiAdapter
import AccessControl
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

    def tearDown(self):
        super(TestFileDownload, self).tearDown()
        eventtesting.clearEvents()

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
        self.index_html()
        events = [e for e in eventtesting.getEvents()
                  if IFileDownloadedEvent.providedBy(e)]
        self.assertEqual(1, len(events))

    def test_file_download_no_notification_when_system(self):
        _original_security = AccessControl.getSecurityManager()

        _system_user = AccessControl.SecurityManagement.SpecialUsers.system
        AccessControl.SecurityManagement.newSecurityManager(None, _system_user)
        self.index_html()
        events = [e for e in eventtesting.getEvents()
                  if IFileDownloadedEvent.providedBy(e)]
        self.assertEqual(0, len(events))
        AccessControl.SecurityManagement.setSecurityManager(
            _original_security)
        _original_security = None

    @browsing
    def test_inline_download(self, browser):
        browser.login().visit(self.context, view='@@download')
        self.assertEquals('attachment; filename="file.doc"; filename=file.doc*=UTF-8',
                          browser.headers['content-disposition'])

        browser.visit(self.context, view='@@download?inline=true')
        self.assertEquals('inline; filename="file.doc"; filename=file.doc*=UTF-8',
                          browser.headers['content-disposition'])

    @browsing
    def test_head_request(self, browser):
        browser.default_driver = LIB_TRAVERSAL

        browser.login()

        # Accessing "@@download" on the file would normally result in a 302,
        # telling us to go to "@@download/file/file.doc" instead.
        # But since the testbrowser follows the redirects, we get a 200 instead.
        browser.open(self.context, view='@@download', method='HEAD')
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'http://nohost/plone/f1/@@download/file/file.doc',
            browser.url
        )

        # Open the correct url used to access the file.
        browser.open(self.context, view='@@download/file/file.doc', method='HEAD')
        self.assertEqual('200 Ok', browser.headers['status'])
        self.assertEqual('6170', browser.headers['content-length'])
        self.assertEqual('attachment; filename="file.doc"; filename=file.doc*=UTF-8',
                         browser.headers['content-disposition'])
        self.assertEqual('bytes', browser.headers['accept-ranges'])
        self.assertEqual('application/msword', browser.headers['content-type'])


class TestFileDownloadView(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.file = StringIO(1234 * 'dummy')
        setattr(self.file, 'filename', 'file.doc')
        self.portal.invokeFactory('File', 'f1', file=self.file)
        self.context = self.portal.f1

        # Patch our index_html method for simpler testing
        def index_html(self, *args, **kwargs):
            return 'My index_html'
        field = self.context.getField('file')
        self.index_html_orig = field.index_html
        field.index_html = index_html.__get__(field, field.__class__)

    def tearDown(self):
        # Revert patch
        field = self.context.getField('file')
        field.index_html = self.index_html_orig

    def test_download_view_uses_our_index_html(self):
        view = queryMultiAdapter((self.context, self.layer['request']),
                                 name=u'download')
        view.fieldname = 'file'
        self.assertEqual('My index_html', view())
