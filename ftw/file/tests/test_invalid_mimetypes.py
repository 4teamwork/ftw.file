from ftw.builder import create, Builder
from ftw.file.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import Invalid
import os
import transaction


class TestInvalidMimeTypes(FunctionalTestCase):

    def setUp(self):
        super(TestInvalidMimeTypes, self).setUp()
        self.grant('Manager')

        self.registry = getUtility(IRegistry)

    def test_do_not_create_files_with_invalid_mimetype(self):
        obj = create(Builder('file')
                     .titled(u'Some title')
                     .attach_asset(u'test.pdf'))

        self.assertIn(obj.getId(), self.portal)

        self.registry['ftw.file.filesettings.invalid_mimeteypes'] = [u'application/pdf', ]
        with self.assertRaises(Invalid):
            create(Builder('file')
                   .titled(u'Some title')
                   .attach_asset(u'test.pdf'))

    @browsing
    def test_show_meaningful_message_on_form(self, browser):
        file_path = '{}/assets/test.pdf'.format(os.path.split(__file__)[0])

        browser.login().visit()
        factoriesmenu.add('File')
        with open(file_path, 'r') as file_:
            browser.fill({'Title': 'My file',
                          'Filename': 'myfile',
                          'File': (file_.read(),
                                   'test.pdf')
                          }).save()

        self.assertIn(browser.context.getId(), self.portal)

        self.registry['ftw.file.filesettings.invalid_mimeteypes'] = [u'application/pdf', ]
        transaction.commit()
        browser.login().visit()
        with open(file_path, 'r') as file_:
            factoriesmenu.add('File')
            browser.fill({'Title': 'My file',
                          'Filename': 'myfile',
                          'File': (file_.read(),
                                   'test.pdf')
                          }).save()
        self.assertEquals(
            u'Invalid mime type: application/pdf is not allowed',
            browser.css('.fieldErrorBox .error').first.text
        )
