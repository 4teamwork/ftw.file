from ftw.activity.interfaces import IActivityRepresentation
from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from zope.component import getMultiAdapter
import os.path


class TestActivityRepresentation(TestCase):
    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Contributor'])

    @browsing
    def test_renders_preview_for_images(self, browser):
        file_ = create(
            Builder('file')
            .titled('An important file')
            .attach_file_containing(self.asset('transparent.gif'),
                                    'transparent.gif'))
        self.render_representation(browser, file_)
        self.assertEqual('An important file',
                         browser.css('.title').first.text)
        self.assertTrue(browser.css('.colorboxLink'))

    @browsing
    def test_renders_no_preview_for_files(self, browser):
        file_ = create(Builder('file')
                       .titled('An important file')
                       .with_dummy_content())
        self.render_representation(browser, file_)
        self.assertEqual('An important file',
                         browser.css('.title').first.text)
        self.assertFalse(browser.css('.colorboxLink'))

    def render_representation(self, browser, file_):
        repr = getMultiAdapter((file_, self.layer['request']),
                               IActivityRepresentation)
        self.assertTrue(repr.visible(),
                        'The activity representation is invisible.')
        html = repr.render()
        browser.open_html(html)

    def asset(self, filename):
        path = os.path.join(os.path.dirname(__file__),
                            'assets',
                            filename)
        with open(path, 'r') as fh:
            return fh.read()
