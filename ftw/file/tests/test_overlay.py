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
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.context = create(Builder('file')
                              .titled(u'Some title')
                              .attach_asset(u'transparent.gif'))

    @browsing
    def test_image_displayed(self, browser):
        browser.login().visit(self.context)
        self.assertIn(
            '<a id="preview" class="colorboxLink"'
            ' href="{}/transparent.gif/@@images/file">'.format(self.portal_url),
            browser.contents)
        self.assertIn(
            '<img src="{}/transparent.gif/@@images'.format(self.portal_url),
            browser.contents)

    @browsing
    def test_image_link_works(self, browser):
        browser.login().open(self.context.absolute_url() + '/@@images/file')
        self.assertEqual('image/gif', browser.headers['content-type'])
