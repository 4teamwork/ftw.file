from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from unittest2 import TestCase
from ftw.builder import create
from ftw.builder import Builder
from ftw.testbrowser import browsing
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
import transaction


class TestFileName(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.file1 = create(Builder('file').titled("file1"))
        self.file2 = create(Builder('file').titled("file2"))

    @browsing
    def test_show_relateditems(self, browser):
        self.file1.Schema().get('relatedItems').set(self.file1,
                                                    self.file2.UID())
        transaction.commit()
        browser.login().open(self.file1.absolute_url())
        box = browser.css('#relatedItemBox a')
        self.assertEqual(['file2'], box.text)

    @browsing
    def test_show_referenced_by(self, browser):
        self.file1.Schema().get('relatedItems').set(self.file1,
                                                    self.file2.UID())
        transaction.commit()
        browser.login().open(self.file2.absolute_url())
        box = browser.css('#referencedByBox a')
        self.assertEqual(['file1'], box.text)

    @browsing
    def test_show_circular(self, browser):
        self.file1.Schema().get('relatedItems').set(self.file1,
                                                    self.file2.UID())
        self.file2.Schema().get('relatedItems').set(self.file2,
                                                    self.file1.UID())

        transaction.commit()
        browser.login().open(self.file2.absolute_url())
        ref_box = browser.css('#referencedByBox')
        self.assertEqual([], ref_box.text)
        rel_box = browser.css('#relatedItemBox a')
        self.assertEqual(['file1'], rel_box.text)
