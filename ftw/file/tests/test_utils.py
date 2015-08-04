from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING
from ftw.file.utils import FileMetadata
from ftw.file.utils import redirect_to_download_by_default
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


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


class FileMetadataBase(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())


class TestFileMetadataGetImageTag(FileMetadataBase):

    def test_return_none_if_no_image_exists(self):
        self.assertEqual(
            None,
            FileMetadata(self.dummyfile).get_image_tag(
                fieldname="file", width=1, direction="down"))

    def test_return_scale_if_available(self):
        img_file = create(Builder('file').attach_asset('transparent.gif'))
        self.assertTrue(
            FileMetadata(img_file).get_image_tag(
                fieldname="file", width=1, direction="down"),
            "Should return the scale for this image")

    def test_return_none_if_scale_is_not_available(self):
        img_file = create(Builder('file').attach_asset('CCITT_1.TIF'))
        self.assertEqual(
            None,
            FileMetadata(img_file).get_image_tag("file", 1, 'down'))


class TestFileMetadataCanEdit(FileMetadataBase):

    def test_can_edit_if_has_permission(self):
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(FileMetadata(self.dummyfile).can_edit)

    def test_cannot_edit_if_has_no_permission(self):
        logout()
        self.assertFalse(FileMetadata(self.dummyfile).can_edit)


class TestFileMetadataDocumentDate(FileMetadataBase):

    def test_return_document_date_if_exists(self):
        self.dummyfile.setDocumentDate(DateTime('10.05.2015 10:25'))
        self.assertEqual(
            u'Oct 05, 2015', FileMetadata(self.dummyfile).document_date)


class TestFileMetadataModifiedDate(FileMetadataBase):

    def test_return_modified_date_if_exists(self):
        self.dummyfile.setModificationDate(DateTime('10.05.2015 10:25'))
        self.assertEqual(
            u'Oct 05, 2015 10:25 AM',
            FileMetadata(self.dummyfile).modified_date)


class TestFileMetadataAuthor(FileMetadataBase):

    def test_return_fullname_and_url_if_exist_user_exist(self):
        api.user.create(
            email='chuck@norris.org',
            username='chuck',
            properties={'fullname': 'Chuck Norris'})

        self.dummyfile.setCreators(tuple(['chuck', ]))

        self.assertEqual(
            {'id': 'chuck',
             'name': 'Chuck Norris',
             'url': 'http://nohost/plone/author/chuck'},
            FileMetadata(self.dummyfile).author)

    def test_return_userid_and_url_if_user_exists_without_fullname(self):
        api.user.create(
            email='chuck@norris.org',
            username='chuck',
            properties={'fullname': ''})

        self.dummyfile.setCreators(tuple(['chuck', ]))

        self.assertEqual(
            {'id': 'chuck',
             'name': 'chuck',
             'url': 'http://nohost/plone/author/chuck'},
            FileMetadata(self.dummyfile).author)

    def test_return_userid_and_no_url_if_user_does_not_exist(self):
        self.dummyfile.setCreators(tuple(['chuck', ]))

        self.assertEqual(
            {'id': 'chuck',
             'name': 'chuck',
             'url': ''},
            FileMetadata(self.dummyfile).author)


class TestFileMetadataShowAuthor(FileMetadataBase):

    def test_true_if_logged_in_and_allow_AnonymousViewAbout_is_true(self):
        self._login(True)
        self._set_allowAnonymousViewAbout(True)

        self.assertTrue(
            FileMetadata(self.dummyfile).show_author,
            'Logged in user should see author if allowAnonymousViewAbout '
            'is True.')

    def test_true_if_anonymous_and_allow_AnonymousViewAbout_is_true(self):
        self._login(False)
        self._set_allowAnonymousViewAbout(True)

        self.assertTrue(
            FileMetadata(self.dummyfile).show_author,
            'Anonymous user user should see author if allowAnonymousViewAbout '
            'is True.')

    def test_true_if_logged_in_and_allow_AnonymousViewAbout_is_false(self):
        self._login(True)
        self._set_allowAnonymousViewAbout(False)

        self.assertTrue(
            FileMetadata(self.dummyfile).show_author,
            'Logged in user should see author if allowAnonymousViewAbout '
            'is False.')

    def test_false_if_anonymous_and_allow_AnonymousViewAbout_is_false(self):
        self._login(False)
        self._set_allowAnonymousViewAbout(False)

        self.assertFalse(
            FileMetadata(self.dummyfile).show_author,
            'Anonymous user should not see author if allowAnonymousViewAbout '
            'is False.')

    def _set_allowAnonymousViewAbout(self, value):
        site_props = getToolByName(
            self.portal, 'portal_properties').site_properties
        site_props.allowAnonymousViewAbout = value

    def _login(self, value):
        if value:
            login(self.portal, TEST_USER_NAME)
        else:
            logout()
