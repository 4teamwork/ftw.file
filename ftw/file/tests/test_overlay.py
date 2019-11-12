from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import TestCase


class TestFileOverlay(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.context = create(Builder('file')
                              .titled(u'Some title')
                              .attach_asset(u'transparent.gif'))

    @browsing
    def test_image_displayed(self, browser):
        browser.login().visit(self.context)
        self.assertIn(
            '<a id="preview" class="colorboxLink"'
            ' href="http://nohost/plone/transparent.gif/@@images/file">',
            browser.contents)
        self.assertIn('<img src="http://nohost/plone/transparent.gif/@@images',
                      browser.contents)

    @browsing
    def test_image_link_works(self, browser):
        browser.login().open(self.context.absolute_url() + '/@@images/file')
        self.assertEqual('image/gif', browser.headers['content-type'])
