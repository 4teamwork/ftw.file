from Products.CMFCore.utils import getToolByName
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase
import os
import transaction


class TestFileName(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.path = "%s/assets/testfile.NonsenseExtension" % (
            os.path.split(__file__)[0])
        self.file_ = open(self.path, 'r')
        self.mtr = getToolByName(self.portal, 'mimetypes_registry')

    @browsing
    def test_custom_icon(self, browser):
        # NB Plone includes all Python's 'mimetypes' in it's mimetypes_registry
        self.mtr.manage_addMimeType('customimage type',
                                    ['image/x-custom-image'],
                                    ['NonsenseExtension'],
                                    'customicon.png')
        transaction.commit()

        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')  # fortunately ftw.file.File is before File

        with open(self.path, 'r') as file_:
            browser.fill({'Title': 'My file',
                          'Filename': 'myfile',
                          'File': (file_.read(),
                                   'testfile.NonsenseExtension',
                                   'image/x-custom-image')
                          }).save()
        errors = browser.css('.error')
        self.assertEqual(0, len(errors), "Check no errors on form submission")

        plonefile = self.portal['myfile-nonsenseextension']
        self.assertEqual('plone/customicon.png', plonefile.getIcon())

    @browsing
    def test_default_icon(self, browser):
        self.mtr.manage_addMimeType('customimage type',
                                    ['image/x-custom-image'],
                                    ['NonsenseExtension'],
                                    '')
        transaction.commit()

        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')  # fortunately ftw.file.File is before File

        with open(self.path, 'r') as file_:
            browser.fill({'Title': 'My file',
                          'Filename': 'myfile',
                          'File': (file_.read(),
                                   'testfile.NonsenseExtension',
                                   'image/x-custom-image')
                          }).save()
        errors = browser.css('.error')
        self.assertEqual(0, len(errors), "Check no errors on form submission")

        plonefile = self.portal['myfile-nonsenseextension']
        self.assertEqual('plone/image.png', plonefile.getIcon())

    @browsing
    def test_icon_for_contenttype_not_found(self, browser):
        # To test the behavior of our function when a contenttype is not found
        # in mimetyperegistry we add a mimetype so everything is indexed and
        # created correctly.
        self.mtr.manage_addMimeType('customimage type',
                                    ['image/x-custom-image'],
                                    ['NonsenseExtension'],
                                    '')
        transaction.commit()

        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')  # fortunately ftw.file.File is before File

        with open(self.path, 'r') as file_:
            browser.fill({'Title': 'My file',
                          'Filename': 'myfile',
                          'File': (file_.read(),
                                   'testfile.NonsenseExtension',
                                   'image/x-custom-image')
                          }).save()
        errors = browser.css('.error')
        self.assertEqual(0, len(errors), "Check no errors on form submission")

        # and then we remove it again so we won't find it in the registry.
        self.mtr.manage_delObjects(['image/x-custom-image'])
        transaction.commit()

        plonefile = self.portal['myfile-nonsenseextension']
        self.assertEqual('plone/file_icon.png', plonefile.getIcon())
