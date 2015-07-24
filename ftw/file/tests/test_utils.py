from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from ftw.file.utils import format_filesize
from ftw.file.utils import redirect_to_download_by_default
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest2 import TestCase


class TestFormatFilesize(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def test_byte_lowest(self):
        self.assertEqual(
            '0.0 B', format_filesize(0))

    def test_byte_heighest(self):
        self.assertEqual(
            '1024.0 B', format_filesize(1024**1-0.001))

    def test_kilobyte_lowest(self):
        self.assertEqual(
            '1.0 KB', format_filesize(1024**1))

    def test_kilobyte_heighest(self):
        self.assertEqual(
            '1024.0 KB', format_filesize(1024**2-0.001))

    def test_megabyte_lowest(self):
        self.assertEqual(
            '1.0 MB', format_filesize(1024**2))

    def test_megabyte_heighest(self):
        self.assertEqual(
            '1024.0 MB', format_filesize(1024**3-0.001))

    def test_gigabyte_lowest(self):
        self.assertEqual(
            '1.0 GB', format_filesize(1024**3))


class TestRedirectToDownloadByDefault(TestCase):

    layer = FTW_FILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_should_return_True_for_anonymous_users(self):
        login(self.portal, TEST_USER_NAME)
        obj = create(Builder('file'))
        logout()

        self.assertTrue(
            redirect_to_download_by_default(obj),
            'An anonymous user should be redirected to the downloads view.')

    def test_should_return_True_for_anonymous_users_with_forced_border(self):
        login(self.portal, TEST_USER_NAME)
        obj = create(Builder('file'))
        logout()

        obj.REQUEST.other['enable_border'] = True
        self.assertTrue(
            redirect_to_download_by_default(obj),
            'An anonymous user should be redirected to the downloads view, '
            'even when enable_border is True.')

        self.assertTrue(
            obj.REQUEST.get('enable_border'),
            'enable_border should not be removed from the request')

    def test_should_return_False_for_editors(self):
        login(self.portal, TEST_USER_NAME)
        obj = create(Builder('file'))
        setRoles(self.portal, TEST_USER_ID, ['Editor'])

        self.assertFalse(
            redirect_to_download_by_default(obj),
            'An editor should not be redirected to the downloads view.')

    def test_should_return_False_for_editors_in_previewish_mode(self):
        login(self.portal, TEST_USER_NAME)
        obj = create(Builder('file'))
        setRoles(self.portal, TEST_USER_ID, ['Editor'])

        obj.REQUEST.other['disable_border'] = True
        self.assertFalse(
            redirect_to_download_by_default(obj),
            'An editor should not be redirected to the downloads view, '
            'even when disable_border is True.')

        self.assertTrue(
            obj.REQUEST.get('disable_border'),
            'disable_border should not be removed from the request')
