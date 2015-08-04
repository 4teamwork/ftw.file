from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestFilePreview(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.dummyfile = create(
            Builder('file').titled('Chuck Norris').with_dummy_content())

    @browsing
    def test_render_view(self, browser):
        browser.login().visit(self.dummyfile, view="file_preview")

        self.assertEqual(
            'Chuck Norris', browser.css('h3').first.text,
            "View isn't rendered correctly")


class TestFileView(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.dummyfile = create(
            Builder('file').titled('Chuck Norris').with_dummy_content())

    @browsing
    def test_render_view(self, browser):
        browser.login().visit(self.dummyfile, view="file_view")
        self.assertEqual(1, len(browser.css('.filePreview')))


class TestVersionPreview(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.pr = getToolByName(self.portal, 'portal_repository')
        self.pr.setVersionableContentTypes('File')

    @browsing
    def test_calling_view_loads_versioned_content(self, browser):
        dummyfile = create(
            Builder('file').titled('Ch\xc3\xa4ck Norris').with_dummy_content())
        self.pr.save(dummyfile, comment="init Version")

        dummyfile.setTitle('James Bond')
        self.pr.save(dummyfile, comment="Title changed")

        view = dummyfile.unrestrictedTraverse('@@file_preview')
        browser.open_html(view())

        # New Version
        self.assertEqual(
            'James Bond',
            browser.css('.fileDetails h3').first.text,
            'The title of the newes version should be visible')

        self.request['version_id'] = 0
        view = getMultiAdapter(
            (dummyfile, self.request), name="version_preview")

        browser.open_html(view())

        # Old Version
        self.assertEqual(
            u'Ch\xe4ck Norris - Version 1 of 2',
            browser.css('.fileDetails h3').first.text,
            'The title of the last version should be visible')
