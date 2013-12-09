from StringIO import StringIO
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest2 import TestCase


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
                                                 RESPONSE=response)
        return response

    def set_filedata(self, filename):
        data = StringIO(100 * "dummy")
        setattr(data, 'filename', filename)
        self.context.setFile(data)

    def test_whitespace(self):
        response = self.get_response_for(filename='ein file.doc')
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename="ein file.doc"')

    def test_umlauts(self):
        response = self.get_response_for(
            filename='Gef\xc3\xa4hrliche Zeichen.doc')
        self.assertEqual(
            response.getHeader('Content-disposition'),
            'attachment; filename="Gef\xc3\xa4hrliche Zeichen.doc"')

    def test_unicode(self):
        response = self.get_response_for(filename=u'\xfcber.html')
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename="\xc3\xbcber.html"')

    def test_msie(self):
        request = HTTPRequest('', dict(HTTP_HOST='nohost:8080',
                                       HTTP_USER_AGENT='MSIE'), {})
        response = self.get_response_for(filename=u'\xfcber.html',
                                         request=request)
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename=%C3%BCber.html')
        response = self.get_response_for(
            filename=u'\xfcber\xe2\x80\x93uns.html', request=request)
        self.assertEqual(
            response.getHeader('Content-disposition'),
            'attachment; filename=%C3%BCber%C3%A2%C2%80%C2%93uns.html')

    def test_get_origin_filename_has_no_extension(self):
        self.set_filedata('dummyfile.txt')
        self.assertEqual('dummyfile', self.context.getOriginFilename())

    def test_set_origin_filename_overrides_the_filename(self):
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
