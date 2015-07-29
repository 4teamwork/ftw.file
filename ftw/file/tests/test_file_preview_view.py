from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_BUMBLEBEE_INTEGRATION_TESTING
from ftw.testbrowser import browsing
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestFilePreview(TestCase):

    layer = FTW_FILE_BUMBLEBEE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.pr = getToolByName(self.portal, 'portal_repository')
        self.pr.setVersionableContentTypes('File')
        self.dummyfile = create(Builder('file').with_dummy_content())

    @browsing
    def test_journal_is_visible(self, browser):
        view = self.dummyfile.unrestrictedTraverse('@@file_preview')
        self.pr.save(self.dummyfile, comment="new Version")
        browser.open_html(view())

        self.assertTrue(
            browser.css('.journal'),
            'The journal-div is not visible, but it should.')

    @browsing
    def test_disable_journal(self, browser):
        view = self.dummyfile.unrestrictedTraverse('@@file_preview')
        self.pr.save(self.dummyfile, comment="new Version")
        browser.open_html(view(show_history=False))

        self.assertEqual(
            0, len(browser.css('.journal')),
            'The journal-div is visible, but it should not.')

    @browsing
    def test_show_user_id_of_deleted_user_in_journal(self, browser):
        # Create a new user
        api.user.create(
            email='chuck@norris.org',
            username='chuck',
            properties={'fullname': 'Chuck Norris'})
        setRoles(self.portal, 'chuck', ['Manager'])

        # create a content and a new version with the new user
        logout()
        login(self.portal, 'chuck')
        dummyfile = create(Builder('file').with_dummy_content())
        self.pr.save(dummyfile, comment="new Version")

        # login with testuser and delete chuck
        logout()
        login(self.portal, TEST_USER_NAME)
        api.user.delete(username='chuck')

        view = dummyfile.unrestrictedTraverse('@@file_preview')
        browser.open_html(view())

        self.assertIn(
            'chuck', browser.css('.journalItem').first.text,
            'The user-id should be visible in the journal item')

    @browsing
    def test_show_fullname_of_user_in_journal_if_exists(self, browser):
        # Create a new user
        api.user.create(
            email='chuck@norris.org',
            username='chuck',
            properties={'fullname': 'Chuck Norris'})
        setRoles(self.portal, 'chuck', ['Manager'])

        # create a content and a new version with the new user
        logout()
        login(self.portal, 'chuck')
        dummyfile = create(Builder('file').with_dummy_content())
        self.pr.save(dummyfile, comment="new Version")

        view = dummyfile.unrestrictedTraverse('@@file_preview')
        browser.open_html(view())

        self.assertIn(
            'Chuck Norris', browser.css('.journalItem').first.text,
            'The fullname should be visible in the journal item')

    @browsing
    def test_show_userid_in_journal_if_no_fullname_exists(self, browser):
        # Create a new user
        api.user.create(
            email='chuck@norris.org',
            username='chuck')
        setRoles(self.portal, 'chuck', ['Manager'])

        # create a content and a new version with the new user
        logout()
        login(self.portal, 'chuck')
        dummyfile = create(Builder('file').with_dummy_content())
        self.pr.save(dummyfile, comment="new Version")

        view = dummyfile.unrestrictedTraverse('@@file_preview')
        browser.open_html(view())

        self.assertIn(
            'chuck', browser.css('.journalItem').first.text,
            'The user-id should be visible in the journal item')

    @browsing
    def test_set_default_actions(self, browser):
        view = self.dummyfile.unrestrictedTraverse('@@file_preview')

        browser.open_html(view(actions_list=['edit', 'delete']))
        self.assertEqual(
            ['Edit File', 'Delete File'],
            [link.text for link in browser.css('.fileActions a')],
            'Only the edit and the delete buttons should be visible '
            'in the given order')

    @browsing
    def test_check_if_actions_are_listed_by_default(self, browser):
        view = self.dummyfile.unrestrictedTraverse('@@file_preview')

        browser.open_html(view())
        self.assertTrue(
            0 < len(browser.css('.fileActions a')),
            'Show some fileactions by default')

    @browsing
    def test_set_default_fileinfos(self, browser):
        self.dummyfile.setDescription('Chuck')
        view = self.dummyfile.unrestrictedTraverse('@@file_preview')

        browser.open_html(view(file_infos_list=['filename', 'description']))

        self.assertEqual(
            ['Filename: test.doc', 'Description: Chuck'],
            [container.text for container in browser.css('.detailItem')],
            'Only the filename and the description infos should be visible '
            'in the given order')

    @browsing
    def test_set_empty_default_title_gets_context_title(self, browser):
        view = self.dummyfile.unrestrictedTraverse('@@file_preview')

        browser.open_html(view(documentTitle=None))
        self.assertEqual(
            self.dummyfile.Title(),
            browser.css('.file-details h3').first.text,
            'The default title should be the title of the context')

    @browsing
    def test_set_default_title(self, browser):
        view = self.dummyfile.unrestrictedTraverse('@@file_preview')

        browser.open_html(view(documentTitle="This is the title"))
        self.assertEqual(
            "This is the title",
            browser.css('.file-details h3').first.text,
            'The default title should be overridden by the documentTitle')
