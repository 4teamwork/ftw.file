from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from StringIO import StringIO
from unittest2 import TestCase
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse


class TestFileName(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('File', 'f1')
        self.context = self.portal.f1

    def get_response_for(self, filename='foo.pdf', response=HTTPResponse(),
                         request=None):
        if not request:
            request = HTTPRequest('', dict(HTTP_HOST='nohost:8080'),
                                  {}, response)
        self.set_filedata(filename)
        self.context.getField('file').index_html(self.context, REQUEST=request,
                                                 RESPONSE=response,
                                                 disposition='attachment')
        return response

    def set_filedata(self, filename):
        data = StringIO(100 * "dummy")
        setattr(data, 'filename', filename)
        self.context.setFile(data)

    def test_whitespace(self):
        response = self.get_response_for(filename='ein file.doc')
        self.assertEqual('attachment; filename="ein file.doc"; filename=ein file.doc*=UTF-8',
                         response.getHeader('Content-disposition'))

    def test_umlauts(self):
        response = self.get_response_for(
            filename='Gef\xc3\xa4hrliche Zeichen.doc')
        self.assertEqual(
            'attachment; filename="Gef\xc3\xa4hrliche Zeichen.doc"; filename=Gef\xc3\xa4hrliche Zeichen.doc*=UTF-8',
            response.getHeader('Content-disposition'))

    def test_unicode(self):
        response = self.get_response_for(filename=u'\xfcber.html')
        self.assertEqual(
            'attachment; filename="\xc3\xbcber.html"; filename=\xc3\xbcber.html*=UTF-8',
            response.getHeader('Content-disposition'))

    def test_msie(self):
        request = HTTPRequest('', dict(HTTP_HOST='nohost:8080',
                                       HTTP_USER_AGENT='MSIE'), {})
        response = self.get_response_for(filename=u'\xfcber.html',
                                         request=request)

        self.assertEqual('attachment; filename=\xc3\xbcber.html; filename*=UTF-8\'\'%C3%BCber.html',
                         response.getHeader('Content-disposition'))
        response = self.get_response_for(
            filename=u'\xfcber\xe2\x80\x93uns.html', request=request)
        self.assertEqual(
            'attachment; filename=\xc3\xbcber\xc3\xa2\xc2\x80\xc2\x93uns.html; filename*=UTF-8\'\'%C3%BCber%C3%A2%C2%80%C2%93uns.html',
            response.getHeader('Content-disposition'))

    def test_get_origin_filename_has_no_extension(self):
        self.set_filedata('dummyfile.txt')
        self.assertEqual('dummyfile', self.context.getOriginFilename())

    def test_set_origin_filename_overrides_the_filename_and_keeps_the_extension(self):
        self.set_filedata('dummyfile.txt')
        self.context.setOriginFilename(u'\xfcber')
        self.assertEqual('\xc3\xbcber.txt', self.context.getFilename())

    def test_set_origin_filename_does_not_override_filename_if_its_empty(self):
        self.set_filedata('dummyfile.txt')
        self.context.setOriginFilename('')
        self.assertEqual('dummyfile.txt', self.context.getFilename())

    def test_set_origin_filename_if_no_filename_exists(self):
        self.assertEqual(None, self.context.getFilename())
        self.context.setOriginFilename('testfile')
        self.assertEqual(None, self.context.getFilename())

    def test_get_origin_filename_if_no_filename_exists(self):
        self.assertEqual(None, self.context.getOriginFilename())

    def test_get_origin_filename_if_no_extension_exists(self):
        self.set_filedata('dummyfile')
        self.assertEqual('dummyfile', self.context.getOriginFilename())

    def test_set_origin_filename_if_no_extension_exists(self):
        self.set_filedata('dummyfile')
        self.context.setOriginFilename(u'\xfcber')
        self.assertEqual('\xc3\xbcber', self.context.getFilename())

    @browsing
    def test_origin_filename_is_set_if_no_file_is_uploaded(self, browser):
        existingfile = create(Builder('file').with_dummy_content()
                              .titled('The File'))
        browser.login().open(existingfile, view='edit')
        browser.fill({'Filename': 'newFilename'}).submit()
        self.assertEquals('newFilename.doc', existingfile.getFilename())

    @browsing
    def test_origin_filename_is_filename_of_uploaded_file(self, browser):
        existingfile = create(Builder('file').with_dummy_content())
        browser.login().open(existingfile, view='edit')
        browser.fill({
            'file_delete': '',
            'file_file': ('Raw file data', 'newfile.txt', 'text/plain')
        }).submit()
        self.assertEqual('newfile.txt', existingfile.getFilename())

    @browsing
    def test_origin_filename_cannot_contain_slash(self, browser):
        existingfile = create(Builder('file').with_dummy_content()
                              .titled('The File'))

        browser.login()

        # Set an origin filename without slash. This must work.
        browser.open(existingfile, view='edit')
        browser.fill({'Filename': 'Foobar'}).submit()
        statusmessages.assert_no_error_messages()
        self.assertEqual('Foobar.doc', existingfile.getFilename())

        # Set an origin filename containing a slash. This must fail.
        browser.open(existingfile, view='edit')
        browser.fill({'Filename': 'Foo / bar'}).submit()
        statusmessages.assert_message('Please correct the indicated errors.')
        self.assertEqual('Foobar.doc', existingfile.getFilename())
