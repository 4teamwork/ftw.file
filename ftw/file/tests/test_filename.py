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

    def get_response_for(self, filename='foo.pdf', file_content=100*"dummy", response=HTTPResponse(),
                         request=None):
        if not request:
            request = HTTPRequest('', dict(HTTP_HOST='nohost:8080'), {}, response)
        data = StringIO(file_content)
        setattr(data, 'filename', filename)
        self.context.setFile(data)
        self.context.getField('file').index_html(self.context, REQUEST=request, RESPONSE=response)
        return response

    def test_whitespace(self):
        response = self.get_response_for(filename='ein file.doc')
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename="ein file.doc"')

    def test_umlauts(self):
        response = self.get_response_for(filename='Gef\xc3\xa4hrliche Zeichen.doc')
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename="Gef\xc3\xa4hrliche Zeichen.doc"')

    def test_unicode(self):
        response = self.get_response_for(filename=u'\xfcber.html')
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename="\xc3\xbcber.html"')

    def test_msie(self):
        request = HTTPRequest('', dict(HTTP_HOST='nohost:8080', HTTP_USER_AGENT='MSIE'), {})
        response = self.get_response_for(filename=u'\xfcber.html', request=request)
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename=%C3%BCber.html')
        response = self.get_response_for(filename=u'\xfcber\xe2\x80\x93uns.html', request=request)
        self.assertEqual(response.getHeader('Content-disposition'),
                         'attachment; filename=%C3%BCber%C3%A2%C2%80%C2%93uns.html')
