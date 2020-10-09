from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from unittest import TestCase
from zope.component import getMultiAdapter


class TestFileName(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('ftw.file.File', 'f1')
        self.context = self.portal.f1

        blob = NamedBlobFile(data=1234 * 'dummy',
                             filename=u'file.doc')
        self.context = create(Builder('file')
                              .having(file=blob))

    def get_response_for(self, filename='foo.pdf', request=None):
        if request is None:
            request = self.context.REQUEST
        self.set_filename(filename)
        view = getMultiAdapter((self.context, request), name='download')
        view()
        return view.request.response

    def set_filename(self, filename):
        if not isinstance(filename, unicode):
            filename = filename.decode('utf-8')
        self.context.file.filename = filename

    def test_whitespace(self):
        response = self.get_response_for(filename='ein file.doc')
        self.assertEqual('attachment; filename="ein file.doc"; filename*=UTF-8\'\'ein%20file.doc',
                         response.getHeader('Content-disposition'))

    def test_umlauts(self):
        response = self.get_response_for(filename='Gef\xc3\xa4hrliche Zeichen.doc')
        self.assertEqual(
            'attachment; filename="Gef\xc3\xa4hrliche Zeichen.doc"; filename*=UTF-8\'\'Gef%C3%A4hrliche%20Zeichen.doc',
            response.getHeader('Content-disposition'))

    def test_unicode(self):
        response = self.get_response_for(filename=u'\xfcber.html')
        self.assertEqual(
            'attachment; filename="\xc3\xbcber.html"; filename*=UTF-8\'\'%C3%BCber.html',
            response.getHeader('Content-disposition'))

    def test_get_filename_override_has_no_extension(self):
        self.set_filename('dummyfile.txt')
        self.assertEqual('dummyfile', self.context.filename_override)

    def test_set_filename_override_overrides_the_filename_and_keeps_the_extension(self):
        self.set_filename('dummyfile.txt')
        self.context.filename_override = u'\xfcber'
        self.assertEqual(u'\xfcber.txt', self.context.file.filename)

    def test_set_filename_override_does_not_override_filename_if_its_empty(self):
        self.set_filename('dummyfile.txt')
        self.context.filename_override = u''
        self.assertEqual('dummyfile.txt', self.context.file.filename)

    def test_set_filename_override_if_no_filename_exists(self):
        self.context.file.filename = None
        self.assertEqual(None, self.context.file.filename)
        self.context.filename_override = u'dummy'
        self.assertEqual(None, self.context.file.filename)

    def test_get_filename_override_if_no_filename_exists(self):
        self.context.file.filename = None
        self.assertEqual(None, self.context.filename_override)

    def test_get_filename_override_if_no_extension_exists(self):
        self.set_filename('dummyfile')
        self.assertEqual('dummyfile', self.context.filename_override)

    def test_set_filename_override_if_no_extension_exists(self):
        self.set_filename('dummyfile')
        self.context.filename_override = u'\xfcber'
        self.assertEqual(u'\xfcber', self.context.file.filename)

    @browsing
    def test_filename_override_is_set_if_no_file_is_uploaded(self, browser):
        existingfile = create(Builder('file').with_dummy_content()
                              .titled(u'The File'))
        browser.login().open(existingfile, view='edit')
        browser.fill({'Filename': u'newFilename'})
        browser.find_button_by_label(u'Save').click()
        self.assertEquals(u'newFilename.doc', existingfile.file.filename)

    @browsing
    def test_filename_override_is_filename_of_uploaded_file(self, browser):
        existingfile = create(Builder('file')
                              .titled(u'Some title')
                              .with_dummy_content())
        browser.login().open(existingfile, view='edit')
        browser.fill({
            'Replace with new file': True,
            'form.widgets.file': ('Raw file data', 'newfile.txt', 'text/plain')})
        browser.find_button_by_label(u'Save').click()
        self.assertEqual(u'newfile.txt', existingfile.file.filename)

    @browsing
    def test_filename_override_cannot_contain_slash(self, browser):
        existingfile = create(Builder('file').with_dummy_content()
                              .titled(u'The File'))

        browser.login()

        # Set an origin filename without slash. This must work.
        browser.visit(existingfile, view='edit')
        browser.fill({'Filename': u'Foobar'})
        browser.find_button_by_label(u'Save').click()
        statusmessages.assert_no_error_messages()
        self.assertEqual('Foobar.doc', existingfile.file.filename)

        # Set an origin filename containing a slash. This must fail.
        browser.visit(existingfile, view='edit')
        browser.fill({'Filename': u'Foo / bar'})
        browser.find_button_by_label(u'Save').click()
        statusmessages.assert_message('There were some errors.')
        self.assertEqual('Foobar.doc', existingfile.file.filename)
