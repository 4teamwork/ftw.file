from ftw.builder import Builder
from ftw.builder import create
from ftw.file.bumblebee.interfaces import IFilePreviewActionsCollector
from ftw.file.testing import FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.component import getMultiAdapter


class ActionsCollectorBaseTest(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.actions_tool = getToolByName(self.portal, 'portal_actions')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())
        self.view = self.dummyfile.unrestrictedTraverse('@@file_preview')
        self.adapter = getMultiAdapter(
            (self.dummyfile, self.request, self.view),
            IFilePreviewActionsCollector)


class TestDownloadOriginalAction(ActionsCollectorBaseTest):

    def test_download_original_action_url_is_correct(self):
        action = self.adapter._data_download_original()

        self.assertEqual(
            'http://nohost/plone/file/download', action.get('url'))


class TestDeleteAction(ActionsCollectorBaseTest):

    def test_delete_action_url_is_correct(self):
        action = self.adapter._data_delete()

        self.assertEqual(
            'http://nohost/plone/file/delete_confirmation', action.get('url'))

    def test_do_not_show_action_if_user_has_no_delete_permission(self):
        logout()
        action = self.adapter._data_delete()

        self.assertEqual({}, action)


class TestEditAction(ActionsCollectorBaseTest):

    def test_edit_action_url_is_correct(self):
        action = self.adapter._data_edit()

        self.assertEqual('http://nohost/plone/file/edit', action.get('url'))

    def test_do_not_show_action_if_user_has_no_edit_permission(self):
        logout()
        action = self.adapter._data_edit()

        self.assertEqual({}, action)


class TestOpenPdfAction(ActionsCollectorBaseTest):

    def test_do_not_display_action_if_document_is_already_a_pdf(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, self.request, view), IFilePreviewActionsCollector)

        action = adapter._data_open_pdf()

        self.assertEqual({}, action)

    def test_do_not_display_action_if_mimetype_is_not_supported(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.bad-mimetype'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, self.request, view), IFilePreviewActionsCollector)

        action = adapter._data_open_pdf()

        self.assertEqual({}, action)

    def test_if_the_mimetype_is_supported_it_will_create_an_action(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.doc'))
        view = dummyfile.unrestrictedTraverse('@@file_preview')
        adapter = getMultiAdapter(
            (dummyfile, self.request, view), IFilePreviewActionsCollector)

        action = adapter._data_open_pdf()

        self.assertIsNotNone(action.get('url', None))


class TestDownloadTisVersionAction(ActionsCollectorBaseTest):

    def test_download_this_version_url_is_correct(self):
        self.dummyfile.version_id = 20
        action = self.adapter._data_download_this_version()

        self.assertEqual(
            'http://nohost/plone/file/file_download_version?version_id=20',
            action.get('url'))


class TestGoToOriginalAction(ActionsCollectorBaseTest):

    def test_goto_original_url_is_correct(self):
        self.dummyfile.version_id = 20
        action = self.adapter._data_goto_original_file()

        self.assertEqual(
            'http://nohost/plone/file',
            action.get('url'))

    def test_do_not_show_action_if_user_has_no_edit_permission(self):
        logout()
        action = self.adapter._data_goto_original_file()

        self.assertEqual({}, action)


class TestExternalEdit(ActionsCollectorBaseTest):

    def test_do_not_show_action_if_user_has_no_edit_permission(self):
        action_extedit = self.actions_tool.document_actions.extedit

        action_extedit.visible = True

        action = self.adapter._data_external_edit()
        self.assertNotEqual(
            {}, action,
            "The action should be visible")

        logout()

        action = self.adapter._data_external_edit()

        self.assertEqual(
            {}, action,
            "The action should be invisible if the user has no permission")

    def test_do_not_show_action_if_extedit_action_is_not_visible(self):
        action_extedit = self.actions_tool.document_actions.extedit

        action_extedit.visible = True

        action = self.adapter._data_external_edit()
        self.assertNotEqual(
            {}, action,
            "THe action should be visible")

        action_extedit.visible = False

        action = self.adapter._data_external_edit()
        self.assertEqual(
            {}, action,
            "The action should be invisible if the visibility "
            "of the portal_action action is false")

    def test_externaledit_url_is_correct(self):
        action = self.adapter._data_external_edit()

        self.assertEqual(
            'http://nohost/plone/file/external_edit',
            action.get('url'))
