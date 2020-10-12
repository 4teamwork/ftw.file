from ftw.builder import Builder
from ftw.builder import create
from ftw.file.interfaces import IFileDownloadedEvent
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser import LIB_MECHANIZE
from ftw.testbrowser import LIB_REQUESTS
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from unittest import TestCase
from webdav.common import rfc1123_date
from zope.component import eventtesting
from zope.component import getMultiAdapter
import AccessControl


class TestFileDownload(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.file = NamedBlobFile(data=1234 * 'dummy',
                                  filename=u'file.doc')
        self.context = create(Builder('file').having(file=self.file))

    def tearDown(self):
        super(TestFileDownload, self).tearDown()
        eventtesting.clearEvents()

    def get_response(self, request=None):
        if request is None:
            request = self.context.REQUEST

        view = getMultiAdapter((self.context, request), name='download')
        view()
        return view.request.response

    def test_content_length_header(self):
        response = self.get_response()
        self.assertEqual(
            '6170',
            response.getHeader('Content-Length')
        )

    def test_handle_if_modified_since_requests(self):
        self.layer['request'].environ.update({
            'HTTP_IF_MODIFIED_SINCE': rfc1123_date(self.context._p_mtime + 1)
        })
        response = self.get_response()
        self.assertEqual(304, response.getStatus())

    def test_handle_range_requests(self):
        self.layer['request'].environ.update({'HTTP_RANGE': 'bytes=0-'})
        response = self.get_response()
        self.assertEqual(206, response.getStatus())
        self.assertEqual(
            'bytes 0-6169/6170',
            response.getHeader('Content-Range'))

    def test_download_returns_stream_iterator(self):
        content = self.context.restrictedTraverse('@@download')()
        self.assertEqual(self.file.data, content.next())

    def test_file_download_notification_for_non_system_users(self):
        events = []
        self.portal.getSiteManager().registerHandler(
            events.append, (IFileDownloadedEvent,))
        self.assertEqual(0, len(events))
        self.get_response()
        self.assertEqual(
            1, len(events),
            'The downloaded event should fire for non system users.')

        system_user = AccessControl.SecurityManagement.SpecialUsers.system
        AccessControl.SecurityManagement.newSecurityManager(None, system_user)
        self.get_response()
        self.assertEqual(
            1, len(events),
            'No event should fire for system users')

    @browsing
    def test_inline_download(self, browser):
        browser.login().visit(self.context, view='@@download')
        self.assertEquals('attachment; filename="file.doc"; filename*=UTF-8\'\'file.doc',
                          browser.headers['content-disposition'])

        browser.open(self.context.absolute_url() + '/@@download?inline=true')
        self.assertEquals('inline; filename="file.doc"; filename*=UTF-8\'\'file.doc',
                          browser.headers['content-disposition'])

    @browsing
    def test_head_request(self, browser):
        browser.default_driver = LIB_REQUESTS

        browser.login()

        # Accessing "@@download" on the file would normally result in a 302,
        # telling us to go to "@@download/file/file.doc" instead.
        # But since the testbrowser follows the redirects, we get a 200 instead.
        browser.open(self.context, view='@@download', method='HEAD')
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            '{}/file.doc/@@download/file/file.doc'.format(self.portal_url),
            browser.url
        )

        # Open the correct url used to access the file.
        browser.open(self.context, view='@@download/file/file.doc', method='HEAD')
        self.assertEqual('200 Ok', browser.headers['status'])
        self.assertEqual('6170', browser.headers['content-length'])
        self.assertEqual('attachment; filename="file.doc"; filename*=UTF-8\'\'file.doc',
                         browser.headers['content-disposition'])
        self.assertEqual('bytes', browser.headers['accept-ranges'])
        self.assertEqual('application/msword', browser.headers['content-type'])
        browser.default_driver = LIB_MECHANIZE

    @browsing
    def test_redirect_as_anonymous_user_with_umlauts(self, browser):
        browser.default_driver = LIB_REQUESTS
        blob = NamedBlobFile(data=1234 * 'dummy',
                             filename=u'\xfcber\xe2\x80\x93uns.doc')
        self.context = create(Builder('file')
                              .having(file=blob))

        browser.logout()

        browser.visit(self.context.absolute_url())
        self.assertEquals('200 Ok', browser.headers['status'])
        self.assertEquals(
            '{}/uberauns.doc/@@download/file/%C3%BCber%C3%A2%C2%80%C2%93uns.doc'.format(self.portal_url),
            browser.url
        )
        browser.default_driver = LIB_MECHANIZE
